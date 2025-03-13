from django import forms
from django.forms import ModelForm

from apps.devices.models import Device, KasaSwitch, Fridge

class DeviceForm(ModelForm):
  kasa_ipv4 = forms.GenericIPAddressField(required=False, label='kasa_ipv4')
  
  class Meta:
    model = Device
    fields = ['name', 'description', 'type', 'status', 'critical_load', 'adr_enabled']

class DeviceUpdateForm(forms.ModelForm):
  kasa_ipv4 = forms.GenericIPAddressField(required=False, label="IPv4 Address")

  class Meta:
    model = Device
    fields = ['name', 'type', 'description', 'status', 'critical_load', 'adr_enabled', 'on_window_begin', 'on_window_end', 'off_window_begin', 'off_window_end']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Hide IPv4 field unless it's a KasaSwitch
    if self.instance and self.instance.type != 'kasa_switch':
        self.fields.pop('ipv4', None)