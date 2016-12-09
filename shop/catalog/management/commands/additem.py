from django.core.management.base import BaseCommand, CommandError
from catalog.models import Currency, Item, Category
import string
import random
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
	help = 'Adds new item to the inventory'

	def add_arguments(self, parser):
		parser.add_argument('quantity', type=int)

	def handle(self, *args, **options):
		quantity = options['quantity'] if options.has_key('quantity') else 1

		try:
			cur = Currency.objects.get(name="Dollar")
			cat = Category.objects.get(name="Smartphone")

		except ObjectDoesNotExist:
			return

		bulk_list = []
		for i in range(quantity):
			n = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
			bulk_list.append(Item(name=n, currency=cur, category=cat, price=100))
			
		Item.objects.bulk_create(bulk_list)

