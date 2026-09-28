import random
import re
import scrapy
from realestate.items import ApartmentItem


# 4zida serves at most 100 pages (2000 ads) per search; deeper pages repeat page 100.
# The spider splits the search into price bands (EUR) until each band fits under that cap.
MAX_PAGES = 100
MAX_RESULTS = MAX_PAGES * 20
MAX_PRICE = 20_000_000
MIN_BAND_WIDTH = 1000
BASE_URL = "https://www.4zida.rs/prodaja-stanova"


class ApartmentSpider4Zida(scrapy.Spider):
    name = "apartmentspider4zida"
    allowed_domains = ["4zida.rs"]

    custom_settings = {
        'FEEDS': {
            'apartmentsdata2026.csv': {'format': 'csv'},
        },
        'ITEM_PIPELINES': {
            'realestate.pipelines.Apartments4ZidaPipeline': 300
        },
        'DOWNLOAD_DELAY': 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Premium ads repeat across pages and ads priced on a band boundary appear in both bands
        self.seen_urls = set()

    def start_requests(self):
        yield self.band_request(0, MAX_PRICE)
        yield self.band_request(MAX_PRICE, None)

    def band_request(self, low, high):
        search_url = f"{BASE_URL}?skuplje_od={low}eur"
        if high is not None:
            search_url += f"&jeftinije_od={high}eur"
        return scrapy.Request(search_url, callback=self.parse,
                              cb_kwargs={'search_url': search_url, 'page': 1, 'low': low, 'high': high})

    def parse(self, response, search_url, page, low, high):

        if page == 1 and high is not None and high - low > MIN_BAND_WIDTH:
            match = re.search(r'([\d.]+)\s*oglas', re.sub(r'<[^>]+>', '', response.text))
            total = int(match.group(1).replace('.', '')) if match else 0
            if total > MAX_RESULTS:
                middle = (low + high) // 2 // 1000 * 1000
                yield self.band_request(low, middle)
                yield self.band_request(middle, high)
                return

        apartments = response.css('div[test-data="ad-search-card"]')
        new_on_page = 0

        for item in apartments:
            # Header link holds title, location, price and price per m² as <p> elements
            header = item.css('a.justify-between')

            url = response.urljoin(header.attrib.get('href', ''))
            if url in self.seen_urls:
                continue
            self.seen_urls.add(url)
            new_on_page += 1

            apartment_item = ApartmentItem()

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

        # Past the last page the site repeats earlier results, so stop once a page brings nothing new
        next_page_number = page + 1

        if new_on_page and next_page_number <= MAX_PAGES:
            next_page = f"{search_url}&strana={next_page_number}"
            yield response.follow(next_page, callback=self.parse,
                                  cb_kwargs={'search_url': search_url, 'page': next_page_number, 'low': low, 'high': high},
                                  headers={'User-Agent': random.choice(self.settings.get('USER_AGENTS'))})
