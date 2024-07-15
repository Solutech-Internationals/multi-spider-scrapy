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
    page_count = 0
    max_pages = 100

    description_mapping = {
        "yom": "modelYear",
        "make": "manufacturer",
        "model": "model",
        "gear": "transmission",
        "fuel type": "fuelType",
        "engine (cc)": "engineCapacity",
        "mileage (km)": "mileage",
    }

    def parse_image_and_description(self, response):
        global description_text
        loader = response.meta['loader']
        # Extract all image URLs from the slider
        # main_image_url = response.css("#main-image-url::attr(href)").extract()
        thumbnail_images = response.css("div.thumb a::attr(href)").getall()

        images = " | ".join(thumbnail_images)

        # Extracting the description fields from the table
        description = []
        rows = response.css("table.moret tr")
        for row in rows:
            tds = row.css("td")
            if len(tds) == 4:
                header1 = tds[0].css("p.moreh::text").get()
                value1 = tds[1].css("::text").get()
                header2 = tds[2].css("p.moreh::text").get()
                value2 = tds[3].css("::text").get()

                if header1 and value1:
                    field_name = self.description_mapping.get(header1.strip().lower())
                    if field_name:
                        loader.add_value(field_name, value1.strip())
                    description.append(f"{header1.strip()}: {value1.strip()}")
                if header2 and value2:
                    field_name = self.description_mapping.get(header2.strip().lower())
                    if field_name:
                        loader.add_value(field_name, value2.strip())
                    description.append(f"{header2.strip()}: {value2.strip()}")

            description_text = " | ".join(description)


        # Add the images to the loader
        loader.add_value('image', images)

        # Extracting the description fields from the table
        loader.add_value("description", description_text)

        yield loader.load_item()

    def start_requests(self):
        urls = [
            "https://riyasewana.com/search/cars",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("li.item"):

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.more a::text")
            loader.add_css("price", "div.boxintxt.b::text")
            loader.add_value("url", product.css("h2.more a::attr(href)").get())

            inner_page = product.css('h2.more a::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image_and_description)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('div.pagination a:contains("Next")::attr(href)').get()
        if next_page and self.page_count < self.max_pages:
            self.page_count += 1
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found or maximum page limit reached.")

        pass



process.crawl(Riyasewana)
process.start()