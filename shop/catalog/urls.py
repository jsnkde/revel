from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'catalog'

urlpatterns = [
    url(r'^$', views.ItemList.as_view(), name='index'),
    url(r'^login$', views.SigninView.as_view(), name='signin'),
    url(r'^logout$', views.SignoutView.as_view(), name='signout'),
    url(r'^user/(?P<pk>[0-9]+)$', views.ProfileView.as_view(), name='profile'),
    url(r'^register$', views.Registration.as_view(), name='register'),
    url(r'^item/(?P<pk>[0-9]+)$', login_required(views.ItemDetail.as_view()), name='detail'),
	url(r'^cart$', views.CartView.as_view(), name='cart'),   
	url(r'^orders$', views.OrderView.as_view(), name='orders'), 
]