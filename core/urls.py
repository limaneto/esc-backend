from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('generate/', views.generate),
]
