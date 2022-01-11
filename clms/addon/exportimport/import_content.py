""" export_content view override"""
# -*- coding: utf-8 -*-

from collective.exportimport.import_content import ImportContent as Base


class ImportContent(Base):
    """custom class for importing content. We need a custom importer
    to override object ids and thus the way to calculate the parent object

    In production the site is at https://domain.com/api/XXXX and in development
    the site is at http://localhost:8080/Plone/XXXX, so we need to change those
    /api/ to /Plone/ or viceversa.
    """

    def global_dict_hook(self, item):
        """override the path of the object to be aligned with the prodction
        or devel settings
        """
        url = self.context.absolute_url()
        url_parts = url.split("/")
        if "api" in url_parts:
            # we are importing in production, so we need
            # to change 'Plone' with 'api'
            old_path = item.get("@id")
            old_path_parts = old_path.split("/")
            if "Plone" in old_path_parts:
                old_path_parts[old_path_parts.index("Plone")] = "api"
                new_path = "/".join(old_path_parts)
                item["@id"] = new_path
        elif "Plone" in url_parts:
            # we are importing in development, so we need
            # to change 'api' with 'Plone'
            old_path = item.get("@id")
            if "api" in old_path:
                old_path_parts = old_path.split("/")
                old_path_parts[old_path_parts.index("api")] = "Plone"
                new_path = "/".join(old_path_parts)
                item["@id"] = new_path

        # in all other cases, leave this as is it
        return item
