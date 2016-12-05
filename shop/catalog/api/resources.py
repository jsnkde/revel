from tastypie.resources import ModelResource, Resource
from catalog.models import Item, Review, UserConfirmationHash, Order, OrderItem
from tastypie import fields
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication, MultiAuthentication, SessionAuthentication, Authentication
from django.contrib.auth.models import User
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.db.models import signals, Avg, Sum
from django.db import IntegrityError
from tastypie.models import create_api_key
from tastypie.models import ApiKey
from tastypie.validation import FormValidation
from catalog.forms import ReviewForm
from datetime import datetime
from uuid import uuid4
from django.core.mail import send_mail
from django.conf import settings
from catalog.management.commands import randomorder


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
        return object_list.filter(username=bundle.request.user, is_active=True)


class CreateUserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()        
        resource_name = 'create_user'
        allowed_methods = ['post', 'patch', 'put',]
        fields = ['username', 'email', 'password']
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        bundle = super(CreateUserResource, self).obj_create(bundle, request=request, **kwargs)
        bundle.obj.set_password(bundle.data.get('password'))
        bundle.obj.is_active = False
        bundle.obj.save()
        
        hash = uuid4().hex
        UserConfirmationHash(user=bundle.obj, hash=hash).save()
        msg = 'To confirm registration go to http://%s/#confirm?id=%s&hash=%s' % (bundle.request.META['HTTP_HOST'], bundle.obj.id, hash)
        send_mail('Confirm Registration', msg, settings.DEFAULT_FROM_EMAIL, [bundle.obj.email,], fail_silently=False)

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        uch = UserConfirmationHash.objects.filter(user=bundle.obj)
        if uch.exists() and uch[0].hash == bundle.data['hash']:
            bundle.obj.is_active = True
            bundle.obj.save()

        return bundle

    def dehydrate(self, bundle):
        bundle.data['email'] = ''
        bundle.data['password'] = ''
        bundle.data['username'] = ''

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
        queryset = Item.objects.all().order_by('name')
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


class OrderAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

class OrderItemResource(ModelResource):
    class Meta:
        resource_name = "order_item"
        authorization = Authorization()
        authentication = MultiAuthentication(BasicAuthentication(), ApiKeyAuthentication())
        allowed_methods = ['get']
        fields = ['name', 'price', 'total_price', 'id']
        queryset = OrderItem.objects.all()

    def dehydrate(self, bundle):   
        bundle.data['name'] = bundle.obj
        bundle.data['price'] = bundle.obj.item.price
        bundle.data['id'] = bundle.obj.item.id
        bundle.data['oid'] = bundle.obj.id
        return bundle    


class OrderResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    items = fields.ToManyField(OrderItemResource, 'items', full=True)

    class Meta:
        resource_name = 'order'
        authorization = OrderAuthorization()
        authentication = MultiAuthentication(BasicAuthentication(), ApiKeyAuthentication())
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'patch', 'put']
        queryset = Order.objects.all().order_by('-id').select_related()
        always_return_data = True

    def dehydrate(self, bundle):
        if bundle.obj.items.exists():
            bundle.data['items'] = sorted(bundle.data['items'],key=lambda x: x.data['price'])
            bundle.data['total_price'] = reduce(lambda res, x: x + res, [i.data['price'] for i in bundle.data['items']])

        return bundle

    def dehydrate_created(self, bundle):
        return (bundle.data['created']).strftime('%H:%M %d.%m.%Y')

    def obj_update(self, bundle, request=None, **kwargs):
        print bundle.data
        if bundle.data.has_key('done') and bundle.data['done'] is True:
            bundle.obj.done = True
            bundle.obj.save()

        if bundle.data.has_key('del'):
            bundle.obj.items.get(id=bundle.data['del']).delete()

        if bundle.data.has_key('add'):
            it = Item.objects.get(id=bundle.data['add'])
            oi = OrderItem.objects.create(item=it)
            oi.save()
            bundle.obj.items.add(oi)

        if not bundle.obj.items.exists():
            pass

        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        obj = super(OrderResource, self).obj_create(bundle, request=request, user=bundle.request.user, **kwargs)
        return bundle

    def save_m2m(self, bundle):
        print "save_m2m"
        pass

    def hydrate_m2m(self, bundle):
        print "hydrate_m2m"
        pass

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(done=True)

    def authorized_read_detail(self, object_list, bundle):
        return object_list


class CartResource(OrderResource):
    class Meta:
        resource_name = 'cart'
        authorization = OrderAuthorization()
        authentication = MultiAuthentication(BasicAuthentication(), ApiKeyAuthentication())
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'put']
        queryset = Order.objects.filter().order_by('-id').select_related()
        always_return_data = True

    def authorized_read_list(self, object_list, bundle):
        return object_list

    def authorized_read_detail(self, object_list, bundle):
        return object_list

    def obj_update(self, bundle, request=None, **kwargs):
        if bundle.data.has_key('del'):
            bundle.obj.items.get(id=bundle.data['del']).delete()

        if not bundle.obj.items.exists():
            pass

        return bundle


class CommandObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class CommandResource(Resource):
    order_id = fields.IntegerField(attribute='order_id')

    class Meta:
        resource_name = 'command'
        authorization = Authorization()
        authentication = MultiAuthentication(BasicAuthentication(), ApiKeyAuthentication())
        allowed_methods = ['get']
        object_class = CommandObject

    def detail_uri_kwargs(self, bundle_or_obj):
        return {}

    def get_object_list(self, request):
        return []

    def obj_get_list(self, bundle, **kwargs):
        cmd = CommandObject() 
        cmd.order_id = randomorder.create_random_order(user=bundle.request.user.username)
        return [cmd]

    def obj_get(self, bundle, **kwargs):
        cmd = CommandObject() 
        cmd.order_id = randomorder.create_random_order(user=bundle.request.user.username, num=kwargs['pk'])
        return cmd

