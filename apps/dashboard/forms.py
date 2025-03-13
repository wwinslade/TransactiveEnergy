from django import forms
from django.forms import ModelForm

from apps.devices.models import Device, KasaSwitch, Fridge

class DeviceForm(ModelForm):
  kasa_ipv4 = forms.GenericIPAddressField(required=False, label='kasa_ipv4')
  
  class Meta:
    model = Device
    fields = ['name', 'description', 'type', 'status']

class DeviceUpdateForm(forms.ModelForm):
  kasa_ipv4 = forms.GenericIPAddressField(required=False, label="IPv4 Address")

  class Meta:
    model = Device
    fields = ['name', 'type', 'description', 'status']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Hide IPv4 field unless it's a KasaSwitch
    if self.instance and self.instance.type != 'kasa_switch':
        self.fields.pop('ipv4', None)