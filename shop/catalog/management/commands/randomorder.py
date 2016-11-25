from django.core.management.base import BaseCommand, CommandError
from catalog.models import Order, OrderItem, Item
from django.contrib.auth.models import User
import string
import random


class Command(BaseCommand):
	help = 'Generates a random order for a random or given user'

	def add_arguments(self, parser):
		parser.add_argument('user', type=str)

	def handle(self, *args, **options):
		users = User.objects.all()
		items = Item.objects.all()

		if not users.exists():
			raise Exception('No users exist')

		if not items.exists():
			raise Exception('No items exist')

		user = users[random.randint(0, users.count() - 1)]

		if options.has_key('user'):
			username = options['user']
			if users.filter(username=username).exists():
				user = users.get(username=username)

		order = Order(user=user)
		order.save()
		print "Order for", user

		# Up to 10 items in an order
		for i in range(0, random.randint(1, 10)):
			it = items[random.randint(0, items.count() - 1)]
			print "\t", it.name, it.price, it.currency.ticker
			order_item = OrderItem(item=it)
			order_item.save()
			order.items.add(order_item)

		
		 