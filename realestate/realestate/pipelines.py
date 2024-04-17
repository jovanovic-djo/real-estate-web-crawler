# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class Apartments4zidaPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        apartments = adapter.field_names()
        for apartment in apartments:
            if not(all(item.values())):
                raise DropItem()
            else:
                adapter['title'] = adapter['title'].strip()

                adapter['price'] = int(adapter['price'].replace('.','').replace('€', '').strip())

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
                        adapter['floor'] = '-1'
                    case "nisko prizemlje":
                        adapter['floor'] = '0.5'
                    case "visoko prizemlje":
                        adapter['floor'] = '0.5'

                adapter['city'] = adapter['location'].split(',')[-1].strip()

                adapter['location'] = adapter['location'].rsplit(',', 1)[0].strip()


                return item
            
