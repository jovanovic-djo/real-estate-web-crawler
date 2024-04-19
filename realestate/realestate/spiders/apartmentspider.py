import random
import scrapy
from realestate.items import ApartmentItem
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.reactor import install_reactor

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")


NUMBER_OF_PAGES = 4
finished_crawls = 0


class ApartmentSpider4Zida(scrapy.Spider):
    name = "apartmentspider4zida"
    allowed_domains = ["4zida.rs"]
    start_urls = ["https://4zida.rs/prodaja-stanova"]

    custom_settings = {
        'FEEDS': {
            'apartmentsdata.csv': {'format': 'csv'},
        },
        'ITEM_PIPELINES': {
            'realestate.pipelines.Apartments4ZidaPipeline': 400
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
        
        global finished_crawls
        finished_crawls += 1  

        if finished_crawls == 2:  
            reactor.stop()  



class ApartmentSpiderHaloOglasi(scrapy.Spider):
    name = "apartmentspiderhalooglasi"
    allowed_domains = ["halooglasi.com"]
    start_urls = ["https://www.halooglasi.com/nekretnine/prodaja-stanova"]

    custom_settings = {
        'FEEDS': {
            'apartmentsdata.csv': {'format': 'csv'},
        },
        'ITEM_PIPELINES': {
            'realestate.pipelines.ApartmentsHaloOglasiPipeline': 300
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
            apartment_item['location'] = 1
            apartment_item['source'] = "halooglasi"

            yield apartment_item
        
        current_page = int(response.url.split('=')[-1]) if '=' in response.url else 1

        next_page_number = current_page + 1

        if next_page_number <= NUMBER_OF_PAGES:
            next_page = f"https://www.halooglasi.com/nekretnine/prodaja-stanova?page={next_page_number}"
            yield response.follow(next_page, callback=self.parse, headers={'User-Agent': random.choice(self.settings.get('USER_AGENTS'))})

        global finished_crawls
        finished_crawls += 1  

        if finished_crawls == 2:  
            reactor.stop()  

# configure_logging()
# runner = CrawlerRunner()

# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(ApartmentSpider4Zida)
#     yield runner.crawl(ApartmentSpiderHaloOglasi)
#     reactor.stop()

# crawl()
# reactor.run()