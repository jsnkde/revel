from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import re

class ReviewForm(forms.Form):
	RATING = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),)

	name = forms.CharField(max_length=100, required=False)
	rating = forms.ChoiceField(widget=forms.Select(), choices=RATING)
	comment = forms.CharField(max_length=1000, widget=forms.Textarea(), required=False)

class SigninForm(forms.Form):
	name = forms.CharField(max_length=100)
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super(SigninForm, self).clean()

		password = self.cleaned_data['password']		
		name = self.cleaned_data['name']

		if User.objects.filter(username=name).count() == 0:
			raise forms.ValidationError(u'No user with this name exists')

		p = re.compile('\d')
		if p.search(password) is None:
			raise forms.ValidationError(u'Password does not contain numbers')

		if authenticate(username=name, password=password) is None:
			raise forms.ValidationError(u'Password is incorrect')

class SignupForm(forms.Form):
	username = forms.CharField(max_length=100)
	#first_name = forms.CharField(max_length=100)
	#last_name = forms.CharField(max_length=100)
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)

	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username=username).count() > 0:
			raise forms.ValidationError(u'Username already in use')

		return username
