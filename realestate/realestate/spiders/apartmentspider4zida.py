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

        apartments = response.css('div.flex.flex-col.gap-4')
        
        for item in apartments:
            apartment_item = ApartmentItem()

            apartment_item['title'] = item.css('p.truncate.font-medium.leading-tight.desk\:text-lg::text').get()
            apartment_item['price'] = item.css('p.rounded-tl.bg-spotlight.px-2.py-1.text-lg.font-bold.desk\\:text-2xl::text').get()
            apartment_item['square_price'] = item.css('p.rounded-bl.border.border-spotlight.bg-spotlight-300.px-2.text-2xs.font-medium.text-spotlight-700.desk\\:text-xs::text').get()
            apartment_item['area'] = item.css('a.px-1.py-3.text-center.font-bold.leading-\\[0\\.9rem\\]::text').get() 
            apartment_item['rooms'] = item.css('a.px-1.py-3.text-center.font-bold.leading-\\[0\\.9rem\\]::text').get() 
            apartment_item['floor'] = item.css('a.px-1.py-3.text-center.font-bold.leading-\\[0\\.9rem\\]::text').get() 
            apartment_item['city'] = item.css('p.line-clamp-2.text-wrap.text-xs.\\!leading-tight.text-foreground\\/60.desk\\:line-clamp-3.desk\\:text-sm::text').get() 
            apartment_item['location'] = item.css('p.line-clamp-2.text-wrap.text-xs.\\!leading-tight.text-foreground\\/60.desk\\:line-clamp-3.desk\\:text-sm::text').get()
            apartment_item['source'] = "4zida"

            yield apartment_item
        
        current_page = int(response.url.split('=')[-1]) if '=' in response.url else 1

        next_page_number = current_page + 1

        if next_page_number <= NUMBER_OF_PAGES:
            next_page = f"https://4zida.rs/prodaja-stanova?strana={next_page_number}"
            yield response.follow(next_page, callback=self.parse, headers={'User-Agent': random.choice(self.settings.get('USER_AGENTS'))})



