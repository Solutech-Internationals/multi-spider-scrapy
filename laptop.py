

import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DropItem
from scrapy.loader import ItemLoader
from itemloaders.processors import  MapCompose, TakeFirst
from w3lib.html import remove_tags
from ai_extract import extractDescriptionAi
import json
import requests

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
    site = scrapy.Field(
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
    def to_dict(self):
        return {field: value for field, value in self.items()}

    def validate(self):
        required_fields = ['title', 'price', 'url', 'image', 'description', 'site']
        for field in required_fields:
            if not self.get(field):
                raise scrapy.exceptions.DropItem(f"Missing required field: {field}")

def clean_title_and_description_alternative(raw_title):
    if raw_title is None:
        return None, None

    phrase = "– Order Now! – "

    raw_title = raw_title.replace(phrase, "")

    # Example cleaning process
    cleaned_title = raw_title.strip()
    description = cleaned_title

    return cleaned_title, description


class LaptopScraper(scrapy.Spider):
    name = 'laptop_spider'

    start_urls = [
        "https://www.laptop.lk/?s=&product_cat=laptops&post_type=product",
        "https://buyabans.com/computers/laptops",
        "https://redtech.lk/product-category/laptops-notebooks/",
        "https://www.nanotek.lk/category/laptops"
    ]

    data = []


    def parse(self, response):
        if "laptop.lk" in response.url:
            yield from self.parse_laptoplk(response)
        elif "abans" in response.url:
            yield from self.parse_abans(response)
        elif "redtech" in response.url:
            yield from self.parse_redtech(response)
        elif "nanotek" in response.url:
            yield from self.parse_nanotek(response)

    def parse_description_laptopLK(self, response):
        loader = response.meta['loader']
        descs = response.css('div#tab-specification p::text').extract()

        description = ' | '.join(descs)

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

        item = loader.load_item()

        try:
            item.validate()
            if item not in self.data:
                self.data.append(item)
        except DropItem as e:
            self.logger.warning(f"Item dropped: {e}")


    def parse_laptoplk(self, response):
        for product in response.css("li.product"):
            # Check if the product is out of stock
            if product.css("span.wcsob_soldout::text").get() == "Out Of Stock":
                continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "h2.woocommerce-loop-product__title")
            loader.add_css("price", "span.woocommerce-Price-amount bdi::text")
            loader.add_value("url", product.css("a.woocommerce-LoopProduct-link::attr(href)").get())
            loader.add_css("image", "img.attachment-woocommerce_thumbnail::attr(src)")
            loader.add_value("site", "laptop.lk")

            item = loader.load_item()

            # Check if the item already exists in self.data based on unique attributes
            existing_item = any(d.get('title') == item.get('title') and d.get('url') == item.get('url') for d in self.data)

            if existing_item:
                self.logger.info(f"Item already exists: {item.get('title')}, skipping costly extraction.")
                return

            inner_page = product.css('a.woocommerce-LoopProduct-link::attr(href)').get()

            if inner_page:
                request = response.follow(inner_page, self.parse_description_laptopLK)
                request.meta['loader'] = loader
                yield request
            else:
                # Validate the item and add to self.data if valid
                try:
                    item.validate()
                    if item not in self.data:
                        self.data.append(item)
                except DropItem as e:
                    self.logger.warning(f"Item dropped: {e}")


    def parse_abans(self, response):
        for product in response.css("li.product-item"):

            # Check if the product is out of stock
            if product.css("div.stock span::text").get() == "Out of stock":
                continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_css("title", "a.product-item-link::text")
            loader.add_css("price", "span.price::text")
            loader.add_value("url", product.css("a.product-item-link::attr(href)").get())
            loader.add_css("image", "img.product-image-photo::attr(src)")
            loader.add_value("site", "abans")

            item = loader.load_item()  # Load the item
            item = loader.load_item()

            # Check if the item already exists in self.data based on unique attributes
            existing_item = any(d.get('title') == item.get('title') and d.get('url') == item.get('url') for d in self.data)

            if existing_item:
                self.logger.info(f"Item already exists: {item.get('title')}, skipping costly extraction.")
                return
            raw_price = item.get("price")  # Access the 'title' field from the loaded item
            price = clean_price(raw_price)
            loader.replace_value("price", price)
            inner_page = product.css('a.product-item-photo::attr(href)').get()
            if inner_page:
                request = response.follow(inner_page, self.parse_description)
                request.meta['loader'] = loader
                yield request
            else:
                item = loader.load_item()
            # Validate the item
            try:
                item.validate()
                self.data.append(item)
            except DropItem as e:
                self.logger.warning(f"Item dropped: {e}")

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_abans)
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

        item = loader.load_item()

        # Validate the item
        try:
            item.validate()
            if item not in self.data:
                self.data.append(item)
        except DropItem as e:
            self.logger.warning(f"Item dropped: {e}")

    def parse_redtech(self, response):
        for product in response.css("li.product"):

            if product.css("b.br-labels-css::text").get() == "Out of Stock":
                continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            raw_title = product.css("h2.woocommerce-loop-product__title::text").extract_first()
            cleaned_title, description = clean_title_and_description_alternative(raw_title)
            loader.add_value("title", cleaned_title)
            loader.add_css("price", "span.woocommerce-Price-amount bdi::text")
            loader.add_value("url", product.css("a.woocommerce-LoopProduct-link::attr(href)").get())
            loader.add_css("image", "div.product-thumbnail img::attr(data-src)")
            loader.add_value("description", description)
            loader.add_value("site", "redtech")

            item = loader.load_item()

            # Check if the item already exists in self.data based on unique attributes
            existing_item = any(d.get('title') == item.get('title') and d.get('url') == item.get('url') for d in self.data)

            if existing_item:
                self.logger.info(f"Item already exists: {item.get('title')}, skipping costly extraction.")
                continue

            extracted_content = extractDescriptionAi(description)

            loader.add_value('ram', extracted_content.get('ram', ''))
            loader.add_value('gpu', extracted_content.get('gpu', ''))
            loader.add_value('processor', extracted_content.get('processor', ''))
            loader.add_value('storage', extracted_content.get('storage', ''))
            loader.add_value('good_for_students', extracted_content.get('good_for_students', {}).get('is_suitable', ''))
            loader.add_value('good_for_students_reason', extracted_content.get('good_for_students', {}).get('reason', ''))
            loader.add_value('good_for_developers', extracted_content.get('good_for_developers', {}).get('is_suitable', ''))
            loader.add_value('good_for_developers_reason', extracted_content.get('good_for_developers', {}).get('reason', ''))
            loader.add_value('good_for_video_editors', extracted_content.get('good_for_video_editors', {}).get('is_suitable', ''))
            loader.add_value('good_for_video_editors_reason', extracted_content.get('good_for_video_editors', {}).get('reason', ''))
            loader.add_value('good_for_gaming', extracted_content.get('good_for_gaming', {}).get('is_suitable', ''))
            loader.add_value('good_for_gaming_reason', extracted_content.get('good_for_gaming', {}).get('reason', ''))
            loader.add_value('good_for_business', extracted_content.get('good_for_business', {}).get('is_suitable', ''))
            loader.add_value('good_for_business_reason', extracted_content.get('good_for_business', {}).get('reason', ''))

            item = loader.load_item()  # Load the item again after adding more values

            # Validate the item
            try:
                item.validate()
                if item not in self.data:
                    self.data.append(item)
            except DropItem as e:
                self.logger.warning(f"Item dropped: {e}")

        next_page = response.css('a.page-numbers::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse_redtech)
        else:
            self.logger.info("No next page found.")

    def parse_nanotek(self, response):
        for product_item in response.css('li.ty-catPage-productListItem'):
            link = product_item.css('a::attr(href)').get()
            if link:
                yield response.follow(link, self.parse_items_nanotech)

        next_page = response.css('li a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_nanotek)

    def parse_items_nanotech(self, response):
        if response.css("span.ty-special-msg::text").get() == "Out of Stock":
            return

        loader = ItemLoader(item=ProductItem(), response=response)
        loader.add_css('title', 'h1.ty-productTitle::text')
        loader.add_css('price', 'span.ty-price-now::text')
        loader.add_value("url", response.url)
        loader.add_css('image', 'div.ty-productPage-content-imgHolder img::attr(src)')
        description = response.css('div.ty-productPage-info').extract_first()
        loader.add_value('description', description.replace('\r', ''))
        loader.add_value('site', 'nanotek')

        item = loader.load_item()

        # Check if the item already exists in self.data based on unique attributes
        existing_item = any(d.get('title') == item.get('title') and d.get('url') == item.get('url') for d in self.data)

        if existing_item:
            self.logger.info(f"Item already exists: {item.get('title')}, skipping costly extraction.")
            return

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

        item = loader.load_item()

        # Validate the item
        try:
            item.validate()
            if item not in self.data:
                self.data.append(item)
        except DropItem as e:
            self.logger.warning(f"Item dropped: {e}")


    def close(self, reason):
        with open("laptops.json", "w") as f:
            json.dump([item.to_dict() for item in self.data], f)

        self.send_data_to_api(self.data, 'http://localhost:8080/api/saveLaptops')

        self.data.clear()

    def send_data_to_api(self, data, endpoint):
        chunk_size = 20
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            json_data = json.dumps([item.to_dict() for item in chunk])
            response = requests.post(endpoint, headers={"Content-Type": "application/json", "x-api-key": "your-api-key"}, data=json_data)
            if response.status_code != 201:
                print(response.text)
            else:
                print(f"Data sent successfully: {response.status_code}")

def clean_price(raw_price):
    if raw_price is None:
        return None

    cleaned_price = raw_price.replace("Rs.", "").replace(",", "").strip()
    return cleaned_price

# Configure CrawlerProcess to export to JSON
process = CrawlerProcess(settings={
    "FEEDS": {
        "laptops.json": {"format": "json"},
    },
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    "FEED_EXPORT_ENCODING": "utf-8",
    "ROBOTSTXT_OBEY": False,
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
})


process.crawl(LaptopScraper)
process.start()

# Save the data to a JSON file
with open('laptops.json', 'w', encoding='utf-8') as f:
    json.dump([item.to_dict() for item in LaptopScraper.data], f, ensure_ascii=False, indent=4)

