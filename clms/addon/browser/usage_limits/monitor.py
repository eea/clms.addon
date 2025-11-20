"""Usage Limits Monitor.

A view to check API usage limits and send email alerts when thresholds are exceeded.
"""

import logging
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException

from chameleon import PageTemplateLoader
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema, ISiteSchema
from Products.Five import BrowserView
from zope.component import getUtility
from clms.addon.browser.cdse.utils import get_env_var
from clms.addon.browser.usage_limits.utils import get_usage
from clms.addon.browser.usage_limits.config import (
    USAGE_LIMITS_MONITOR_TOKEN_ENV_VAR, USAGE_LIMITS_EMAIL_TO_ENV_VAR
)

logger = logging.getLogger("clms.addon")
DEFAULT_THRESHOLD = 0.20


def get_usage_limits_monitor_token():
    """The token that protects the view"""
    if 'localhost' in api.portal.get().absolute_url():
        return "test-usage-limits"  # DEBUG

    return get_env_var(USAGE_LIMITS_MONITOR_TOKEN_ENV_VAR)


class UsageLimitsMonitor(BrowserView):
    """Monitor API usage limits and send email alerts"""

    def calculate_monthly_projection(
            self, metric_name, configuration, consumed, remaining):
        """Calculate monthly projection based on consumption rate

        Args:
            metric_name: Name of the metric
            configuration: Total monthly limit
            consumed: Amount consumed so far
            remaining: Amount remaining

        Returns:
            dict: Projection data including daily average, projected consumption, etc.
        """
        now = datetime.now()
        current_day = now.day
        # Get total days in current month
        import calendar
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        days_remaining = days_in_month - current_day

        # Calculate daily average consumption
        daily_average = consumed / current_day if current_day > 0 else 0

        # Project consumption until end of month
        projected_total_consumption = consumed + \
            (daily_average * days_remaining)

        # Will we run out?
        will_run_out = projected_total_consumption > configuration

        # Calculate when we might run out
        days_until_runout = None
        runout_date = None
        if will_run_out and daily_average > 0:
            days_until_runout = remaining / daily_average
            if days_until_runout >= 0:
                runout_date = current_day + int(days_until_runout)

        # Calculate overage amount if we'll run out
        projected_overage = max(0, projected_total_consumption - configuration)

        projection = {
            'current_day': current_day,
            'days_in_month': days_in_month,
            'days_remaining': days_remaining,
            'daily_average': daily_average,
            'projected_total_consumption': projected_total_consumption,
            'projected_overage': projected_overage,
            'will_run_out': will_run_out,
            'days_until_runout': days_until_runout,
            'runout_date': runout_date,
        }

        return projection

    def _parse_metric_data(self, monthly_data, overage_data, metric_name):
        """Parse and combine monthly + overage data for a metric

        Returns: dict with all calculated values
        """
        monthly_config = int(monthly_data.get('configuration', 0))
        monthly_consumed = int(monthly_data.get('consumed', 0))
        monthly_remaining = int(monthly_data.get('remaining', 0))

        overage_config = int(overage_data.get('configuration', 0))
        overage_remaining = int(overage_data.get('remaining', 0))

        total_config = monthly_config + overage_config
        total_remaining = monthly_remaining + overage_remaining

        return {
            'name': metric_name,
            'monthly': {
                'config': monthly_config,
                'consumed': monthly_consumed,
                'remaining': monthly_remaining,
            },
            'overage': {
                'config': overage_config,
                'remaining': overage_remaining,
            },
            'total': {
                'config': total_config,
                'remaining': total_remaining,
            }
        }

    def _check_metric_thresholds(self, metric_data,
                                 threshold_pct=DEFAULT_THRESHOLD):
        """Check if metric exceeds thresholds and generate alerts

        Args:
            metric_data: dict from _parse_metric_data()
            threshold_pct: threshold percentage (default 0.20 = 20%)

        Returns:
            list of alert dicts
        """
        alerts = []

        # Calculate thresholds
        total_threshold = metric_data['total']['config'] * threshold_pct
        monthly_threshold = metric_data['monthly']['config'] * threshold_pct

        # Calculate projection for monthly
        projection = None
        if metric_data['monthly']['config'] > 0:
            projection = self.calculate_monthly_projection(
                f"{metric_data['name']} Monthly",
                metric_data['monthly']['config'],
                metric_data['monthly']['consumed'],
                metric_data['monthly']['remaining']
            )

        # High Importance: Total (monthly + overage) < 20%
        if metric_data['total']['remaining'] < total_threshold:
            pct = (metric_data['total']['remaining'] / metric_data['total']
                   ['config'] * 100) if metric_data['total']['config'] > 0 else 0

            alerts.append({
                'severity': 'High Importance',
                'metric': f"{metric_data['name']} (TOTAL)",
                'message': f'Total remaining below {threshold_pct*100:.0f}% threshold ({pct:.1f}%)',
                'data': metric_data,
                'projection': projection
            })

        # Warning: Monthly only < 20%
        if metric_data['monthly']['remaining'] < monthly_threshold:
            pct = (metric_data['monthly']['remaining'] / metric_data['monthly']
                   ['config'] * 100) if metric_data['monthly']['config'] > 0 else 0

            alerts.append({
                'severity': 'Warning',
                'metric': f"{metric_data['name']} Monthly",
                'message': f'Monthly remaining below {threshold_pct*100:.0f}% threshold ({pct:.1f}%)',
                'data': metric_data,
                'projection': projection
            })

        return alerts, projection

    def check_usage_limits(self):
        print("Checking usage limits...")
        print("\n" + "="*60)

        all_alerts = []

        # Process Processing Units
        print("\n### PROCESSING UNITS ###")
        pu_data = self._parse_metric_data(
            self.usage.get('processingUnitsMonthly', {}),
            self.usage.get('processingUnitsOverage', {}),
            'Processing Units'
        )

        print(
            f"Monthly: {pu_data['monthly']['consumed']:,} / {pu_data['monthly']['config']:,} "
            f"(remaining: {pu_data['monthly']['remaining']:,})")
        print(
            f"Overage: {pu_data['overage']['remaining']:,} / {pu_data['overage']['config']:,}")
        print(
            f"TOTAL: {pu_data['total']['remaining']:,} / {pu_data['total']['config']:,}")

        pu_alerts, pu_projection = self._check_metric_thresholds(pu_data)
        all_alerts.extend(pu_alerts)

        for alert in pu_alerts:
            print(f"{alert['severity']}: {alert['message']}")

        if pu_projection and pu_projection['will_run_out']:
            print(
                f"PROJECTION: Will run out on day {pu_projection['runout_date']}")

        # Process Requests
        print("\n### REQUESTS ###")
        req_data = self._parse_metric_data(
            self.usage.get('requestsMonthly', {}),
            self.usage.get('requestsOverage', {}),
            'Requests'
        )

        print(
            f"Monthly: {req_data['monthly']['consumed']:,} / {req_data['monthly']['config']:,} "
            f"(remaining: {req_data['monthly']['remaining']:,})")
        print(
            f"Overage: {req_data['overage']['remaining']:,} / {req_data['overage']['config']:,}")
        print(
            f"TOTAL: {req_data['total']['remaining']:,} / {req_data['total']['config']:,}")

        req_alerts, req_projection = self._check_metric_thresholds(req_data)
        all_alerts.extend(req_alerts)

        for alert in req_alerts:
            print(f"{alert['severity']}: {alert['message']}")

        if req_projection and req_projection['will_run_out']:
            print(
                f"PROJECTION: Will run out on day {req_projection['runout_date']}")

        # Summary
        print("\n" + "="*60)
        print(f"\nSUMMARY: {len(all_alerts)} alert(s) found")
        for alert in all_alerts:
            print(
                f"  [{alert['severity']}] {alert['metric']}: {alert['message']}")

        print("\n" + "="*60)

        # Send consolidated email if there are alerts
        email_sent = False
        if all_alerts:
            email_sent = self._send_consolidated_email(all_alerts)
            if not email_sent:
                print(
                    "Note: Alerts detected but email not sent (check SMTP configuration)")

        return all_alerts  # Return alerts for further processing

    def _format_consolidated_email(self, all_alerts):
        """Format email using template - same pattern as post_subscribe.py

        Args:
            all_alerts: list of alert dicts

        Returns:
            str: HTML email body
        """
        # Separate by severity
        critical_alerts = [a for a in all_alerts
                           if a['severity'] == 'High Importance']
        warning_alerts = [a for a in all_alerts if a['severity'] == 'Warning']

        # Determine overall severity
        overall_severity = 'High Importance' if critical_alerts else 'Warning'

        # Get portal title
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix='plone', check=False)
        portal_title = site_settings.site_title

        path = os.path.dirname(__file__)
        templates = PageTemplateLoader(path)
        template = templates['usage_limits_alert_template.pt']

        return template(
            severity=overall_severity,
            alert_count=len(all_alerts),
            date=datetime.now().strftime('%B %d, %Y at %H:%M:%S UTC'),
            critical_alerts=critical_alerts,
            warning_alerts=warning_alerts,
            portal_title=portal_title,
        )

    def _send_consolidated_email(self, all_alerts):
        """Send a single consolidated email with all alerts

        Args:
            all_alerts: list of alert dicts

        Returns:
            bool: True if sent successfully
        """
        if not all_alerts:
            print("No alerts to send")
            return False

        # Count by severity
        critical_count = sum(1 for a in all_alerts
                             if a['severity'] == 'High Importance')
        warning_count = sum(1 for a in all_alerts
                            if a['severity'] == 'Warning')

        # Build subject line
        parts = []
        if critical_count > 0:
            parts.append(f"{critical_count} high importance")
        if warning_count > 0:
            parts.append(f"{warning_count} warning")

        severity = 'High Importance' if critical_count > 0 else 'Warning'
        subject = f"[{severity}] CDSE Usage Limit Alerts: {', '.join(parts)}"

        # Format email body
        html_body = self._format_consolidated_email(all_alerts)

        # Get email configuration from environment variable
        email_to = get_env_var(USAGE_LIMITS_EMAIL_TO_ENV_VAR)

        if not email_to:
            print(f"\n{'='*60}")
            print("EMAIL NOT SENT - No recipient configured")
            print(f"Set {USAGE_LIMITS_EMAIL_TO_ENV_VAR} environment variable")
            print(f"Subject: {subject}")
            print(f"Body length: {len(html_body)} chars")
            print(f"{'='*60}\n")
            return False

        # Send email using Plone's MailHost
        try:
            registry = getUtility(IRegistry)
            mail_settings = registry.forInterface(IMailSchema, prefix='plone')
            from_address = mail_settings.email_from_address
            from_name = mail_settings.email_from_name or 'Usage Monitor'
            source = '"{0}" <{1}>'.format(from_name, from_address)
            encoding = registry.get('plone.email_charset', 'utf-8')

            mailhost = api.portal.get_tool('MailHost')

            # Create multipart message
            message = MIMEMultipart('related')
            message['Subject'] = subject
            message['From'] = source
            message['Reply-To'] = from_address
            message.preamble = 'This is a multi-part message in MIME format'

            msg_alternative = MIMEMultipart('alternative')
            message.attach(msg_alternative)

            # Plain text alternative
            msg_txt = MIMEText(
                'This email requires HTML support to display properly.')
            msg_alternative.attach(msg_txt)

            # HTML content
            from Products.CMFPlone.utils import safe_text
            msg_html = MIMEText(safe_text(html_body), 'html')
            msg_alternative.attach(msg_html)

            # Send to each recipient (support comma-separated list)
            recipients = [email.strip() for email in email_to.split(',')]

            for recipient in recipients:
                try:
                    mailhost.send(
                        message.as_string(),
                        recipient,
                        source,
                        subject=subject,
                        charset=encoding,
                    )
                    logger.info(
                        f"Usage limit alert email sent to: {recipient}")
                    print(f"Email sent to: {recipient}")

                except (SMTPException, RuntimeError):
                    plone_utils = api.portal.get_tool('plone_utils')
                    exception = plone_utils.exceptionString()
                    message = "Unable to send mail: {exception}".format(
                        exception=exception
                    )
                    logger.error(message)
                    print(
                        f"Failed to send email to {recipient}: {exception}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to prepare email: {e}")
            print(f"Failed to prepare email: {e}")
            return False

    def __call__(self):
        """Handle HTTP request to this view"""
        # Token authentication
        monitor_token = get_usage_limits_monitor_token()

        if monitor_token is None:
            logger.info("Usage Limits Monitor Canceled: missing token ENV.")
            return "missing env var"

        view_token = self.request.form.get("token", None)
        if view_token is None:
            logger.info("Usage Limits Monitor Canceled: missing view token.")
            return "missing view token"

        if view_token != monitor_token:
            logger.info("Usage Limits Monitor Canceled: invalid token.")
            return "invalid token"

        # Token verified - proceed with monitoring
        self.usage = get_usage()
        alerts = self.check_usage_limits()

        # Preview mode - return HTML email without sending
        preview = self.request.form.get("preview", None)
        if preview:
            if alerts:
                html_body = self._format_consolidated_email(alerts)
                return html_body
            else:
                return "<html><body><p>No alerts - All metrics within thresholds</p></body></html>"

        # Return summary for HTTP response
        if alerts:
            critical_count = sum(
                1 for a in alerts if a['severity'] == 'High Importance')
            warning_count = sum(
                1 for a in alerts if a['severity'] == 'Warning')
            return f"OK: {len(alerts)} alerts found ({critical_count} high importance, {warning_count} warning)"
        else:
            return "OK: No alerts - All metrics within thresholds"
