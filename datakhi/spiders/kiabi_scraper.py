import json
from urllib.parse import urljoin
import scrapy
from scrapy.http import Response

from tqdm.auto import tqdm

from ..utils import save_json
from ..selenium import KiabiSeleniumManager
from ..items import DatakhiItem


class KiabiScraperSpider(scrapy.Spider):
    name = "kiabi"
    allowed_domains = ["www.kiabi.com"]
    start_urls = ["https://www.kiabi.com/"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "datakhi.pipelines.kiaby_pipeline.KiabyPipeline": 300,
        }
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.kiabi.com/",
    }

    def start_requests(self):
        base_url = self.start_urls[0]
        paths = [
            "femme_200005",
            "homme_200010",
            "fille_200015",
            "garcon_200020",
            "bebe_200025",
            "ado_430187",
            "puericulture_412323",
            "maison_200035",
        ]

        kiabi_manager = KiabiSeleniumManager(max_click=5)

        for path in paths:
            yield scrapy.Request(
                url=urljoin(base_url, path),
                callback=self.parse_collection_v2,
                headers=self.headers,
                cb_kwargs={"page_manager": kiabi_manager},
            )

    def parse_collection(self, response: Response, page_manager: KiabiSeleniumManager):
        selector, _ = page_manager.retrieve_items(response.url)
        products = selector.css("div.productCard_productCardContainer__1ssLc")[:1]
        progress_bar = tqdm(products, total=len(products), desc="Products", leave=True)

        for product in progress_bar:
            uri = product.css(
                'a[data-testid="productCard_div_linkImages"]::attr(href)'
            ).get()
            url = urljoin(self.start_urls[0], uri)
            image_src = (
                product.css("img::attr(src)").get()
                or product.css("img::attr(data-src)").get()
            )
            try:
                loaded_page, _ = page_manager.load_page(url)
                scrapy_selector = page_manager.to_scrapy_selector(loaded_page)

                for item in self.parse_product_details(
                    scrapy_selector=scrapy_selector,
                    product_details={"url_image": image_src, "url": url},
                ):
                    yield item

            except Exception as e:
                print(e)

            finally:
                loaded_page.close()

    def parse_collection_v2(
        self, response: Response, page_manager: KiabiSeleniumManager
    ):
        selector, _ = page_manager.retrieve_items(response.url)
        products = selector.css("div.productCard_productCardContainer__1ssLc")
        progress_bar = tqdm(products, total=len(products), desc="Products", leave=True)

        for product in progress_bar:
            uri = product.css(
                'a[data-testid="productCard_div_linkImages"]::attr(href)'
            ).get()
            url = urljoin(self.start_urls[0], uri)
            image_src = (
                product.css("img::attr(src)").get()
                or product.css("img::attr(data-src)").get()
            )

            yield response.follow(
                url,
                callback=self.parse_product_details,
                cb_kwargs={"product_details": {"url_image": image_src, "url": url}},
                headers=self.headers,
            )

    def parse_product_details(self, scrapy_selector: Response, product_details: dict):
        price = scrapy_selector.css(
            "span.productPrice_productPrice__11_pN span::text"
        ).get()

        name = scrapy_selector.css("h1[data-testid='text']::text").get()
        color = scrapy_selector.css(
            "div[data-testid='productColor_div_currentColorLabel'] :first-child::text"
        ).get()

        json_data = json.loads(scrapy_selector.css("script#__NEXT_DATA__::text").get())
        save_json(json_data, "product.json")

        id = json_data["props"]["pageProps"]["productUid"]
        composition = json_data["props"]["pageProps"]["queryResponse"]["product"][
            "composition"
        ]
        description = json_data["props"]["pageProps"]["queryResponse"]["product"][
            "productDescription"
        ]
        size = json_data["props"]["pageProps"]["queryResponse"]["product"]["display"][
            "price"
        ]["skus"]
        provenance = json_data["props"]["pageProps"]["queryResponse"]["product"][
            "origins"
        ]

        yield DatakhiItem(
            **{
                **{
                    "name": name,
                    "id": id,
                    "color": color,
                    "size": size,
                    "composition": composition,
                    "price": price,
                    "description": description,
                    "category": None,
                    "provenance": provenance,
                },
                **product_details,
            }
        )

