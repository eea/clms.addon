"""
Content rule string interpolator to return subscribed email address
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapter
from zope.interface import Interface

from clms.addon import _


@adapter(Interface)
class MeetingStart(BaseSubstitution):
    """Subscriber substitution adapter"""

    category = _(u"eea.meeting (clms.addon)")
    description = _(u"Meeting start date")

    def safe_call(self):
        """format the start date"""
        start = self.context.start.strftime("%d.%m.%Y")
        end = self.context.end.strftime("%d.%m.%Y")
        timezone = "Time zone: Copenhagen, Denmark"
        if start == end:
            return "{} {}".format(
                self.context.start.strftime("%b %d, %Y %H.%M"), timezone
            )
        return "{} - {} {}".format(
            self.context.start.strftime("%b %d, %Y %H.%M"),
            self.context.end.strftime("%b %d, %Y %H.%M"),
            timezone,
        )
