# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.djangoitem import DjangoItem
from django.core.exceptions import ObjectDoesNotExist

class HPizzaItem(Item):
    # define the fields for your item here like:
    # name = Field()
    id = Field()
    name = Field()
    value = Field()
    size = Field()

class GnsDjangoItem(DjangoItem):
    _key_fields = []

    def __init__(self, *args, **kwargs):
        super (GnsDjangoItem,self).__init__(*args,**kwargs)
        self._generate_key_fields()

    def _generate_key_fields(self):
        for i,fld in enumerate(self._key_fields):
            if not fld in self._model_fields:
                self._key_fields.pop(i)
        if not self._key_fields: self._key_fields = [self._model_fields[0]]
        self._not_key_fields = [fld for fld in self._model_fields if fld not in self._key_fields]

    def change_key_fields(self,new_key_fields):
        if new_key_fields:
           self._key_fields = new_key_fields
           self._generate_key_fields()

    def read_model_for_key(self):
        key_value = {}
        for fld in self._key_fields:
            if fld in self._values:
                key_value[fld]=self._values[fld]
            else:
                return None
        try:
            obj = self.django_model._default_manager.filter(**key_value).get()
        except ObjectDoesNotExist:
            obj = None
        return obj

    def set_items_for_model(self):
        obj = self.read_model_for_key()
        if obj:
            for fld in self._not_key_fields:
                self.__setitem__(fld,obj.__getattribute__(fld))
        return obj


    def save(self, commit=True):
        model = self.read_model_for_key()
        if model:
            for fld in self._not_key_fields:
                if fld in self._values: model.__setattr__(fld,self.__getitem__(fld))
        else:
            modelargs = dict((k, self.get(k)) for k in self._values
                         if k in self._model_fields)
            model = self.django_model(**modelargs)
        if commit:
            model.save()
        return model

