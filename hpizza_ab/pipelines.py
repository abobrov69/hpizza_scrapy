# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from time import sleep
from scrapy import log

class HpizzaPipeline(object):

    def __init__(self):
        self.product_objects ={}
        self.restoran_obj = None

    def process_item(self, item, spider):
        log.msg(' '.join(['PIPE - ',item.__class__.__name__,unicode(item).encode('cp1251')]),level=log.DEBUG)
        if item.__class__.__name__=='RestoranItem':
            if not self.restoran_obj:
                self.restoran_obj = item.save()
        elif item.__class__.__name__=='ProductItem':
            item['restoran']=self.restoran_obj
            obj = item.save()
            self.product_objects[item['pk']] = obj
        else:
            item['product'] = self.product_objects[item['product']]
            item.save()
        sleep(3)
        return item
