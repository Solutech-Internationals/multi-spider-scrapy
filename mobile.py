
import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
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


process = CrawlerProcess(
    settings={
        "FEEDS": {
            "mobiles.json": {"format": "json"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEED_EXPORT_ENCODING": "utf-8",
        "ROBOTSTXT_OBEY": False,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

)



class Celltronics(scrapy.Spider):

    name = "celltronics"

    def parse_image(self, response):
        loader = response.meta['loader']
        image = response.css('figure.woocommerce-product-gallery__image a::attr(href)').extract()

        loader.add_value('image', image)
        yield loader.load_item()

    def start_requests(self):
        urls = [
            "https://celltronics.lk/product-category/mobile-phones-price-in-sri-lanka/",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("div.product-wrapper"):
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h3.wd-entities-title a::text")
            loader.add_css("price", "span.woocommerce-Price-amount bdi::text")
            loader.add_value("url", product.css("h3.wd-entities-title a::attr(href)").get())
            # loader.add_css("image", "figure.woocommerce-product-gallery_image a::attr(href)")

            # Extracting the description from the list items within hover-content-inner
            description_items = product.css("div.hover-content-inner ul li::text").getall()
            description = " | ".join(description_items)  # Join items with a separator for clarity
            loader.add_value("description", description)

            # item =  loader.load_item()
            inner_page = product.css('a.product-image-link::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('a.next.page-numbers::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")
        pass


class LifeMobile(scrapy.Spider):

    name = "lifemobile"

    def parse_image_description(self, response):
        loader = response.meta['loader']
        stock = response.css('p.stock::text').get()
        # Skip item if out of stock
        if stock and 'Out of stock' in stock:
            return

        image = response.css('div.woocommerce-product-gallery__image a::attr(href)').extract()
        description_parts = response.css('div.woocommerce-Tabs-panel--specification table tr').extract()


        description = ' | '.join(description_parts)
        loader.add_value('description', description)
        loader.add_value('image', image)
        yield loader.load_item()

    def start_requests(self):
        urls = [
            "https://lifemobile.lk/product-category/mobile-phones/",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("li.product"):
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.woocommerce-loop-product__title")
            loader.add_css("price", "span.woocommerce-Price-amount bdi::text")
            loader.add_value("url", product.css("a.woocommerce-LoopProduct-link::attr(href)").get())
            # loader.add_css("image", "img.attachment-woocommerce_thumbnail::attr(src)")


            inner_page = product.css('a.woocommerce-LoopProduct-link::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image_description)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('a.next.page-numbers::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")
        pass

class XMobile(scrapy.Spider):

    name = "xmobile"

    def parse_image_description(self, response):
        loader = response.meta['loader']

        image = response.css('img.zoomImg::attr(src)').extract()
        description_parts = response.css('div.woocommerce-product-details__short-description ul li').extract()


        description = ' | '.join(description_parts)
        loader.add_value('description', description)
        loader.add_value('image', image)
        yield loader.load_item()

    def start_requests(self):
        urls = [
            "https://xmobile.lk/product-category/mobile-phones/",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("div.product-grid-item"):
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h3.wd-entities-title a::text")
            loader.add_css("price", "span.woocommerce-Price-amount bdi::text")
            loader.add_value("url", product.css("h3.wd-entities-title a::attr(href)").get())
            # loader.add_css("image", "img.attachment-woocommerce_thumbnail::attr(src)")


            inner_page = product.css('a.product-image-link::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image_description)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('a.next.page-numbers::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")
        pass


# process.crawl(Celltronics)
# process.crawl(LifeMobile)
# process.crawl(XMobile)
process.start()
