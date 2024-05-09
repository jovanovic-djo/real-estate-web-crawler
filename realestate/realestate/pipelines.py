# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import math
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class Apartments4ZidaPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        if not(all(item.values())):
            raise DropItem()
        else:
            adapter['title'] = adapter['title'].strip()

            adapter['price'] = int(adapter['price'].replace('.','').replace('€', '').strip())
            if adapter['price'] < 5000:
                raise DropItem()

            adapter['square_price'] = int(adapter['square_price'].replace('.','').replace('€/m²', '').strip())

            adapter['area'] = int(adapter['area'].split('m')[0])

            adapter['rooms'] = float(adapter['rooms'].split('•')[1].split('•')[0].strip().split(' ')[0])

            if len(adapter['floor']) < 15:
                adapter['floor'] = 'n/a'
            else:
                adapter['floor'] = adapter['floor'].split('•')[-1].strip().lower()
                if '/' in adapter['floor']:
                    adapter['floor'] = adapter['floor'].split('/')[0]
                else:
                    adapter['floor'] = adapter['floor'].split('.')[0]
            match adapter['floor']:
                case "potkrovlje":
                    adapter['floor'] = 'p'
                case "prizemlje":
                    adapter['floor'] = '0'
                case "suteren":
                    adapter['floor'] = '-0.5'
                case "nisko prizemlje":
                    adapter['floor'] = '0.5'
                case "visoko prizemlje":
                    adapter['floor'] = '0.5'

            adapter['city'] = adapter['location'].split(',')[-1].strip()

            adapter['location'] = adapter['location'].rsplit(',', 1)[0].strip()


            return item
        



class ApartmentsHaloOglasiPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if not(all(item.values())):
            raise DropItem()
        else:
            adapter['title'] = adapter['title'].strip()

            adapter['price'] = int(adapter['price'].replace('.','').replace('€', '').strip())
            if adapter['price'] < 5000:
                raise DropItem()

            adapter['square_price'] = int(adapter['square_price'].replace('.','').replace('€/m', '').strip())
            if adapter['square_price'] > 10000:
                raise DropItem()

            adapter['area'] = int(math.ceil(float(adapter['area'].replace('m','').replace(',', '.').strip())))

            adapter['rooms'] = adapter['rooms'].strip()
            if adapter['rooms'] == '5+':
                adapter['rooms'] = '6'
            else:
                adapter['rooms'] = float(adapter['rooms'].strip())

            try:
                total_floors = adapter['floor'].split('/')[1].strip()
            except IndexError:
                total_floors = None 
            
            adapter['floor'] = adapter['floor'].split('/')[0].strip()
            match adapter['floor']:
                case 'SUT':
                    adapter['floor'] = '-0.5'
                case 'PSUT':
                    adapter['floor'] = '-0.5'
                case 'PR':
                    adapter['floor'] = '0'
                case 'VPR':
                    adapter['floor'] = '0.5'
                case _:
                    adapter['floor'] = str(self.roman_to_arabic(adapter['floor']))
            if adapter['floor'] == total_floors:
                adapter['floor'] = 'p'

            adapter['city'] = adapter['city'].strip()

            adapter['location'] = adapter['location'].replace('<ul class="subtitle-places"><li>', '').replace('</li><li>', ', ').replace('</li></ul>', '').split(',')[1:]

            return item
    
    def roman_to_arabic(self, roman):
        roman_numerals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        arabic_num = 0
        prev_value = 0

        for numeral in reversed(roman):
            value = roman_numerals[numeral]
            if value < prev_value:
                arabic_num -= value
            else:
                arabic_num += value
            prev_value = value

        return arabic_num
    