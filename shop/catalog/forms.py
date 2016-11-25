from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from catalog.models import Review
import re


class ReviewForm(forms.ModelForm):
	#RATING = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),)

	#name = forms.CharField(max_length=100, required=False)
	#rating = forms.ChoiceField(choices=RATING)
	#comment = forms.CharField(max_length=1000, widget=forms.Textarea(), required=False)

	class Meta:
		model = Review
		fields = ['name', 'rating', 'text']

	def clean_rating(self):
		rating = self.cleaned_data['rating']

		if rating < 1 or rating > 11:
			raise forms.ValidationError(u'Rating should be between 0 and 10 (or 11 if you are really stunned).')

		return rating


class SigninForm(forms.Form):
	name = forms.CharField(max_length=100)
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super(SigninForm, self).clean()

		password = self.cleaned_data['password']		
		name = self.cleaned_data['name']

		if not User.objects.filter(username=name).exists():
			raise forms.ValidationError(u'No user with this name exists')

		p = re.compile('\d')
		if p.search(password) is None:
			raise forms.ValidationError(u'Password does not contain numbers')

		if authenticate(username=name, password=password) is None:
			raise forms.ValidationError(u'Password is incorrect')


class SignupForm(forms.ModelForm):
	#username = forms.CharField(max_length=100)
	#first_name = forms.CharField(max_length=100)
	#last_name = forms.CharField(max_length=100)
	#email = forms.EmailField()
	#password = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ['username', 'email', 'password']
		widgets = {'password': forms.PasswordInput()}

	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError(u'Username already in use')

		return username
