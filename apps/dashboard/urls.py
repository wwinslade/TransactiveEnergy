from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('dashboard/', views.dashboard, name='dashboard'),
  path('dashboard/update/', views.update_dashboard_state, name='update_dashboard_state'),
  path('operator/', views.admin, name='admin'),
  path('operator/new_device', views.CreateNewDevice, name='new_device'),
  path('operator/update_device/<str:pk>', views.UpdateDevice, name='update_device'),
  path('webcam/feed/', views.WebcamStreamTest, name='webcam_feed'),
  path('webcam/stream/', views.WebcamStreamTestPage, name='webcam_stream'),
]