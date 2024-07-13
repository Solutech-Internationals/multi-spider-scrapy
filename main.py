
import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from itemloaders.processors import  MapCompose, TakeFirst
from w3lib.html import remove_tags

def remove_whitespace(value):
    return value.strip().replace("\n", "")

class ProductItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    image = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )

class LaptopLK(scrapy.Spider):
    name = "laptoplk"
    def start_requests(self) :
        urls = [
            "https://www.laptop.lk/?s=&product_cat=laptops&post_type=product",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("li.product"):
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.woocommerce-loop-product__title")
            loader.add_css("price", "span.woocommerce-Price-amount")
            loader.add_value("url", product.css("a.woocommerce-LoopProduct-link::attr(href)").get())
            loader.add_css("image", "img.attachment-woocommerce_thumbnail::attr(src)")
            loader.add_css("description", "div.product-short-description")
            yield loader.load_item()

        next_page = response.css('a.next.page-numbers::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")
        pass



# class RedlineTech(scrapy.Spider):
#     pass
#
# class ChamaComputers(scrapy.Spider):
#     pass
#
# class NanoTek(scrapy.Spider):
#     pass


process = CrawlerProcess(
    settings={
        "FEEDS": {
            "items.json": {"format": "json"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEED_EXPORT_ENCODING": "utf-8",
        "ROBOTSTXT_OBEY": False,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }
)

process.crawl(LaptopLK)
# process.crawl(RedlineTech)
# process.crawl(ChamaComputers)
# process.crawl(NanoTek)
process.start()