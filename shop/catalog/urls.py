from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'catalog'

urlpatterns = [
    #url(r'^$', views.index, name='index'),
    url(r'^$', views.ItemList.as_view(), name='index'),
    url(r'^login$', views.SigninView.as_view(), name='signin'),
    url(r'^logout$', views.signout, name='signout'),
    url(r'^user/(?P<pk>[0-9]+)$', views.ProfileView.as_view(), name='profile'),
    url(r'^user', views.profile, name='profile'),
    #url(r'^register$', views.register, name='register'),
    url(r'^register$', views.Registration.as_view(), name='register'),
    #url(r'^(?P<item_id>[0-9]+)/$', views.item, name='item'),
    url(r'^item/(?P<pk>[0-9]+)$', login_required(views.ItemDetail.as_view()), name='detail'),
]