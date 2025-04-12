from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner, Crawler
from scrapy.utils.log import configure_logging
from scrapy import signals

from datakhi.spiders.damart_scraper import DamartScraperSpider
from datakhi.spiders.jules_scraper import JulesScraperSpider
from datakhi.spiders.kiabi_scraper import KiabiScraperSpider
from twisted.internet.defer import inlineCallbacks, gatherResults

scraped_data = []


def collect_results(item, spider):
    scraped_data.append(item)


@inlineCallbacks
def crawl_concurrently(runner: CrawlerRunner, spider_cls):
    crawler: Crawler = runner.create_crawler(spider_cls)
    crawler.signals.connect(collect_results, signal=signals.item_scraped)
    yield runner.crawl(crawler)


@inlineCallbacks
def run():
    configure_logging()
    runner = CrawlerRunner()

    # Run spiders with their own pipelines
    deferred_list = [
        crawl_concurrently(runner, DamartScraperSpider),
        crawl_concurrently(runner, JulesScraperSpider),
        crawl_concurrently(runner, KiabiScraperSpider),
    ]

    yield gatherResults(deferred_list)  # Wait for all spiders to finish
    yield runner.join()
    reactor.stop()


if __name__ == "__main__":
    import json

    run()
    reactor.run()
    with open("data.json", "w") as f:
        f.write(json.dumps(list(map(dict, scraped_data)), indent=4))
