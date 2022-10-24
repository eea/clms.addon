""" Adapters """
from plone.stringinterp.adapters import BaseSubstitution
from eea.meeting import _
from eea.meeting.interfaces import IMeeting
from plone import api


class SetMeetingURL(BaseSubstitution):
    """Meeting URL"""

    category = _("eea.meeting")
    description = _("Finds the closest meeting and returns it's URL.")

    def safe_call(self):
        """Safe call"""

        def find_meeting(context):
            """return related meeting"""
            return (
                context
                if IMeeting.providedBy(context)
                else find_meeting(context.aq_parent)
            )

        meeting = find_meeting(self.context)
        return self.volto_url(meeting.absolute_url()) if meeting else ""

    def volto_url(self, value):
        """do the required substitutions to replace the url with Volto's"""
        plone_domain = api.portal.get().absolute_url()
        frontend_domain = api.portal.get_registry_record(
            "volto.frontend_domain"
        )
        if frontend_domain.endswith("/"):
            frontend_domain = frontend_domain[:-1]

        return value.replace(plone_domain, frontend_domain)
