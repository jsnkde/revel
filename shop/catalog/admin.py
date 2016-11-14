# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Category, Item, Review, Currency, Accessory, Replacement, ReplacementCatalog, Order


class ReviewInline(admin.StackedInline):
	model = Review

class ItemAdmin(admin.ModelAdmin):
	inlines = [ReviewInline, ]


admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Review)
admin.site.register(Currency)
admin.site.register(Accessory)
admin.site.register(Replacement)
admin.site.register(Order)
admin.site.register(ReplacementCatalog)