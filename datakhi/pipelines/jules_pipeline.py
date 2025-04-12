from itemadapter import ItemAdapter


class JulesPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.get_color(adapter)
        self.get_description(adapter)
        self.format_size(adapter)

        return item

    def get_color(self, adapter: ItemAdapter):
        color = adapter.get("color", [])
        if color:
            adapter["color"] = " ".join([c.strip() for c in color if c.strip() != ""])

    def get_description(self, adapter: ItemAdapter):
        description = adapter.get("description", [])
        if description:
            adapter["description"] = "\n".join(
                [
                    d.strip()
                    for d in description
                    if d.strip() not in ("", "Voir plus", "Voir moins")
                ]
            )
    
    def format_size(self, adapter: ItemAdapter):
        size = adapter.get("size", [])
        if size:
            adapter["size"] = [s.strip() for s in size if s.strip() != ""]
