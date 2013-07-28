# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from time import sleep
from scrapy import log

class HpizzaPipeline(object):
    def process_item(self, item, spider):
        log.msg(' '.join(['PIPE - ',item.__class__.__name__,unicode(item).encode('cp1251')]),level=log.INFO)
        sleep(10)
        return item
