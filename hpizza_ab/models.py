# -*- coding: utf-8 -*-

""" Модуль содержит описание моделей Django и соответствующих им Item'ов Scrapy, а также процедуру считывания
всей информации из моделей в списки Item-ов.
"""

from django.db import models
from gns_djangoitem import GnsDjangoItem
from scrapy.item import Field

class Product(models.Model):
    """ Модель, содержащая блюда """
    title = models.CharField(max_length=255) # Название блюда,  в рамках задачи считать сочитание полей title и restoran_id уникальным
    price = models.IntegerField(blank=True) # Цена наименьшей порции
    restoran = models.ForeignKey("Restoran") # Ресторан, из которого взято блюдо (создайте модель самостоятельно).

    def __unicode__(self):
        a = self.restoran
        return ' | '.join([unicode(self.restoran),self.title,str(self.price)])

class ProductItem(GnsDjangoItem):
    """ Item, опписывающий блюда """
    django_model = Product
    _key_fields = ['title','restoran']
    pk = Field()

class ProductPortion(models.Model):
    """ Модель, содержащая порции """
    product = models.ForeignKey("Product")
    portion = models.CharField(max_length = 255) # Название порции. Например, 25cм, 35см, 45см, 400г, 681г, 1.2кг,  8 штук, 36 штук, ¼, ½ , ¾,
    price = models.IntegerField() # Цена порции.

    def __unicode__(self):
        return ' / '.join([unicode(self.product),self.portion,unicode(self.price)])

class ProductPortionItem(GnsDjangoItem):
    """ Item, опписывающий порции """
    django_model = ProductPortion
    _key_fields = ['product','portion']
    value = Field()
    pk = Field()

    def get_minimal_price(self):
        try:
            qs = self.django_model._default_manager.filter(product=self.__getitem__('product'))
        except ObjectDoesNotExist:
            return 0
        return min([obj.price for obj in qs])

class Restoran(models.Model):
    """ Модель, содержащая рестораны """
    restoran_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.restoran_name

class RestoranItem(GnsDjangoItem):
    """ Item, опписывающий рестораны """
    django_model = Restoran
    pk = Field()

class ProductConnection(models.Model):
    """ Модель, содержащая ID блюд на сайте """
    product = models.ForeignKey('Product')
    product_site_id = models.CharField(max_length=10)

    def __unicode__(self):
        return ' - '.join((unicode(self.product),self.product_site_id))

class ProductConnectionItem(GnsDjangoItem):
    """ Item, опписывающий ID блюд на сайте """
    django_model = ProductConnection
    pk = Field()

def ReadAllItemsFromDB(restoran_name):
    """ Считывает всю информацию по одному ресторану из моделей в набор списков соответствующих Item-ов """
    restoran_item = RestoranItem()
    restoran_item['restoran_name'] = restoran_name
    restoran_obj = restoran_item.save()
    restoran_item['pk'] = restoran_obj.pk
    product_items = []
    product_conn_items = []
    portion_items = []
    for product in Product._default_manager.filter(restoran=restoran_obj):
        product_items.append(ProductItem())
        product_items[-1]['title']=product.title
        product_items[-1]['pk']=product.pk
        product_items[-1]['restoran']=restoran_item['pk']
        product_items[-1]['price']=product.price
        product_conn_items.append(ProductConnectionItem())
        product_conn_items[-1]['product'] = product.pk
        product_conn = product_conn_items[-1].set_items_for_model()
        if not product_conn:
            product_conn_items[-1]['product_site_id']=None
            product_conn_items[-1]['pk']=0
        else:
            product_conn_items[-1]['pk']=product_conn.pk
        for portion in ProductPortion._default_manager.filter(product=product):
            portion_items.append(ProductPortionItem())
            portion_items[-1]['product']=product.pk
            portion_items[-1]['portion']=portion.portion
            portion_items[-1]['price']=portion.price
            portion_items[-1]['pk']=portion.pk
    return (restoran_item,product_items,product_conn_items,portion_items)



