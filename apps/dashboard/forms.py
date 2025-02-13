from django.forms import ModelForm

from apps.devices.models import Device

class DeviceForm(ModelForm):
  class Meta:
    model = Device
    fields = ['name', 'description', 'type', 'status', ]