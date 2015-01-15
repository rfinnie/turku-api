from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'^update_config$', views.update_config, name='update_config'),
)

