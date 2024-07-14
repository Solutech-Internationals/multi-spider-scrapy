
import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from itemloaders.processors import  MapCompose, TakeFirst
from w3lib.html import remove_tags
from ai_extract import extractDescriptionAi

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
    ram = scrapy.Field(
        output_processor=TakeFirst()
    )
    gpu = scrapy.Field(
        output_processor=TakeFirst()
    )
    processor = scrapy.Field(
        output_processor=TakeFirst()
    )
    storage = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_students = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_students_reason = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_developers = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_developers_reason = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_video_editors = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_video_editors_reason = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_gaming = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_gaming_reason = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_business = scrapy.Field(
        output_processor=TakeFirst()
    )
    good_for_business_reason = scrapy.Field(
        output_processor=TakeFirst()
    )


class LaptopLK(scrapy.Spider):

    def parse_description(self, response):
        loader = response.meta['loader']
        descs = response.css('div#tab-specification p::text').extract()

        description = ' | '.join(descs)

        loader.add_value('description', description)
        yield loader.load_item()

    name = "laptoplk"
    def start_requests(self) :
        urls = [
            "https://www.laptop.lk/?s=&product_cat=laptops&post_type=product",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("li.product"):
            # Check if the product is out of stock
            if product.css("span.wcsob_soldout::text").get() == "Out Of Stock":
                continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.woocommerce-loop-product__title")
            loader.add_css("price", "span.woocommerce-Price-amount bdi::text")
            loader.add_value("url", product.css("a.woocommerce-LoopProduct-link::attr(href)").get())
            loader.add_css("image", "img.attachment-woocommerce_thumbnail::attr(src)")

            inner_page = product.css('a.woocommerce-LoopProduct-link::attr(href)').get()

            if inner_page:
                request = response.follow(inner_page, self.parse_description)
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

# ///////////////////////////

class Abans(scrapy.Spider):
    name = "abans"
    def start_requests(self):
        urls = [
            "https://buyabans.com/computers/laptops",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):
        for product in response.css("li.product-item"):

            # Check if the product is out of stock
            if product.css("div.stock span::text").get() == "Out of stock":
                continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "a.product-item-link::text")
            loader.add_css("price", "span.price::text")
            loader.add_value("url", product.css("a.product-item-link::attr(href)").get())
            loader.add_css("image", "img.product-image-photo::attr(src)")

            item = loader.load_item()  # Load the item
            raw_price = item.get("price")  # Access the 'title' field from the loaded item
            price = clean_price(raw_price)
            loader.replace_value("price", price)
            inner_page = product.css('a.product-item-photo::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_description)
                request.meta['loader'] = loader
                yield request
            else:
                yield loader.load_item()

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")

    def parse_description(self, response):
        loader = response.meta['loader']
        description_parts = response.css('div.value table tr').extract()
        description = ' | '.join(description_parts)
        loader.add_value('description', description)

        extracted_content = extractDescriptionAi(description)

        loader.add_value('ram', extracted_content['ram'])
        loader.add_value('gpu', extracted_content['gpu'])
        loader.add_value('processor', extracted_content['processor'])
        loader.add_value('storage', extracted_content['storage'])
        loader.add_value('good_for_students', extracted_content['good_for_students']['is_suitable'])
        loader.add_value('good_for_students_reason', extracted_content['good_for_students']['reason'])
        loader.add_value('good_for_developers', extracted_content['good_for_developers']['is_suitable'])
        loader.add_value('good_for_developers_reason', extracted_content['good_for_developers']['reason'])
        loader.add_value('good_for_video_editors', extracted_content['good_for_video_editors']['is_suitable'])
        loader.add_value('good_for_video_editors_reason', extracted_content['good_for_video_editors']['reason'])
        loader.add_value('good_for_gaming', extracted_content['good_for_gaming']['is_suitable'])
        loader.add_value('good_for_gaming_reason', extracted_content['good_for_gaming']['reason'])
        loader.add_value('good_for_business', extracted_content['good_for_business']['is_suitable'])
        loader.add_value('good_for_business_reason', extracted_content['good_for_business']['reason'])

        yield loader.load_item()


class NanoTek(scrapy.Spider):
    name = "nanotek"
    def start_requests(self) :
        urls = [
            "https://www.nanotek.lk/category/laptops",
        ]
        for url in urls:
            yield Request(url, self.parse_items_link)

    def parse_items_link(self, response):
        for product_item in response.css('li.ty-catPage-productListItem'):
            link = product_item.css('a::attr(href)').get()
            if link:
                yield response.follow(link, self.parse_items)

        next_page = response.css('li a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_items_link)

    def parse_items(self, response):

        if response.css("span.ty-special-msg::text").get() == "Out of Stock":
            return

        loader = ItemLoader(item=ProductItem(), response=response)
        loader.add_css('title', 'h1.ty-productTitle::text')
        loader.add_css('price', 'span.ty-price-now::text')
        loader.add_value("url", response.url)
        loader.add_css('image', 'div.ty-productPage-content-imgHolder img::attr(src)')
        description = response.css('div.ty-productPage-info').extract_first()
        loader.add_value('description', description.replace('\r', ''))

        extracted_content = extractDescriptionAi(description)

        loader.add_value('ram', extracted_content['ram'])
        loader.add_value('gpu', extracted_content['gpu'])
        loader.add_value('processor', extracted_content['processor'])
        loader.add_value('storage', extracted_content['storage'])
        loader.add_value('good_for_students', extracted_content['good_for_students']['is_suitable'])
        loader.add_value('good_for_students_reason', extracted_content['good_for_students']['reason'])
        loader.add_value('good_for_developers', extracted_content['good_for_developers']['is_suitable'])
        loader.add_value('good_for_developers_reason', extracted_content['good_for_developers']['reason'])
        loader.add_value('good_for_video_editors', extracted_content['good_for_video_editors']['is_suitable'])
        loader.add_value('good_for_video_editors_reason', extracted_content['good_for_video_editors']['reason'])
        loader.add_value('good_for_gaming', extracted_content['good_for_gaming']['is_suitable'])
        loader.add_value('good_for_gaming_reason', extracted_content['good_for_gaming']['reason'])
        loader.add_value('good_for_business', extracted_content['good_for_business']['is_suitable'])
        loader.add_value('good_for_business_reason', extracted_content['good_for_business']['reason'])

        yield loader.load_item()

class RedTech(scrapy.Spider):

    name = "redtech"

    def start_requests(self):
        urls = [
            "https://redtech.lk/product-category/laptops-notebooks/",
        ]
        for url in urls:
            yield Request(url=url, callback=self.parse_items)

    def parse_items(self, response):

        for product in response.css("li.product"):

            if product.css("b.br-labels-css::text").get() == "Out of Stock":
                continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.woocommerce-loop-product__title")
            loader.add_css("price", "span.woocommerce-Price-amount bdi::text")
            loader.add_value("url", product.css("a.woocommerce-LoopProduct-link::attr(href)").get())
            loader.add_css("image", "div.product-thumbnail img::attr(data-src)")
            description = response.css("div.product-short-description").extract_first()
            loader.add_value("description", description)


            extracted_content = extractDescriptionAi(description)

            loader.add_value('ram', extracted_content['ram'])
            loader.add_value('gpu', extracted_content['gpu'])
            loader.add_value('processor', extracted_content['processor'])
            loader.add_value('storage', extracted_content['storage'])
            loader.add_value('good_for_students', extracted_content['good_for_students']['is_suitable'])
            loader.add_value('good_for_students_reason', extracted_content['good_for_students']['reason'])
            loader.add_value('good_for_developers', extracted_content['good_for_developers']['is_suitable'])
            loader.add_value('good_for_developers_reason', extracted_content['good_for_developers']['reason'])
            loader.add_value('good_for_video_editors', extracted_content['good_for_video_editors']['is_suitable'])
            loader.add_value('good_for_video_editors_reason', extracted_content['good_for_video_editors']['reason'])
            loader.add_value('good_for_gaming', extracted_content['good_for_gaming']['is_suitable'])
            loader.add_value('good_for_gaming_reason', extracted_content['good_for_gaming']['reason'])
            loader.add_value('good_for_business', extracted_content['good_for_business']['is_suitable'])
            loader.add_value('good_for_business_reason', extracted_content['good_for_business']['reason'])

            item = loader.load_item()  # Load the item
            raw_title = item.get("title")  # Access the 'title' field from the loaded item
            self.logger.info(f"Raw Title: {raw_title}")

            cleaned_title, description = clean_title_and_description_alternative(raw_title)
            loader.replace_value("title", cleaned_title)
            loader.replace_value("description", description)

            item = loader.load_item()

            yield item

        next_page = response.css('a.page-numbers::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_items)
        else:
            self.logger.info("No next page found.")
    pass
def clean_title_and_description_alternative(raw_title):
    if raw_title is None:
        return None, None

    phrase = "– Order Now! – "

    raw_title = raw_title.replace(phrase, "")

    # Example cleaning process
    cleaned_title = raw_title.strip()
    description = cleaned_title

    return cleaned_title,description

def clean_price(raw_price):
    if raw_price is None:
        return None

    cleaned_price = raw_price.replace("Rs.", "").replace(",", "").strip()
    return cleaned_price

process = CrawlerProcess(
    settings={
        "FEEDS": {
            "laptops.json": {"format": "json"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEED_EXPORT_ENCODING": "utf-8",
        "ROBOTSTXT_OBEY": False,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }
)

process.crawl(LaptopLK)
# process.crawl(RedTech)
# process.crawl(NanoTek)
# process.crawl(Abans)
process.start()