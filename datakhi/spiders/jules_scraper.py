from urllib.parse import urljoin
import scrapy
from scrapy.http import Response

from ..items import DatakhiItem


class JulesScraperSpider(scrapy.Spider):
    name = "jules_scraper"
    allowed_domains = ["www.jules.com"]
    start_urls = ["https://www.jules.com/"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "datakhi.pipelines.jules_pipeline.JulesPipeline": 300,
        }
    }
    ITEMS_PER_PAGE = 24

    def start_requests(self):
        base_url = self.start_urls[0]
        path = [
            "fr-fr/l/nouveautes/",
            "fr-fr/l/jeans/",
            "fr-fr/l/costumes/",
            "fr-fr/l/sous-vetements/",
            "fr-fr/l/accessoires/",
            "fr-fr/l/collection-mariage/",
        ]
        for p in path:
            url = urljoin(base_url, p)
            yield scrapy.Request(url=url, callback=self.parse_collection)

    def parse_collection(self, response: Response):
        total_pages = response.css(
            "div.ocs-text[data-productcount]::attr(data-productcount)"
        ).get()

        if total_pages is not None and "sz" not in response.url:
            total_pages = int(total_pages) + self.ITEMS_PER_PAGE
            yield response.follow(
                url=f"{response.url}?sz={total_pages}", callback=self.parse_collection
            )

        else:
            products = response.css("div.lineproduct")
            for product in products:
                img_scr = product.css("div.carousel-item.active img::attr(src)").get()

                uri = product.css("a.container-img_plp::attr(href)").get()
                url = urljoin(
                    response.url, uri
                )
                name =  product.css(".link.pdp-title-link::text").get()

                yield response.follow(
                    url,
                    callback=self.parse_product_details,
                    cb_kwargs={"product_details": {"url_image": img_scr, "url": url, "name": name}},
                )

    def parse_product_details(self, response: Response, product_details: dict):
        product_id = response.css(
            "div#sizeRecommander fitle-size-recommender[productid]::attr(productid)"
        ).get()
        price = response.css("div.ocs-price span.price::text").get()
        product_category = response.css("h1.product-name::text").get()

        description = response.xpath(
            '//div[@class="product-description"]//text()'
        ).getall()
        color = response.css('div[data-attr="color"] span#js-color-name::text').getall()
        composition = response.xpath(
            "//div[@class='product-composition' and not(*)]/text()"
        ).get()

        size_btn = response.css(
            'div[data-attr="size"] button.ocs-button span.label.selectable.size-choose'
        )
        sizes = []
        for btn in size_btn:
            sizes.append(btn.css("::text").get())

        product_details = {
            **product_details,
            "id": product_id,
            "price": price,
            "category": product_category,
            "color": color,
            "composition": composition,
            "size": sizes,
            "description": description,
        }

        yield DatakhiItem(**product_details)
