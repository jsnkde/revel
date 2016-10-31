# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from django.template import RequestContext
from django.db.models import Avg, Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

from .models import Item, Review, Accessory, Currency, A, B
from .forms import ReviewForm, SigninForm, SignupForm

def index(request):
	items = Item.objects.all()
	template = loader.get_template('catalog/index.html')
	context = {'items': items,}

	#aa = A.objects.all()
	#print "SQL", aa.query
	#import pdb; pdb.set_trace()
	#print aa[0].name

	return render(request, 'catalog/index.html', context)

@login_required
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
		review_form = ReviewForm(initial={'name': request.user.username})

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

				if request.GET.has_key('next'):
					return redirect(request.GET['next'])

		
		return HttpResponseRedirect(reverse('catalog:index'))

	else:
		lform = SigninForm()

		return render(request, 'catalog/login.html', {'lform': lform, })

def signout(request):
	logout(request)
	return HttpResponseRedirect(reverse('catalog:signin'))

def profile(request, user_id=1):
	if request.method == 'GET' and request.GET.has_key('id'):
		user_id = request.GET['id']

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
			
			u = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
			u.save()
			send_mail('Successful Registration', 'You are successfuly registered in our internet shop.', 'jsnk@yandex.ru', [email,], fail_silently=False)
			login(request, u)

			return HttpResponseRedirect(reverse('catalog:index'))

		else:
			return render(request, 'catalog/registration.html', {'regform': regform,})

	else:
		regform = SignupForm()
		return render(request, 'catalog/registration.html', {'regform': regform,})


class ItemDisplay(generic.DetailView):
	model = Item
	template_name='catalog/item.html'
	context_object_name = 'item'

	def get_context_data(self, **kwargs):
		context = super(ItemDisplay, self).get_context_data(**kwargs)
		context['reviews'] = Review.objects.filter(item=self.get_object().id)
		context['form'] = ReviewForm(initial={'name': self.request.user.username})

		return context

class ReviewView(generic.detail.SingleObjectMixin, generic.FormView):
	template_name = 'catalog/item.html'
	form_class = ReviewForm
	model = Review

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()
		if form.is_valid():
			review = Review(name=form.cleaned_data['name'], rating=form.cleaned_data['rating'], text=form.cleaned_data['comment'], item=Item.objects.get(id=kwargs['pk']))
			review.save()
			self.object = review
		return super(ReviewView, self).post(request, *args, **kwargs)

	def get_success_url(self):
		return reverse('catalog:detail', kwargs={'pk': self.object.item_id})

class ItemDetail(View):
	def get(self, request, *args, **kwargs):
		view = ItemDisplay.as_view()			
		return view(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		view = ReviewView.as_view()
		return view(request, *args, **kwargs)

class ItemList(generic.ListView):
	model = Item
	template_name = 'catalog/index.html'
	context_object_name = 'items'

class Registration(generic.FormView):
	form_class = SignupForm
	template_name = 'catalog/registration.html'

	def get_success_url(self):
		return reverse('catalog:index')

	def form_valid(self, form):
		u = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
		u.save()
		login(self.request, u)

		return super(Registration, self).form_valid(form)

class SigninView(generic.FormView):
	template_name = 'catalog/login.html'
	form_class = SigninForm

	def get_success_url(self):
		if self.request.GET.has_key('next'):
			return self.request.GET['next']

		return reverse('catalog:index')

	def form_valid(self, form):
		user = authenticate(username=form.cleaned_data['name'], password=form.cleaned_data['password'])
		if user is not None:
			login(self.request, user)

		return super(SigninView, self).form_valid(form)

class ProfileView(generic.DetailView):
	model = User
	template_name = 'catalog/profile.html'
	context_object_name = 'user'

	def get_context_data(self, **kwargs):
		context = super(ProfileView, self).get_context_data(**kwargs)
		self.object = User.objects.get(id=self.get_object().pk)

		return context
