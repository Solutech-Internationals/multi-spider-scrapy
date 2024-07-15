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
        input_processor=MapCompose(remove_tags, remove_whitespace)
    )
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    modelYear = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    condition = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    transmission = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    manufacturer = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    model = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    fuelType = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    engineCapacity = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    mileage = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
    color = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )



process = CrawlerProcess(
    settings={
        "FEEDS": {
            "cars.json": {"format": "json"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEED_EXPORT_ENCODING": "utf-8",
        "ROBOTSTXT_OBEY": False,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

)


class Riyasewana(scrapy.Spider):
    name = "riyasewana"

    def parse_image_and_description(self, response):
        loader = response.meta['loader']
        image = response.css('figure.woocommerce-product-gallery__image a::attr(href)').extract()

        loader.add_value('image', image)
        yield loader.load_item()

    def start_requests(self):
        urls = [
            "https://riyasewana.com/search/cars/2018-2024/petrol/automatic/registered",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("li.item"):
            # # Check if the product is out of stock
            # if product.css("span.out-of-stock::text").get() == "Sold out":
            #     continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.more a::text")
            loader.add_css("price", "div.boxintxt.b::text")
            loader.add_value("url", product.css("h2.more a::attr(href)").get())
            loader.add_css("image", "div.imgbox a img::attr(src)")

            # Extracting the description from the list items within hover-content-inner
            description_items = product.css("div.boxintxt::text").getall()
            description = " | ".join(description_items)  # Join items with a separator for clarity
            loader.add_value("description", description)

            # item =  loader.load_item()

            inner_page = product.css('h2.more a::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image_and_description)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('div.pagination a:contains("Next")::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")

        pass


process.crawl(Riyasewana)
process.start()
