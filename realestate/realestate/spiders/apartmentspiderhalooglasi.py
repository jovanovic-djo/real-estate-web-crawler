import random
import scrapy
from realestate.items import ApartmentItem


NUMBER_OF_PAGES = 550


class ApartmentSpiderHaloOglasi(scrapy.Spider):
    name = "apartmentspiderhalooglasi"
    allowed_domains = ["halooglasi.com"]
    start_urls = ["https://www.halooglasi.com/nekretnine/prodaja-stanova"]

    custom_settings = {
        'FEEDS': {
            'apartmentsdata.csv': {'format': 'csv'},
        },
        'ITEM_PIPELINES': {
            'realestate.pipelines.ApartmentsHaloOglasiPipeline': 400
        }
    }

    def parse(self, response):

        apartments = response.css('div.row')
        for item in apartments:
            apartment_item = ApartmentItem()

            apartment_item['title'] = item.css('h3.product-title a::text').get()
            apartment_item['price'] = item.css('span[data-value]::attr(data-value)').get()
            apartment_item['square_price'] = item.css('div.price-by-surface span::text').get()
            apartment_item['area'] = item.css('ul.product-features li:nth-child(1) div.value-wrapper::text').get()
            apartment_item['rooms'] = item.css('ul.product-features li:nth-child(2) div.value-wrapper::text').get()
            apartment_item['floor'] = item.css('ul.product-features li:nth-child(3) div.value-wrapper::text').get()
            apartment_item['city'] = item.css('ul.subtitle-places li:nth-child(1) ::text').get()
            apartment_item['location'] = item.css('ul.subtitle-places').get()
            apartment_item['source'] = "halooglasi"

            yield apartment_item
        
        current_page = int(response.url.split('=')[-1]) if '=' in response.url else 1

        next_page_number = current_page + 1

        if next_page_number <= NUMBER_OF_PAGES:
            next_page = f"https://www.halooglasi.com/nekretnine/prodaja-stanova?page={next_page_number}"
            yield response.follow(next_page, callback=self.parse, headers={'User-Agent': random.choice(self.settings.get('USER_AGENTS'))})


