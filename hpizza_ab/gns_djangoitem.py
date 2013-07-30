# -*- coding: utf-8 -*-

""" Модуль содержит класс GnsDjangoItem, являющийся расширением класса DjangoItem, имеющегося в Scrapy """

from scrapy.contrib.djangoitem import DjangoItem
from django.core.exceptions import ObjectDoesNotExist

class GnsDjangoItem(DjangoItem):
    """ Расширение класса DjangoItem, имеющегося в Scrapy. Имеет дополнительный спмсок полей (_key_filds), являющихся
    ключевыми для соответствующей модели Django. Имеет методы, позволяющие производить поиск по этим полям, заполнять поля
    Item'а из найденной записи БД. Сохранение, в отличие от родительского класса, приводит к обновлению существующей записи,
    найденной по ключевым полям, и только при отсутствии - к добавлению новой.
    """
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
        """ Меняет набор ключевых полей. """
        if new_key_fields:
           self._key_fields = new_key_fields
           self._generate_key_fields()

    def read_model_for_key(self):
        """
        Ищет объект в модели по ключевым полям. Собственные поля, соответствующие ключевым, должны быть инициализированы.
        Возвращает экземпляр класса модель или None, если поиск неудачен.
        """
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
        """ Производит поиск по ключевым полям и в случае успеха заполняет собственные неключевые поля значениями из модели"""
        obj = self.read_model_for_key()
        if obj:
            for fld in self._not_key_fields:
                self.__setitem__(fld,obj.__getattribute__(fld))
        return obj


    def save(self, commit=True):
        """
        Производит поиск по ключевым полям. В случае успеха в полученном объекте класса модели заполняет поля значениями
        обственных полей. В случае неуспеха создает новый объект класса модели и также заполняет его поля.
        При значении commit=True выполняет сохранение объекта класса модели.
        Возвращает этот объект в любом случа
        """
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

