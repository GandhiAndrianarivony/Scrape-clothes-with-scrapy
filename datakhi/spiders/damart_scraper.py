import json
import re
from urllib.parse import urljoin
from typing_extensions import TypedDict

import scrapy
from scrapy.http import Response

from ..items import DatakhiItem


class ProductAdditionalDetails(TypedDict):
    id: str
    color: str
    size: str
    composition: str
    price: str
    currency: str


class DamartScraperSpider(scrapy.Spider):
    name = "damart_product_scraper"
    allowed_domains = ["www.damart.fr"]
    start_urls = ["https://www.damart.fr/"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "datakhi.pipelines.damart_pipeline.DatakhiPipeline": 300,
            "datakhi.pipelines.damart_pipeline.DamartProductSerializer": 400,
        }
    }

    def start_requests(self):
        base_url = self.start_urls[0]
        path = [
            "c-286552-boutique",
            "c-295694-looks-de-ceremonie",
            "c-286913-pret-a-porter-homme"
            "c-208089-jours-eclairs"
            "c-286715-collection-homme",
            "c-277340-thermolactyl",
            "c-314282-sport",
            "c-178663-maison",
        ]
        for p in path:
            url = urljoin(base_url, p)
            yield scrapy.Request(url=url, callback=self.parse_collection)

    def parse_collection(self, response: Response):
        products = response.css("li.item.product.product-item")
        for product in products:
            product_item_info = product.css("div.product-item-info")

            product_url = product_item_info.css(
                "a.product-item-photo::attr(href)"
            ).get()

            if not product_url:
                continue

            product_details = {
                "name": product_item_info.css(
                    "h2.product.name.product-item-name a::text"
                ).get(),
                "url_image": product_item_info.css(
                    "a.product-item-photo img.product-image-photo::attr(src)"
                ).get(),
                "url": product_url,
            }

            yield response.follow(
                product_url,
                callback=self.parse_product_details,
                cb_kwargs={"product_details": product_details},
            )
        # TODO: next page
        next_page = response.css("a[class*='action'][class*='next']::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_collection)

    def parse_product_details(self, response: Response, product_details: dict):
        description = "\n".join(
            [
                selector.css("::text").get()
                for selector in response.css("div#product-info-detailed .value")
            ]
        )

        script_fields = response.css("div.product-add-form .fieldset script")
        additional_info = dict()
        for sf in script_fields:
            if "jsonConfig" in sf.get():
                additional_info = self.extract_additional_details(sf.get())

        datahi_item = {**{"description": description}, **product_details}
        datahi_item = {**datahi_item, **additional_info}

        yield DatakhiItem(**datahi_item)

    def extract_additional_details(
        self, script: str, *args, **kwargs
    ) -> ProductAdditionalDetails:
        output: ProductAdditionalDetails = {}
        if script:
            match = re.search(
                r'"jsonConfig"\s*:\s*({.*?})\s*,\s*\n\s*"jsonSwatchConfig"',
                script,
                re.DOTALL,
            )
            if match:
                json_config_str = match.group(1)

                # Fix escaped characters
                json_config_str = json_config_str.replace('\\"', '"')
                json_config_str = json_config_str.replace("\\/", "/")

                # Load into Python dictionary
                try:
                    json_config = json.loads(json_config_str)

                    for _, v in json_config["attributes"].items():
                        if v["label"] == "Couleur" and len(v["options"]) >= 1:
                            output["color"] = v["options"][0]["label"]

                        if v["label"] == "Taille" and len(v["options"]) >= 1:
                            output["size"] = [size["label"] for size in v["options"]]

                    output["id"] = json_config["productId"]

                    output["price"] = json_config["prices"]["basePrice"]["amount"]

                    if isinstance(json_config["composition"], dict):
                        output["composition"] = [
                            v for _, v in json_config["composition"].items()
                        ]
                    else:
                        output["composition"] = [
                            {"Composition principale": json_config["composition"]}
                        ]

                    output["currency"] = json_config["currencyFormat"]

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
        return output
