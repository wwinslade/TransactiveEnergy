from django.urls import path

from . import views

urlpatterns = [
  path('kasa_switch/<str:uuid>/on', views.KasaSwitchOn, name='kasa_switch_on'),
  path('kasa_switch/<str:uuid>/off', views.KasaSwitchOff, name='kasa_switch_off'),
]
