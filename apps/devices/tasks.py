from apps.devices.models import Device, KasaSwitch, Fridge, EnergyConsumption

from celery import shared_task
import requests

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def query_iotawatt(query_range, sample_interval):
  '''
  Queries IotaWatt device for energy consumption data at a given time interval and sample interval.
  query_range: Tuple of start and end timestamps for the query, must be in ISO relative time format
  sample_interval: Time interval for sampling the data, must be in ISO format

  For more time format information: https://docs.iotawatt.com/en/master/query.html#relative-time
  '''
  url = f'http://192.168.0.111/query?select=[time.iso,input_0,Meter1,Solar]&begin={query_range[0]}&end={query_range[1]}&group={sample_interval}&format=json&header=yes'
  response = requests.get(url)
  if response.status_code != 200:
    logger.error(f'Failed to fetch data from IotaWatt: {response.status_code}')
    return None

  times = response.json().get('range', [])
  times = [datetime.fromtimestamp(time) for time in times]
  
  labels = response.json().get('labels', [])
  data = response.json().get('data', [])

  print(f'IotaWatt Data fetched for {sample_interval} interval from {times[0]} to {times[-1]}')

  # Save the data to the EnergyConsumption model
  for d in data:
    for i, label in enumerate(labels[2:], start=2):
      EnergyConsumption.objects.create(
        timestamp=times[i],
        device_name=label,
        consumption=d[i]
      )

  logger.info(f'Energy consumption data saved to DB for {sample_interval} interval from {times[0]} to {times[-1]}')

if __name__ == "__main__":
  # Example usage
  query_range = ('d-1d', 'd')
  sample_interval = '10m'
  query_iotawatt(query_range, sample_interval)