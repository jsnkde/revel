from django.core.management.base import BaseCommand, CommandError
from catalog.models import Currency, Item, Category
import string
import random

class Command(BaseCommand):
	help = 'Adds new item to the inventory'

	def add_arguments(self, parser):
		parser.add_argument('quantity', type=int)

	def handle(self, *args, **options):
		if options.has_key('quantity'):
			quantity = options['quantity']

		else:
			quantity = 1

		cur = Currency.objects.get(name="Dollar")
		cat = Category.objects.get(name="Smartphone	")

		for i in range(quantity):
			n = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
			it = Item(name=n, currency=cur, category=cat, price=100)
			it.save()

