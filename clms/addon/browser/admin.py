from Products.Five.browser import BrowserView
from plone import api


class GoPDB(BrowserView):
    def __call__(self):
        import pdb

        pdb.set_trace()


def find_items_containing_block(block_name):
    """Find items containing a block (form, grid, etc)"""
    SEARCH_WORD = block_name
    catalog = api.portal.get_tool("portal_catalog")

    results = []

    def search_in_blocks(blocks):
        if not isinstance(blocks, dict):
            return False

        for block_id, block_data in blocks.items():
            if SEARCH_WORD in block_data.get("@type", ""):
                return True

            nested_blocks = block_data.get("blocks", {})
            if search_in_blocks(nested_blocks):
                return True

        return False

    for brain in catalog():
        obj = brain.getObject()
        if hasattr(obj, "blocks") and search_in_blocks(obj.blocks):
            results.append(
                {
                    "title": obj.Title(),
                    "url": obj.absolute_url(),
                }
            )

    return results


class SearchForBlocksView(BrowserView):
    """ Usage: /api/search-for-blocks?block_name=grid """

    def __call__(self):
        block_name = self.request.form.get("block_name", "form")
        results = find_items_containing_block(block_name)
        if results:
            for result in results:
                print(f"Title: {result['title']}")
                print(f"URL: {result['url']}")
                print("-" * 20)
        else:
            print("No results found.")
            return "No results"

        return results
