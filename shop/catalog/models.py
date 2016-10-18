# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Category(models.Model):
	name = models.CharField(max_length=40)

	def __str__(self):
		return self.name

class Item(models.Model):
	name = models.CharField(max_length=80)
	description = models.CharField(max_length=1000, blank=True)
	price = models.IntegerField(default=0)
	image = models.URLField(null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class Review(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	name = models.CharField(max_length=80)
	text = models.CharField(max_length=1000)
	rating = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)
