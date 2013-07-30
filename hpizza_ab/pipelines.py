# -*- coding: utf-8 -*-

""" Модуль описывает механизм сохранения Item-ов, передающихся Scrapy-engine из Spider'а """

from time import sleep
from scrapy import log

class HpizzaPipeline(object):
    """ Класс, определяющий способ сохранения Item-ов, передающихся Scrapy-engine из Spider'а """

    def __init__(self):
        self.product_objects ={}
        self.restoran_obj = None

    def process_item(self, item, spider):
        """ Сохраняет отдельный Item. Действия зависят от типа полученного Item'а.
        При создании нового объекта в модели Product, являющегося ключевым для других типов, он сохраняется
        в списке для дальнейшего использования.
        """
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
#        sleep(3)
        return item
