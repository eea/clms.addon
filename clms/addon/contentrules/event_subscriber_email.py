"""
Special string interpolator to catch the recipient email
from the session when allowing anonymous users to register
for an event
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapter
from zope.interface import Interface

from clms.addon import _


@adapter(Interface)
class EventSubscriberEmail(BaseSubstitution):
    """Subscriber substitution adapter"""

    category = _(u"eea.meeting (clms.addon)")
    description = _(
        u"Event subscriber email (only for anonymous registration cases)"
    )

    def safe_call(self):
        """format the start date"""
        sdm = getattr(self.context, "session_data_manager", None)
        session_data = sdm.getSessionData(create=False)
        return session_data.get("email", None)
