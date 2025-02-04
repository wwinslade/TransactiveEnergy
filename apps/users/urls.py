from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
  path('', RedirectView.as_view(url='login/', permanent=False), name='login'),
  path('login/', views.loginUserPage, name='login'),
  path('register/', views.registerUserPage, name='register'),
  path('logout/', views.logoutUser, name='logout'),
]