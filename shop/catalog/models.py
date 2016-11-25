# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from  django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.core.mail import send_mail


class AbstractClass(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Currency(AbstractClass):
	name = models.CharField(max_length=25)
	ticker = models.CharField(max_length=4)

	def __unicode__(self):
		return self.name


class Category(models.Model):
	name = models.CharField(max_length=40)

	def __unicode__(self):
		return self.name


class ValueItem(AbstractClass):	
	name = models.CharField(max_length=100)		
	price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

	def __unicode__(self):
		return self.name

	class Meta:
		abstract = True


class Accessory(ValueItem):
	pass


class RatedItem(models.Model):
	name = models.CharField(max_length=100, primary_key=True)		
	price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	ticker = models.CharField(max_length=4)
	avg_rating = models.IntegerField(default=0)

	class Meta:
		managed = False
		db_table = 'rated_item'

	def __unicode__(self):
		return "%s: %d %s" % (self.name, self.price, self.ticker)


class Item(ValueItem):
	description = models.CharField(max_length=1000, blank=True)
	image = models.ImageField(null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	accessories = models.ManyToManyField(Accessory, blank=True)

	def __unicode__(self):
		return self.name


class Review(AbstractClass):
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	name = models.CharField(max_length=80)
	text = models.CharField(max_length=1000)
	rating = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)


class Replacement(ValueItem):
	items = models.ManyToManyField(Item, through='ReplacementCatalog', blank=True)


class ReplacementCatalog(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	replacement = models.ForeignKey(Replacement, on_delete=models.CASCADE)	


class OrderItem(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE)

	def __unicode__(self):
		return self.item.name


class Order(AbstractClass):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	items = models.ManyToManyField(OrderItem, blank=True)
	done = models.BooleanField(default=False)


class CustomUser(AbstractBaseUser):
	rank = models.CharField(max_length=100)


class B(models.Model):
	name = models.CharField(max_length=10)


class A(B):
	state = models.CharField(max_length=10)
