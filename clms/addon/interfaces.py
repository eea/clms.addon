"""Module where all interfaces, events and exceptions live."""

# from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.restapi.interfaces import IPloneRestapiLayer


# inheriting from IPloneRestapiLayer makes sure our services have higher specificity
class IClmsAddonLayer(IPloneRestapiLayer):
    """Marker interface that defines a browser layer."""
