from django.contrib import admin
from models import Category, Page
# this file tells the Django admin application what models we wish to make available to the admin interface
# in above there is a correction it shouldn't be import rango.models as models and admin file are in same folder
admin.site.register(Category)
admin.site.register(Page)