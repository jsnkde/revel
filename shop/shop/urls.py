"""shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from tastypie.api import Api
from catalog.api.resources import ItemResource, ReviewResource, UserResource
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Pastebin API')

v1_api = Api(api_name='v1')
v1_api.register(ItemResource())
v1_api.register(ReviewResource())
v1_api.register(UserResource())

urlpatterns = [
    url(r'^doc/$', schema_view),
	url(r'^', include('catalog.urls')),
    url(r'^admin/', admin.site.urls),
    #url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^api/', include(v1_api.urls)),
]



urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
