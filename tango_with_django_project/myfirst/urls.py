__author__ = 'Paul G Mathew'
from django.conf.urls import url,patterns
from myfirst import views

urlpatterns = patterns('',
url(r'^$',views.first,name = 'first'))