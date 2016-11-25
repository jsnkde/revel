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
from django.core.exceptions import ObjectDoesNotExist

from .models import Item, Review, Accessory, Currency, A, B, Order, OrderItem
from .forms import ReviewForm, SigninForm, SignupForm
from django.conf.urls import url
from django.db import connection, DatabaseError
from datetime import date, timedelta


class JSView(generic.TemplateView):
	template_name = 'catalog/js_index.html'


class ItemDisplay(generic.DetailView):
	model = Item
	template_name='catalog/item.html'
	context_object_name = 'item'

	def get(self, request, *args, **kwargs):
		if request.GET.has_key('add') and request.GET['add'] == 'true':
			if request.session.has_key('order') and Order.objects.filter(id=request.session['order']).exists():
				order = Order.objects.get(id=request.session['order'])

			else:
				order = Order(user=request.user)
				order.save()
				request.session['order'] = order.id

			oitem = OrderItem(item=self.get_object())
			oitem.save()
			order.items.add(oitem)
			order.save()

		return super(ItemDisplay, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(ItemDisplay, self).get_context_data(**kwargs)
		reviews = Review.objects.filter(item=self.get_object().id)
		context['reviews'] = reviews
		context['form'] = ReviewForm(initial={'name': self.request.user.username})

		avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
		context['avg_rating'] = 0 if avg_rating is None else "{0:.2f}".format(reviews.aggregate(Avg('rating'))['rating__avg'])

		currencies = Currency.objects.all()
		accessories_prices = []
		for cur in currencies:
			ac_total = self.object.accessories.filter(currency=cur).aggregate(Sum('price'))['price__sum']
			
			if ac_total is not None:
				accessories_prices.append("%d %s" % (ac_total, cur.ticker))

		context['accessories_prices'] = accessories_prices

		if self.request.session.has_key('order'):
			context['cart'] = True

		return context


class ReviewView(generic.edit.CreateView):
	template_name = 'catalog/item.html'
	model = Review
	form_class = ReviewForm

	def form_valid(self, form):
		review = form.save(commit=False)
		review.item = Item.objects.get(id=self.kwargs['pk'])
		return super(ReviewView, self).form_valid(form)

	def get_success_url(self):
		return reverse('catalog:detail', kwargs={'pk': self.kwargs['pk']})


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


class Registration(generic.edit.CreateView):
	form_class = SignupForm
	template_name = 'catalog/registration.html'
	model = User

	def get_success_url(self):
		return reverse('catalog:index')

	def form_valid(self, form):
		u = form.save()
		login(self.request, u)
		#send_mail('Successful Registration', 'You are successfuly registered in our internet shop.', 'jsnk@yandex.ru', [email,], fail_silently=False)
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

class SignoutView(generic.base.RedirectView):
	def get_redirect_url(self):
		logout(self.request)
		return (reverse('catalog:signin'))


class ProfileView(generic.DetailView):
	model = User
	template_name = 'catalog/profile.html'
	context_object_name = 'user'


class CartView(View):
	def get(self, request):
		if not request.session.has_key('order'):
			return render(request, 'catalog/cart.html', {'order': None}) 

		if not Order.objects.filter(id=request.session['order']).exists():
			return render(request, 'catalog/cart.html', {'order': None}) 

		order = Order.objects.get(id=request.session['order'])

		if request.GET.has_key('close'):
			order.done = True
			order.save()
			del request.session['order']

			return redirect(reverse('catalog:index'))

		if request.GET.has_key('delete'):
			try:
				order.items.get(id=request.GET['delete']).delete()

			except ObjectDoesNotExist:
				pass

			if not order.items.exists():
				order = None
				del request.session['order']

		return render(request, 'catalog/cart.html', {'order': order})


class OrderView(View):
	def get(self, request):
		# Default parameters
		begin = str(date.today() - timedelta(days=1))
		end = str(date.today())
		step = 1

		if request.GET.has_key('begin'):
			begin = request.GET['begin']

		if request.GET.has_key('end'):
			end = request.GET['end']

		try:
			if request.GET.has_key('step'):
				step = int(request.GET['step'])

		except ValueError:
			pass

		try:
			cur = connection.cursor()
			cur.callproc('get_orders', [begin, end, step])
			orders = cur.fetchall()
			cur.close()

		except DatabaseError:
			orders = []

		return render(request, 'catalog/orders.html', {'orders': orders, 'begin': begin, 'end': end, 'step': step})



