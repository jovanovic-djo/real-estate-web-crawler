import random
import scrapy
from realestate.items import ApartmentItem


NUMBER_OF_PAGES = 99


class ApartmentSpider4Zida(scrapy.Spider):
    name = "apartmentspider4zida"
    allowed_domains = ["4zida.rs"]
    start_urls = ["https://4zida.rs/prodaja-stanova"]

    custom_settings = {
        'FEEDS': {
            'apartmentsdata.csv': {'format': 'csv'},
        },
        'ITEM_PIPELINES': {
            'realestate.pipelines.Apartments4ZidaPipeline': 300
        }
    }

    def parse(self, response):

        apartments = response.css('div[test-data="ad-search-card"]')

        for item in apartments:
            apartment_item = ApartmentItem()

            # Header link holds title, location, price and price per m² as <p> elements
            header = item.css('a.justify-between')
            location = header.xpath('.//p[contains(@class, "line-clamp-2")]/text()').get()

            # Feature chips, e.g. ['52m²', '2 sobe', '7/13 spratova', 'Prazno', 'Uknjiženo']
            chips = [chip.strip() for chip in item.css('span.truncate::text').getall()]

            apartment_item['title'] = header.xpath('.//p[contains(@class, "truncate")]/text()').get()
            apartment_item['price'] = header.xpath('.//p[contains(., "€") and not(contains(., "€/m²"))]//text()').get()
            apartment_item['square_price'] = header.xpath('.//p[contains(., "€/m²")]/text()').get()
            apartment_item['area'] = next((c for c in chips if c.endswith('m²')), None)
            apartment_item['rooms'] = next((c for c in chips if 'sob' in c), None)
            apartment_item['floor'] = next((c for c in chips if any(k in c.lower() for k in ('sprat', 'prizemlje', 'suteren', 'potkrovlje'))), 'n/a')
            apartment_item['city'] = location
            apartment_item['location'] = location
            apartment_item['source'] = "4zida"

            yield apartment_item
        
        current_page = int(response.url.split('=')[-1]) if '=' in response.url else 1

        next_page_number = current_page + 1

        if next_page_number <= NUMBER_OF_PAGES:
            next_page = f"https://4zida.rs/prodaja-stanova?strana={next_page_number}"
            yield response.follow(next_page, callback=self.parse, headers={'User-Agent': random.choice(self.settings.get('USER_AGENTS'))})



