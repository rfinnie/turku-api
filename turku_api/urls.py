from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'turku_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^v1/', include('api.urls', namespace="api")),
    url(r'^admin/', include(admin.site.urls)),
)
