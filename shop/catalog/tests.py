# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib import auth
import re


class AccessTest(TestCase):
	username = 'user'
	password = 'password'
	fixtures = ['catalog/fixtures/fixture1.json',]

	def setUp(self):
		self.user = User.objects.create_user(username=self.username, password=self.password)

	def test_login_logout(self):
		self.assertEqual(self.client.login(username=self.username, password=self.password), True)
		self.client.logout()
		user = auth.get_user(self.client)
		self.assertEqual(user.is_anonymous, True)

	def test_profile(self):
		self.assertEqual(self.client.login(username=self.username, password=self.password), True)

		response = self.client.get('/user/%d' % self.user.id)
		self.assertEqual(response.status_code, 200)

	def test_register(self):
		self.client.logout()
		response = self.client.post('/register', {'username': 'user2', 'password': 'pass', 'email': 'jdoe@gmail.com'})

		result = User.objects.filter(username='user2')
		self.assertNotEqual(len(result), 0)

	def test_main_logged(self):
		self.assertEqual(self.client.login(username=self.username, password=self.password), True)

		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)

		urls = re.findall(r'href=[\'"]?([^\'" >]+)', response.content)
		for url in urls:
			if url.find('item') >= 0:
				response = self.client.get(url)
				self.assertEqual(response.status_code, 200)



