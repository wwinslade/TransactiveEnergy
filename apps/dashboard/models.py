from django.db import models

# Create your models here.
class Device(models.Model):
  name = models.CharField(max_length=100, default='New Device')
  description = models.TextField(null=True, blank=True)
  device_type = models.CharField(max_length=50, default='Unknown')
  status = models.BooleanField(default=False)
  ipv4 = models.GenericIPAddressField(null=True, blank=True)
  sync_or_async = models.CharField(max_length=10, default='sync')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f'{self.device_type}.{self.name}'