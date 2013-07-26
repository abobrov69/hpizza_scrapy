# -*- coding: utf-8 -*-

from django.db import models
from gns_djangoitem import GnsDjangoItem
from scrapy.item import Field

class TestModel(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return str(self.number) + ' ' + self.name

class Product(models.Model):
    title = models.CharField(max_length=255) # Название блюда,  в рамках задачи считать сочитание полей title и restoran_id уникальным
    price = models.IntegerField(blank=True) # Цена наименьшей порции
    restoran = models.ForeignKey("Restoran") # Ресторан, из которого взято блюдо (создайте модель самостоятельно).

    def __unicode__(self):
        a = self.restoran
        return ' | '.join([unicode(self.restoran),self.title,str(self.price)])

class ProductItem(GnsDjangoItem):
    django_model = Product
    _key_fields = ['title','restoran']

class ProductPortion(models.Model):
    product = models.ForeignKey("Product")
    portion = models.CharField(max_length = 255) # Название порции. Например, 25cм, 35см, 45см, 400г, 681г, 1.2кг,  8 штук, 36 штук, ¼, ½ , ¾,
    price = models.IntegerField() # Цена порции.

    def __unicode__(self):
        return ' / '.join([unicode(self.product),self.portion,unicode(self.price)])

class ProductPortionItem(GnsDjangoItem):
    django_model = ProductPortion
    _key_fields = ['product','portion']
    value = Field()

    def get_minimal_price(self):
        try:
            qs = self.django_model._default_manager.filter(product=self.__getitem__('product'))
        except ObjectDoesNotExist:
            return 0
        return min([obj.price for obj in qs])

class Restoran(models.Model):
    restoran_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.restoran_name

class RestoranItem(GnsDjangoItem):
    django_model = Restoran

class ProductConnection(models.Model):
    product = models.ForeignKey('Product')
    product_site_id = models.CharField(max_length=10)

    def __unicode__(self):
        return ' - '.join((unicode(self.product),self.product_site_id))

class ProductConnectionItem(GnsDjangoItem):
    django_model = ProductConnection


