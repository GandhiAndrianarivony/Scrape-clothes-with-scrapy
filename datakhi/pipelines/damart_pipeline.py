# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class DamartProductSerializer:
    exclude_fields = ["currency"]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        for e in self.exclude_fields:
            adapter.pop(e, None)
        return item

class DatakhiPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.extract_product_id(adapter)
        self.format_product_name(adapter)
        self.format_price(adapter)
        self.extract_composition(adapter)

        return item

    def extract_product_id(self, adapter: ItemAdapter):
        adapter["id"] = adapter.get("id", "").replace("product-item-info_", "").strip()

    def format_product_name(self, adapter: ItemAdapter):
        adapter["name"] = adapter.get("name", "").strip()

    def format_price(self, adapter: ItemAdapter):
        currency = adapter.get("currency", "").replace("%s\xa0", " ").strip()
        adapter["price"] = f"{adapter.get('price', '')} {currency}"

    def extract_composition(self, adapter: ItemAdapter):
        if len(adapter.get("composition", [])) > 0:
            comps = ""
            for k, v in adapter.get("composition")[0].items():
                comps += f"{k}: {v}\n"

            adapter["composition"] = comps
