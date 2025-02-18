from django import forms
from django.forms import ModelForm

from apps.devices.models import Device, KasaSwitch, Fridge

class DeviceForm(ModelForm):
  kasa_ipv4 = forms.GenericIPAddressField(required=False, label='kasa_ipv4')
  
  class Meta:
    model = Device
    fields = ['name', 'description', 'type', 'status']
