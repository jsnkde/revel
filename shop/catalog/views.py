# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.template import RequestContext

from .models import Item, Review

def index(request):
	items = Item.objects.all()
	template = loader.get_template('catalog/index.html')
	context = {'items': items,}

	return render(request, 'catalog/index.html', context)

def item(request, item_id):	
	if len(request.POST) > 0 and request.POST.has_key('rating'):
		item = Item.objects.filter(id=item_id)[0]
		Review(item=item, name=request.POST['name'], text=request.POST['text'], rating=request.POST["rating"]).save()

		return HttpResponseRedirect(reverse('catalog:item', args=(item.id,)))

	else:
		item = get_object_or_404(Item, pk=item_id)
		reviews = Review.objects.filter(item=item_id)
		review_title = "Write your own review"

		return render(request, 'catalog/item.html', {'item': item, 'reviews': reviews, })

class DetailView(generic.DetailView):
	model = Item
	template_name='catalog/item.html'


