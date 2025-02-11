from django.forms import ModelForm

from .models import Device

class DeviceForm(ModelForm):
  class Meta:
    model = Device
    fields = ['name', 'description', 'device_type', 'status', 'ipv4', 'sync_or_async']