from typing import Tuple
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector


class PageMixin:
    @property
    def driver(self) -> webdriver.Chrome:
        chromedriver_path = (
            "./chromedriver/chromedriver/chromedriver"
        )
        service = Service(chromedriver_path)
        options = Options()
        options.add_argument("--headless")
        return webdriver.Chrome(service=service, options=options)

    def load_page(self, url: str) -> Tuple[webdriver.Chrome, WebDriverWait]:
        driver = self.driver
        driver.get(url)
        return driver, WebDriverWait(driver, 10)

    def scroll_to_bottom(self, loaded_page: webdriver.Chrome):
        last_height = loaded_page.execute_script("return document.body.scrollHeight")

        for _ in range(5):
            loaded_page.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)
            new_height = loaded_page.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        time.sleep(2)


class KiabiSeleniumManager(PageMixin):
    def __init__(self, max_click: int = 2):
        self._max_click = max_click

    def retrieve_items(
        self, url="https://www.kiabi.com/ado_430187"
    ) -> Tuple[Selector, webdriver.Chrome]:
        loaded_page, wait = self.load_page(url)

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "popin_tc_privacy_button"))
            ).click()

            wait.until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "ab_widget_container_popin-image_close_button")
                )
            ).click()

            self._view_more(loaded_page, wait)
            self.scroll_to_bottom(loaded_page)

            return self.to_scrapy_selector(loaded_page), loaded_page

        except Exception as e:
            print("Error:", e)
            return None, loaded_page

    def to_scrapy_selector(self, loaded_page: webdriver.Chrome) -> Selector:
        return Selector(text=loaded_page.page_source)

    def _view_more(self, loaded_page: webdriver.Chrome, wait: WebDriverWait):
        is_button = True
        n_click = 0
        while is_button and n_click < self._max_click:
            try:
                view_more = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[@data-testid='productList_button_showMore']",
                        )
                    )
                )
                loaded_page.execute_script("arguments[0].scrollIntoView();", view_more)
                view_more.click()

                time.sleep(2)
                n_click += 1
            except:
                is_button = False
