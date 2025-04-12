from itemadapter import ItemAdapter
from ..utils import TextCleaner


class KiabyPipeline:
    def __init__(self):
        self.text_cleaner = TextCleaner()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.format_desc(adapter)
        self.extract_size(adapter)
        self.extract_origin(adapter)

        return item

    def format_desc(self, adapter: ItemAdapter):
        desc = adapter.get("description", "")
        adapter["description"] = self.text_cleaner.clean_text(desc)

    def extract_size(self, adapter: ItemAdapter):
        sizes = adapter.get("size", [])
        if len(sizes) > 0:
            adapter["size"] = [size.get("label") for size in sizes if size["label"]]

    def extract_origin(self, adapter: ItemAdapter):
        origins = adapter.get("provenance", [])
        if len(origins) > 0:
            provenance = []
            for o in origins:
                attrV = o.get("attributeValues", None)
                if attrV:
                    attrV = ", ".join(attrV)
                    provenance.append((o.get("attributeKey"), attrV))

            adapter["provenance"] = provenance
