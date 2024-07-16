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
    site = scrapy.Field(
        output_processor=TakeFirst()
    )


process = CrawlerProcess(
    settings={
        "FEEDS": {
            "bikes.json": {"format": "json"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEED_EXPORT_ENCODING": "utf-8",
        "ROBOTSTXT_OBEY": False,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

)

data = []
class Riyasewana(scrapy.Spider):

    name = "riyasewana"
    page_count = 0
    max_pages = 5

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

        item = loader.load_item()
        data.append(item)
        yield item

    def start_requests(self):
        urls = [
            "https://riyasewana.com/search/motorcycles",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("li.item"):

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.more a::text")

            price = product.css("div.boxintxt.b::text").get()

            if price:
                price = price.replace("Rs.", "").strip().replace("\r", "").replace(" ", "")
            loader.add_value("price", price)

            loader.add_value("url", product.css("h2.more a::attr(href)").get())
            loader.add_value('site', 'riyasewana.com')
            inner_page = product.css('h2.more a::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image_and_description)
                request.meta['loader'] = loader
                yield request
            else:
                item = loader.load_item()
                data.append(item)
                yield item

        next_page = response.css('div.pagination a:contains("Next")::attr(href)').get()
        if next_page and self.page_count < self.max_pages:
            self.page_count += 1
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found or maximum page limit reached.")

        pass


class PatPatLK(scrapy.Spider):
    name = "patpatlk"
    page_count = 0
    max_pages = 1

    def parse_image_and_description(self, response):
        loader = response.meta['loader']

        # Extract all image URLs from the div with class 'slick-track'
        image_urls = response.css('div.item-images a img::attr(data-src)').extract()
        loader.add_value('modelYear', response.css('td:contains("Model Year") + td::text').get())
        loader.add_value('condition', response.css('td:contains("Condition") + td::text').get())
        loader.add_value('transmission', response.css('td:contains("Transmission") + td::text').get())
        loader.add_value('manufacturer', response.css('td:contains("Manufacturer") + td::text').get())
        loader.add_value('model', response.css('table.course-info tr:nth-child(6) td:nth-child(2)::text').get())
        loader.add_value('engineCapacity', response.css('td:contains("Engine Capacity") + td::text').get())
        loader.add_value('mileage', response.css('td:contains("Mileage") + td::text').get())



        # Add unique image URLs to the loader
        loader.add_value('image', image_urls)

        yield loader.load_item()

    def start_requests(self):
        urls = [
            "https://www.patpat.lk/vehicle/filter/bike",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("div.result-item"):

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h4.result-title span::text")

            price = product.css("h3.clearfix label::text").get()
            if price:
                price = price.replace("Rs", "").strip().replace("\r", "").replace(" ", "")

            loader.add_value("price", price)
            loader.add_value("url", product.css("div.result-img a::attr(href)").get())

            loader.add_value('site', 'patpat.lk')

            inner_page = product.css('div.result-img a::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image_and_description)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('ul.pagination a[rel="next"]::attr(href)').get()

        if next_page and self.page_count < self.max_pages:
            self.page_count += 1
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")
        pass

class SaleMe(scrapy.Spider):

    name = "saleme"
    page_count = 0
    max_pages = 2

    def parse_image_and_description(self, response):
        loader = response.meta['loader']

        thumbnail_images = response.css("li.gallery-item a::attr(href)").extract()

        images = " | ".join(thumbnail_images)

        loader.add_value('modelYear', response.css('ul.spec-ul li:nth-child(3) span.spec-des::text').get())
        loader.add_value('condition', response.css('div.vap-details-tail:nth-child(1) div.vap-tail-desc '
                                                   'span.vap-tail-values::text').get())
        loader.add_value('manufacturer', response.css('ul.spec-ul li:nth-child(1) span.spec-des::text').get())
        loader.add_value('model', response.css('ul.spec-ul li:nth-child(2) span.spec-des::text').get())
        loader.add_value('engineCapacity', response.css('ul.spec-ul li:nth-child(4) span.spec-des::text').get())
        loader.add_value('mileage', response.css('div.vap-details-tail:nth-child(2) div.vap-tail-desc '
                                                 'span.vap-tail-values::text').get())
        loader.add_value('description', response.css('div.description-div p::text').get())

        # Add the images to the loader
        loader.add_value('image', images)

        yield loader.load_item()

    def start_requests(self):
        urls = [
            "https://www.saleme.lk/ads/sri-lanka/motorbikes-&-scooters",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("div.all-ads-cont > a"):
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h3.item-title::text")

            price = product.css("h4.item-price::text").get()
            if price:
                price = price.replace("RS", "").strip().replace("\r", "").replace(" ", "").replace(",", "")

            loader.add_value("price", price)
            loader.add_css("url", "a::attr(href)")
            loader.add_value('site', 'saleme.lk')

            inner_page = product.css("a::attr(href)").get()
            if inner_page:
                request = response.follow(inner_page, self.parse_image_and_description)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('ul.pager li a[rel="next"]::attr(href)').get()

        if next_page and self.page_count < self.max_pages:
            self.page_count += 1
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found or maximum page limit reached.")
        pass



class addToJson(scrapy.Spider):

    name = "addToJson"
    def startAdd(self):
        yield data

process.crawl(Riyasewana)
# process.crawl(PatPatLK)
# process.crawl(SaleMe)
process.crawl(addToJson)
process.start()