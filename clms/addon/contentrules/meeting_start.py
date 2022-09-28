"""
Content rule string interpolator to return subscribed email address
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapter
from zope.interface import Interface

from clms.addon import _


@adapter(Interface)
class MeetingStart(BaseSubstitution):
    """ Subscriber substitution adapter"""

    category = _(u"eea.meeting (clms.addon)")
    description = _(u"Meeting start date")

    def safe_call(self):
        """ format the start date """
        return self.context.start.strftime('%d.%m.%Y %H:%M')
