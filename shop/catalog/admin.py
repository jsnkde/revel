# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Category, Item, Review, Currency, Accessory, Replacement, ReplacementCatalog

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Review)
admin.site.register(Currency)
admin.site.register(Accessory)
admin.site.register(Replacement)
admin.site.register(ReplacementCatalog)