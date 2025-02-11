from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('operator/', views.admin, name='admin'),
  path('operator/new_device', views.CreateNewDevice, name='new_device'),
  path('operator/update_device/<str:pk>', views.UpdateDevice, name='update_device'),
]