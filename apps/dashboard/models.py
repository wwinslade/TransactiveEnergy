from django.db import models

# Create your models here.
class ComedPriceData(models.Model):
  timestamp = models.DateTimeField(primary_key=True, unique=True)
  price = models.FloatField(default=0.0)

  def __str__(self):
    return f'ComEd: {self.timestamp} - {self.price} / kWh'
  
class UbibotSensorTemp(models.Model):
  timestamp = models.DateTimeField(primary_key=True, unique=True)
  temp = models.FloatField(default=-1.0)

  def __str__(self):
    return f'TempSensor: {self.timestamp} - {self.temp} deg F'