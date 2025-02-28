from django.urls import path

from . import views

urlpatterns = [
  path('kasa_switch/<str:uuid>/on', views.KasaSwitchOn, name='kasa_switch_on'),
  path('kasa_switch/<str:uuid>/off', views.KasaSwitchOff, name='kasa_switch_off'),
  path('fridge/<str:uuid>/on', views.FridgeOn, name='fridge_on'),
  path('fridge/<str:uuid>/off', views.FridgeOff, name='fridge_off'),
  path('iotawatt/query/', views.QueryIotaWatt, name='iotawatt_query'),
]
