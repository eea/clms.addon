"""Module where all interfaces, events and exceptions live."""

# from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.restapi.interfaces import IPloneRestapiLayer
from eea.volto.policy.interfaces import IEeaVoltoPolicyLayer


# inheriting from IPloneRestapiLayer makes sure our services have higher specificity
# same for eea.volto.policy layer
class IClmsAddonLayer(IPloneRestapiLayer, IEeaVoltoPolicyLayer):
    """Marker interface that defines a browser layer."""
