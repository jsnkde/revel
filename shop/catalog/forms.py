from django import forms

class ReviewForm(forms.Form):
	RATING = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),)

	name = forms.CharField(max_length=100, required=False)
	rating = forms.ChoiceField(widget=forms.Select(), choices=RATING)
	comment = forms.CharField(max_length=1000, widget=forms.Textarea(), required=False)