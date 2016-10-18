from django.conf.urls import url

from . import views

app_name = 'catalog'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<item_id>[0-9]+)/$', views.item, name='item'),
    url(r'^(?P<pk>[0-9]+)/details/$', views.DetailView.as_view(), name='detail'),
]