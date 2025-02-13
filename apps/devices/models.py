from django.db import models
import uuid

# Create your models here.

# Generic model for a device -- can be extended to include more specific device types
class Device(models.Model):
  DEVICE_TYPES = [
    ('generic', 'Generic Device'),
    ('kasa_switch', 'Kasa Switch'),
    ('fridge', 'Fridge'),
  ]

  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100, default='NewGenericDevice', null=True, blank=True)
  type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='generic')
  description = models.TextField(null=True, blank=True)
  status = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f'{self.uuid}.{self.type}.{self.name}'

# Model for KasaSwitches
class KasaSwitch(models.Model):
  device = models.OneToOneField(Device, on_delete=models.CASCADE, primary_key=True)
  ip_address = models.GenericIPAddressField()

  def __str__(self):
    return f'{self.device.uuid}.{self.device.type}.{self.device.name}'
  
# Model for the fridge
class Fridge(models.Model):
  device = models.OneToOneField(Device, on_delete=models.CASCADE, primary_key=True)
  high_temp_threshold = models.FloatField(default=50.0)
  low_temp_threshold = models.FloatField(default=20.0)
  target_temp_threshold = models.FloatField(default=38.0)

  def __str__(self):
    return f'{self.device.uuid}.{self.device.type}.{self.device.name}'
