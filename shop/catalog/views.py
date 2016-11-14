# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.template import RequestContext
from django.db.models import Avg, Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

from .models import Item, Review, Accessory, Currency
from .forms import ReviewForm, SigninForm, SignupForm

@login_required
def index(request):
	items = Item.objects.all()
	template = loader.get_template('catalog/index.html')
	context = {'items': items,}

	return render(request, 'catalog/index.html', context)

def item(request, item_id):	
	if request.method == 'POST':
		rform = ReviewForm(request.POST)
		if rform.is_valid():
			item = Item.objects.filter(id=item_id)[0]
			name = rform.cleaned_data['name']
			rating = rform.cleaned_data['rating']
			comment = rform.cleaned_data['comment']

			Review(item=item, name=name, text=comment, rating=rating).save()

			return HttpResponseRedirect(reverse('catalog:item', args=(item.id,)))

	else:
		item = get_object_or_404(Item, pk=item_id)
		reviews = Review.objects.filter(item=item_id)
		avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
		if avg_rating is  None:
			avg_rating = 0
		else:
			avg_rating = "{0:.2f}".format(reviews.aggregate(Avg('rating'))['rating__avg'])
		review_title = "Write your own review"
		review_form = ReviewForm()

		currencies = Currency.objects.all()
		accessories_prices = []
		for cur in currencies:
			ac_total = item.accessories.filter(currency=cur).aggregate(Sum('price'))['price__sum']
			
			if ac_total is not None:
				accessories_prices.append("%d %s" % (ac_total, cur.ticker))

		return render(request, 'catalog/item.html', {'item': item, 'reviews': reviews, 'accessories_prices': accessories_prices, 'review_form': review_form, 'avg_rating': avg_rating, })

def signin(request):
	if request.method == 'POST':
		lform = SigninForm(request.POST)
		if lform.is_valid():
			user = authenticate(username=lform.cleaned_data['name'], password=lform.cleaned_data['password'])
			if user is not None:
				login(request, user)

		return HttpResponseRedirect(reverse('catalog:index'))

	else:
		lform = SigninForm()

		return render(request, 'catalog/login.html', {'lform': lform, })

def signout(request):
	logout(request)
	return HttpResponseRedirect(reverse('catalog:signin'))

class DetailView(generic.DetailView):
	model = Item
	template_name='catalog/item.html'

def profile(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render(request, 'catalog/profile.html', {'user': user,})

def register(request):
	if request.method == 'POST':
		regform = SignupForm(request.POST)
		
		if regform.is_valid():
			username = regform.cleaned_data['username']
			first_name = regform.cleaned_data['first_name']
			last_name = regform.cleaned_data['last_name']
			email = regform.cleaned_data['email']
			password = regform.cleaned_data['password']
			
			User(username=username, first_name=first_name, last_name=last_name, email=email, password=password).save()
			send_mail('Successful Registration', 'You are successfuly registered in our internet shop.', 'jsnk@yandex.ru', [email,], fail_silently=False)

			return HttpResponseRedirect(reverse('catalog:index'))

		else:
			return render(request, 'catalog/registration.html', {'regform': regform,})

	else:
		regform = SignupForm()
		return render(request, 'catalog/registration.html', {'regform': regform,})



