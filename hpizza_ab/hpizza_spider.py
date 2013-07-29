# -*- coding: utf-8 -*-

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from models import ProductItem, RestoranItem, ProductPortionItem, ProductConnectionItem, ReadAllItemsFromDB
import re
from scrapy import log
from time import sleep
from urllib import urlopen

stop_functions = []

def _msg_encode(s):
    return s.encode('cp1251')

def _items_index1(items,field,value):
    item = [i for i in items if i[field]==value]
    return -1 if not item else items.index(item[0])

def _items_index2(items,field1,value1,field2,value2):
#    print field1,value1,field2,value2
    item = [i for i in items if (i[field1]==value1 and i[field2]==value2)]
    return -1 if not item else items.index(item[0])


class HPizzaSpider(CrawlSpider):
    name = "hpizza"
    allowed_domains = ["www.hardpizza.ru"]
    start_urls = ["http://www.hardpizza.ru/", ]
    rules = (
        Rule(SgmlLinkExtractor(deny=('guestbook','diskont','oplat','component','/pizza/','/dostavka-rollov/','zakazat-rolly')), callback='parse_item', follow=True),
    )
    re_product_id = re.compile ('id=\"productPrice')
    sleep_time = 18
    findstr = 'salesPrice":"'
    valuestr = 'value="'


    def __init__(self, restoran_mame='Hard Pizza', *a, **kw):
        self.valuestr_len = len(self.valuestr)
        self.findstr_len = len(self.findstr)
        self.new_products_ind=100
        (self.restoran_item,self.prod_items,self.prod_conn_items,self.prod_port_items) = ReadAllItemsFromDB(restoran_mame)
#        print self.prod_items[0]
#        for i in [x for x in self.prod_port_items if x['product']==self.prod_items[0]['pk']] : print i
#        assert False
        super (HPizzaSpider,self).__init__(*a, **kw)

    def parse_item (self, response):
        log.msg('Start parsing '+response.url,level=log.INFO,spider=self)
        hxs = HtmlXPathSelector(response)
        list_rows = hxs.select('//*[@class="row"]')
        product_items = []
        portion_items = []
        pr_connection_items =[]
        a = 0
        for rw in list_rows:
            product_split = self.re_product_id.split(rw.extract())
            product_blocks = rw.select ('.//div[@class="spacer"]')
            if len (product_split) > 1:
                for i,product_str in enumerate(product_split[1:]):
                    product_item = ProductItem()
                    product_item['title'] = product_blocks[i].select('.//h3').extract()[0].replace (u'<h3>\r\n\t\t\t\t\t',u'').replace (u'\t\t\t\t\t\t\t\t\t\t</h3>',u'').strip()
                    product_item['restoran'] = self.restoran_item['pk']
                    product_ind = _items_index2(self.prod_items,'restoran',product_item['restoran'],'title',product_item['title'])
                    product_conn_item = ProductConnectionItem()
                    id = re.split('\"',product_str)[0]
                    if product_ind==-1:
                        product_item['pk']='new'+str(self.new_products_ind)
                        self.new_products_ind += 1
                        log.msg(_msg_encode(u'New product "{0}" in restoran {1}'.format(unicode(product_item['title']),unicode(self.restoran_item['restoran_name']))),level=log.INFO,spider=self)
                        product_conn_item['product_site_id'] = id
                        product_conn_item['product'] = product_item['pk']
                        product_conn_item['pk']=0
                    else:
                        product_item['pk'] = self.prod_items[product_ind]['pk']
                        product_conn_item['product'] = product_item['pk']
                        pr_conn_ind = _items_index1(self.prod_conn_items,'product',product_conn_item['product'])
                        product_conn_item['product_site_id'] = id
                        if pr_conn_ind>-1:
                            if self.prod_conn_items[pr_conn_ind]['product_site_id'] != id:
                                log.msg(_msg_encode(u'Site ID for product "{0}" in restoran {1} was changed. Old ID is {2}, new ID is {3}'.format(
                                unicode(product_item['title']),unicode(self.restoran_item['restoran_name']),self.prod_conn_items[pr_conn_ind]['product_site_id'],id)),
                                level=log.WARNING,spider=self)
                            product_conn_item['pk']= self.prod_conn_items[pr_conn_ind]['pk']
                        else:
                            product_conn_item['pk']=0
                    size_blocks = product_blocks[i].select('.//div[@class="field_1"]')
                    for sz in size_blocks:
                        portion_item = ProductPortionItem()
                        portion_item['product'] = product_item['pk']
                        sz_extr = sz.extract()
                        p = sz_extr[sz_extr.find(self.valuestr)+self.valuestr_len:]
                        p = p[:p.find('"')]
                        q = sz.select('.//label[@class="other-customfield"]').extract()[0]
                        q = q[q.find('>')+1:]
                        q = q[:q.find('<')].strip()
                        portion_item['portion'] = q
                        portion_item['value'] = p
                        p = self.start_urls[0].strip()
                        p =  p if p.endswith('/') else p + '/'
                        wrk_url = p+"index.php?option=com_virtuemart&nosef=1&view=productdetails&task=recalculate&virtuemart_product_id="+\
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
                                unicode(product_item['title']),unicode(self.restoran_item['restoran_name']),unicode(portion_item['portion']))),
                                level=log.DEBUG,spider=self)
                        port_ind = _items_index2(self.prod_port_items,'product',portion_item['product'],'portion',portion_item['portion']) if product_ind>-1 else -1
                        if port_ind>-1:
                            if self.prod_port_items[port_ind]['price'] != q:
                                log.msg(_msg_encode(u'Price for portion "{4}" of product "{0}" in restoran {1} was changed. Old price is {2}, new price is {3}'.format(
                                unicode(product_item['title']),unicode(self.restoran_item['restoran_name']),unicode(self.prod_port_items[port_ind]['price']),
                                unicode(q),unicode(portion_item['portion']))),
                                level=log.INFO,spider=self)
                            portion_item['pk'] = self.prod_port_items[port_ind]['pk']
                        else:
                            portion_item['pk'] = 0
                        portion_item['price'] = q
                        portion_items.append(portion_item)
                        sleep (self.sleep_time)
                    product_item['price'] = min([x['price'] for x in portion_items if x['product'] == product_item['pk']])
                    product_items.append(product_item)
                    pr_connection_items.append(product_conn_item)
        log.msg('Finish parsing '+response.url,level=log.INFO,spider=self)
        return [self.restoran_item]+product_items+pr_connection_items+portion_items

