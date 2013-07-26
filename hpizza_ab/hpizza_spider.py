# -*- coding: utf-8 -*-

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from models import ProductItem, RestoranItem, ProductPortionItem, ProductConnectionItem
import re
from scrapy import log
from time import sleep
from urllib import urlopen

stop_functions = []

def _msg_encode(s):
    return s.encode('cp1251')

class HPizzaSpider(CrawlSpider):
    name = "hpizza"
    allowed_domains = ["www.hardpizza.ru"]
    start_urls = ["http://www.hardpizza.ru/", ]
    rules = (
        Rule(SgmlLinkExtractor(allow=('hardpizza', ),deny=('guestbook','diskont','oplat','component','/pizza/','/dostavka-rollov/','zakazat-rolly')), callback='parse_item', follow=False),
    )
    re_product_id = re.compile ('id=\"productPrice')
    sleep_time = 5
    findstr = 'salesPrice":"'
    valuestr = 'value="'

    def __init__(self, restoran_mame='Hard Pizza', *a, **kw):
        restoran_item = RestoranItem()
        restoran_item['restoran_name'] = restoran_mame
        self.restoran_obj = restoran_item.save()
        self.valuestr_len = len(self.valuestr)
        self.findstr_len = len(self.findstr)
        super (HPizzaSpider,self).__init__(*a, **kw)

    def parse_item (self, response):
        log.msg('Start parsing '+response.url,level=log.DEBUG,spider=self)
        hxs = HtmlXPathSelector(response)
        list_rows = hxs.select('//*[@class="row"]')
        for rw in list_rows:
            product_split = self.re_product_id.split(rw.extract())
            product_blocks = rw.select ('.//div[@class="spacer"]')
            if len (product_split) > 1:
                for i,product_str in enumerate(product_split[1:]):
                    product_item = ProductItem()
                    product_item['title'] = product_blocks[i].select('.//h3').extract()[0].replace (u'<h3>\r\n\t\t\t\t\t',u'').replace (u'\t\t\t\t\t\t\t\t\t\t</h3>',u'').strip()
                    product_item['restoran'] = self.restoran_obj
                    product_obj = product_item.read_model_for_key()
                    product_conn_item = ProductConnectionItem()
                    id = re.split('\"',product_str)[0]
                    if not product_obj:
                        product_item['price'] = 120
                        product_obj = product_item.save()
                        log.msg(_msg_encode(u'New product "{0}" in restoran {1}'.format(unicode(product_item['title']),unicode(self.restoran_obj))),level=log.INFO,spider=self)
                        product_conn_item['product_site_id'] = id
                    else:
                        product_conn_item['product'] = product_obj
                        if not product_conn_item.set_items_for_model():
                            product_conn_item['product_site_id'] = id
                        elif product_conn_item['product_site_id'] != id:
                            log.msg(_msg_encode(u'Site ID for product "{0}" in restoran {1} was changed. Old ID is {2}, new ID is {3}'.format(
                                unicode(product_item['title']),unicode(self.restoran_obj),product_conn_item['product_site_id'],id)),
                                level=log.WARNING,spider=self)
                            product_conn_item['product_site_id'] = id
                    size_blocks = product_blocks[i].select('.//div[@class="field_1"]')
                    for sz in size_blocks:
                        portion_item = ProductPortionItem()
                        portion_item['product'] = product_obj
                        sz_extr = sz.extract()
                        p = sz_extr[sz_extr.find(self.valuestr)+self.valuestr_len:]
                        p = p[:p.find('"')]
                        q = sz.select('.//label[@class="other-customfield"]').extract()[0]
                        q = q[q.find('>')+1:]
                        q = q[:q.find('<')].strip()
                        portion_item['portion'] = q
                        portion_item['value'] = p
                        wrk_url = "http://www.hardpizza.ru/index.php?option=com_virtuemart&nosef=1&view=productdetails&task=recalculate&virtuemart_product_id="+\
                                  product_conn_item['product_site_id'].strip()+"&format=json&amp;lang=ru&customPrice%255B0%255D%255B11%255D%3D"+portion_item['value']+\
                                  "%26quantity%255B%255D%3D1%26option%3Dcom_virtuemart%26virtuemart_product_id%255B%255D%3D"+product_conn_item['product_site_id'].strip()+\
                                  "%26virtuemart_manufacturer_id%3DArray%26"
                        p = urlopen(wrk_url).read()
                        p = p[p.find(self.findstr)+self.findstr_len:]
                        try:
                            q = int(p[:p.find('"')].strip())
                        except ValueError:
                            q = 0
                        log.msg(_msg_encode(u'Portion "{2}" of product "{0}" in restoran {1}.'.format(
                                unicode(product_item['title']),unicode(self.restoran_obj),unicode(portion_item['portion']))),
                                level=log.DEBUG,spider=self)
                        if portion_item.set_items_for_model():
                            if portion_item['price'] != q:
                                log.msg(_msg_encode(u'Price for portion "{4}" of product "{0}" in restoran {1} was changed. Old price is {2}, new price is {3}'.format(
                                unicode(product_item['title']),unicode(self.restoran_obj),unicode(portion_item['price']),
                                unicode(q),unicode(portion_item['portion']))),
                                level=log.INFO,spider=self)
                        portion_item['price'] = q
                        obj = portion_item.save()
                        if not obj:
                            log.msg(_msg_encode(u'Cannot save data. Product - {0}, portion - {1}, value={2}'.format(unicode(self.portion_item['product']),
                                        unicode(self.portion_item['portion']),self.portion_item['value'])),level=log.ERROR,spider=self)
                        sleep (self.sleep_time)
                    product_item['price'] = portion_item.get_minimal_price()
                    product_conn_item['product'] = product_item.save()
                    product_conn_item.save()
        log.msg('Finish parsing '+response.url,level=log.DEBUG,spider=self)

