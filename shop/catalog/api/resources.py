from tastypie.resources import ModelResource
from catalog.models import Item, Review
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication, SessionAuthentication
from django.contrib.auth.models import User
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.db.models import signals
from tastypie.models import create_api_key
from tastypie.validation import FormValidation
from catalog.forms import ReviewForm

signals.post_save.connect(create_api_key, sender=User)


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = ApiKeyAuthentication()


class ItemResource(ModelResource):
    class Meta:
        queryset = Item.objects.all()
        allowed_methods = ['get']
        resource_name = 'item'
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        excludes = ['updated', 'created', 'id', 'image', 'description']

    def dehydrate_name(self, bundle):
    	return bundle.data['name'].upper()

	def hydrate_name(self, bundle):
		bundle.data['name'] = bundle.data['name'].lower()
		return bundle


class ReviewResource(ModelResource):
	item = fields.ForeignKey(ItemResource, 'item', full=True)

	class Meta:
		queryset = Review.objects.all()
		resource_name = 'review'
		filtering = {'name': ALL, 'rating': ALL, }
		validation = FormValidation(form_class=ReviewForm)
		authentication = SessionAuthentication()
