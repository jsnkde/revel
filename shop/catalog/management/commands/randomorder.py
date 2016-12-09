from django.core.management.base import BaseCommand, CommandError
from catalog.models import Order, OrderItem, Item
from django.contrib.auth.models import User
import string
import random
from rq import Queue, SimpleWorker
from redis import Redis
import django_rq
import time


def fill_order(id, num):
	order = Order.objects.get(id=id)	
	items = Item.objects.all()

	if not items.exists():
		raise Exception('No items exist')

	for i in range(0, num):
		it = items[random.randint(0, items.count() - 1)]
		print "\t", it.name, it.price, it.currency.ticker
		order_item = OrderItem(item=it)
		order_item.save()
		order.items.add(order_item)

	# Sleep to illustrate async nature of a job
	time.sleep(1)
	order.done = True
	order.save() 


def create_random_order(**options):
	users = User.objects.all()

	if not users.exists():
		raise Exception('No users exist')

	user = users[random.randint(0, users.count() - 1)]
	num = random.randint(1, 10)

	if options.has_key('user'):
		username = options['user']
		if users.filter(username=username).exists():
			user = users.get(username=username)

	if options.has_key('num'):
		num = options['num']

	order = Order(user=user)
	order.save()

	django_rq.enqueue(fill_order, order.id, int(num))	

	return order.id


class Command(BaseCommand):
	help = 'Generates a random order for a random or given user'

	def add_arguments(self, parser):
		parser.add_argument('user', type=str)
		parser.add_argument('num', type=int)

	def handle(self, *args, **options):
		return str(create_random_order(**options))

		
		 