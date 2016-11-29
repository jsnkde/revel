from tastypie.resources import ModelResource, Resource
from catalog.models import Item, Review
from tastypie import fields
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication, MultiAuthentication, SessionAuthentication, Authentication
from django.contrib.auth.models import User
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.db.models import signals, Avg
from django.db import IntegrityError
from tastypie.models import create_api_key
from tastypie.models import ApiKey
from tastypie.validation import FormValidation
from catalog.forms import ReviewForm
from datetime import datetime

signals.post_save.connect(create_api_key, sender=User)


class RevelAuthorization(DjangoAuthorization):
    def read_detail(self, object, bundle):
        return bundle.obj == bundle.request.user


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username',]
        authentication = MultiAuthentication(BasicAuthentication(), ApiKeyAuthentication())
        authorization = RevelAuthorization()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]

    def dehydrate(self, bundle):
        bundle.data['key'] = ApiKey.objects.get(user_id=bundle.obj.id).key
        return bundle

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(username=bundle.request.user)

class CreateUserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()        
        resource_name = 'create_user'
        allowed_methods = ['post',]
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = super(CreateUserResource, self).obj_create(bundle, request=request, **kwargs)
        bundle.obj.set_password(bundle.data.get('password'))
        bundle.obj.save()

        return bundle


class ReviewResource(ModelResource):
    #item = fields.ForeignKey('catalog.ItemResource', 'item')

    class Meta:
        queryset = Review.objects.all()
        resource_name = 'review'
        allowed_methods = ['get', 'post']
        filtering = {'name': ALL, 'rating': ALL, }
        validation = FormValidation(form_class=ReviewForm)
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        always_return_data = True
        ordering = ['created']

    def obj_create(self, bundle, request=None, **kwargs):
        item = Item.objects.get(id=bundle.data['item'])
        bundle.obj = Review(item=item, name=bundle.data['name'], rating=bundle.data['rating'], text=bundle.data['text'])        
        bundle.obj.save()

        return bundle

    def dehydrate_created(self, bundle):
        return (bundle.data['created']).strftime('%H:%M %d.%m.%Y')


class ItemResource(ModelResource):
    reviews = fields.ToManyField(ReviewResource, 'review_set', full=True)

    class Meta:
        queryset = Item.objects.all()
        allowed_methods = ['get']
        resource_name = 'item'
        authentication = Authentication()
        authorization = Authorization()
        excludes = ['updated', 'created', 'image', 'description']

    def dehydrate(self, bundle):
        bundle.data['rating'] = Review.objects.filter(item=bundle.obj.id).aggregate(Avg('rating'))['rating__avg']
        return bundle

    def dehydrate_name(self, bundle):
        return bundle.data['name'].upper()

    def hydrate_name(self, bundle):
        bundle.data['name'] = bundle.data['name'].lower()
        return bundle

