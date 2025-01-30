"""DXFields - override solution from eea.volto.policy in order to fix
our Folder case (of effective date issues)
"""

from plone.app.dexterity.behaviors.metadata import IPublication
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import IDatetime

from plone.app.contenttypes.interfaces import IFolder

from clms.addon.interfaces import IClmsAddonLayer

try:
    from eea.coremetadata.metadata import ICoreMetadata
except ImportError:
    # Fallback
    ICoreMetadata = IPublication


@adapter(IDatetime, IFolder, IClmsAddonLayer)
@implementer(IFieldSerializer)
class DateTimeFieldSerializer(DefaultFieldSerializer):
    """DateTimeFieldSerializer"""

    def get_value(self, default=None):
        """Get value"""
        value = getattr(
            self.field.interface(self.context), self.field.__name__, default
        )
        if value and self.field.interface in (
            IPublication,
            ICoreMetadata,
        ):
            # the patch: we want the dates with full tz infos
            # default value is taken from
            # plone.app.dexterity.behaviors.metadata.Publication that escape
            # timezone
            try:
                result = getattr(self.context, self.field.__name__)()
            except Exception:
                result = getattr(self.context, self.field.__name__)
            return result
        return value
