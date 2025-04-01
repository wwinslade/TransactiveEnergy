from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from apps.devices.models import Device, KasaSwitch, Fridge
from apps.devices.views import estimate_remaining_time
from .forms import DeviceForm, DeviceUpdateForm

import cv2
from django.http import StreamingHttpResponse, JsonResponse

from django.db.models import OuterRef, Subquery, Value, CharField
from django.db.models.functions import Coalesce

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests
import json
from datetime import datetime, timedelta, timezone

from .models import ComedPriceData, UbibotSensorTemp

import os
import dotenv

from django.utils.timezone import now
from devices.views import total_time_minutes

# Create your views here.
def home(request):
  return render(request, 'home.html')

def fetch_comed_data(previous_days):
  ''' Fetch previous_days worth of 5-minute pricing data from ComEd (from now to now - previous_days). 
  Store the data in the db.sqlite db, delete any data older than now - current_days.

  Args:
    previous_days (int): number of previous days from now to get data for
  
  Returns:
    None: Performs query and stores data in DB  
  '''

  # Create datetime objects for window start and end
  end_date_obj = datetime.now(timezone.utc)
  begin_date_obj = datetime.now(timezone.utc) - timedelta(days=previous_days)

  # See if most recent entry is older than end of needed window
  query_end_date = end_date_obj.strftime('%Y%m%d%H%M')

  latest_entry = ComedPriceData.objects.latest('timestamp')

  # TODO: Check if we need to query ComEd at all, don't query if its not necessary

  if latest_entry.timestamp > begin_date_obj:
    query_begin_date = latest_entry.timestamp.strftime('%Y%m%d%H%M')
  else:
    query_begin_date = begin_date_obj.strftime('%Y%m%d%H%M')

  print(f'Querying comed from {query_begin_date} to {query_end_date}')

  url = f'https://hourlypricing.comed.com/api?type=5minutefeed&datestart={query_begin_date}&dateend={query_end_date}'
  response = requests.get(url)
  if response.status_code != 200:
    print('Unable to get pricing data from ComEd')
    return
  
  data = response.json()
  n_saved = 0
  for d in data:
    try:
      timestamp = datetime.fromtimestamp(int(d['millisUTC']) / 1000, timezone.utc)
    except (ValueError, TypeError):
      raise RuntimeError('Could not convert timestamp from comed')
    try:
      price = float(d['price'])
    except (ValueError, TypeError):
      price = -1.0

    new_db_obj = ComedPriceData(
      timestamp = timestamp,
      price = price
    )

    new_db_obj.save()
    n_saved += 1
  
  print(f'Saved {n_saved} new price data objects to DB')

  # Delete all entries with timestamp less than beginning of window
  num_deleted, _ = ComedPriceData.objects.filter(
    timestamp__lt=begin_date_obj
  ).delete()

  print(f'Deleted {num_deleted} ComedPriceData objects older than {begin_date_obj}')

def get_temp():
  ''' Get temperature reading from UbiBot sensor in the fridge

  Args:
    None
  Returns:
    None: Stores temp value in db.sqlite
  '''

  dotenv.load_dotenv()

  # Get secrets from env vars
  api_key = os.getenv('UBIBOT_API_KEY')
  api_channel = os.getenv('UBIBOT_CHANNEL')

  url = f'https://api.ubibot.com/channels/42895?account_key=54183910b6a04fd59648e022d58a1229'
  response = requests.get(url)

  if response != 200:
    print('Error fetching temperature from Ubibot API')
    return
  
  data = response.json()

  # Get temp from JSON. Temp value is in celcius
  temp = data['channel']['last_values']['field1']['value']
  temp = (temp * 9/5) + 32.0

  print(f'Fetched temp value of {temp} from UbiBot API')

  new_temp_obj = UbibotSensorTemp(
    temp = temp
  )

  new_temp_obj.save()

  return temp
  

def dashboard(request):
  weekly_load_url = f'http://192.168.0.111/query?select=[time.iso,input_0,Fridge,Solar,Recepticles]&begin=s-7d&end=s&group=15m&format=json&header=yes'
  response = requests.get(weekly_load_url)
  if response.status_code != 200:
    print('Error fetching weekly data from IotaWatt')
    return JsonResponse({'error': 'Error fetching weekly data from IotaWatt'}, status=500)
  
  weekly_data = response.json().get('data', [])

  if not weekly_data:
    print('No weekly data returned from IotaWatt')
    return JsonResponse({'error': 'Error fetching weekly data from IotaWatt'}, status=500)

  system_weekly_load = []
  weekly_load_labels = []

  for wd in weekly_data:
    date_obj = datetime.fromisoformat(wd[0])
    weekly_load_labels.append(date_obj.strftime('%d %b %Y'))

    try:
      fridge = float(wd[2])
    except (ValueError, TypeError):
      fridge = 0.0
    
    try:
      recepticles = float(wd[4])
    except (ValueError, TypeError):
      recepticles = 0.0

    system_weekly_load.append(fridge + recepticles)
  
  fetch_comed_data(3)

  weekly_price_labels = []
  weekly_price_data = []

  comed_price_objects = ComedPriceData.objects.filter(
    timestamp__gt=datetime.now(timezone.utc) - timedelta(days=3)
  )

  for cpo in comed_price_objects:
    weekly_price_labels.append(cpo.timestamp.strftime('%d %b %y - %H:%S'))
    weekly_price_data.append(cpo.price)

  context = {
    'weeklyLoadLabels': json.dumps(weekly_load_labels),
    'weeklyLoadData': json.dumps(system_weekly_load),
    'weeklyPriceLabels': json.dumps(weekly_price_labels),
    'weeklyPriceData': json.dumps(weekly_price_data)
  }

  return render(request, 'dashboard.html', context)

battery_percentage = 100
last_update_time = now()

def update_dashboard_state(request):
  global battery_percentage, last_update_time
  url = f'http://192.168.0.111/query?select=[time.iso,input_0,Fridge,Solar,Recepticles]&begin=s-5s&end=s&group=5s&format=json&header=yes'
  response = requests.get(url)
  if response.status_code != 200:
    print('Error fetching data from IotaWatt')
    return JsonResponse({'error': 'Error fetching data from IotaWatt'}, status=500)

  data = response.json().get('data', [])

  if not data:
    print('No data returned from IotaWatt')
    return JsonResponse({'error': 'Error fetching data from IotaWatt'}, status=500)
  
  for d in data:
    try:
      fridge = float(d[2])
    except (ValueError, TypeError):
      fridge = 0.0
    
    try:
      battery = float(d[3])
    except (ValueError, TypeError):
      battery = 0.0
    
    try: 
      recepticles = float(d[4])
    except (ValueError, TypeError):
      recepticles = 0.0

    break

  if battery >= 1.0:
    power_source = 'Battery'
  else:
    power_source = 'Grid'
  
  battery_percentage = max(0, battery_percentage)
  estimated_time = estimate_remaining_time(battery_percentage)/60.0

  # fridge_temp = get_temp()
  fridge_temp = -1.0

  new_state = {
    'system_current_power': fridge + recepticles,
    'critical_load_current_power': recepticles,
    'fridge_current_power': fridge,
    'fridge_current_temp': fridge_temp,
    'device_states': {},
    'battery_current_power': battery,
    'battery_charge': battery_percentage,
    'battery_remaining_time': estimated_time,
    'power_source': power_source,
  }

  return JsonResponse(new_state)

@login_required()
def admin(request):
  devices = Device.objects.all().annotate(
    ipv4=Coalesce(
        Subquery(
            KasaSwitch.objects.filter(device=OuterRef('pk')).values('ip_address')[:1],
            output_field=CharField()
        ),
        Value("N/A", output_field=CharField())
    )
  ).order_by('name')
  context = {'devices': devices}
  return render(request, 'admin.html', context)

@login_required()
def CreateNewDevice(request):
  form = DeviceForm()

  if request.method == 'POST':
    form = DeviceForm(request.POST)
    if form.is_valid():
      device = form.save()
      if device.type == 'kasa_switch':
        ip_address = request.POST.get('kasa_ipv4', '').strip()
        if ip_address:
          KasaSwitch.objects.create(device=device, ip_address=ip_address)
        else:
          KasaSwitch.objects.create(device=device, ip_address='0.0.0.0')
      
      return redirect('admin')
    
  context = {'form': form}
  return render(request, 'new_device.html', context)

@login_required()
def UpdateDevice(request, uuid):
  device = Device.objects.get(uuid=uuid)
  form = DeviceUpdateForm(instance=device)
  ipv4_address = None

  if device.type == 'kasa_switch':
    kasa_switch = KasaSwitch.objects.filter(device=device).first()
    if kasa_switch:
      ipv4_address = kasa_switch.ip_address

  if request.method == 'POST':
    form = DeviceUpdateForm(request.POST, instance=device)
    if form.is_valid():
      form.save()
      if device.type == 'kasa_switch':
        new_ip = request.POST.get('kasa-ipv4', '').strip()
        if kasa_switch:
          kasa_switch.ip_address = new_ip
          kasa_switch.save()
        else:
          KasaSwitch.objects.create(device=device, ip_address=new_ip)

      return redirect('admin')
     
  context = {'form': form, 'ipv4_address': ipv4_address}
  return render(request, 'update_device.html', context)

@login_required
def DeleteDevice(request, uuid):
  device = Device.objects.get(uuid=uuid)
  context = {'device_name': device.name, 'device_id': uuid}

  if request.method == 'POST':
    if device.type == 'kasa_switch':
      kasa_switch = KasaSwitch.objects.filter(device=device).first()
      kasa_switch.delete()
    
    device.delete()
    return redirect('admin')
  
  return render(request, 'delete_device.html', context)

camera = None
for i in range(1):
  camera = cv2.VideoCapture(i)
  if camera.isOpened():
    break

if camera is None or not camera.isOpened():
  print('Error: Could not open camera.')
  raise RuntimeError('Could not open camera.')

def generate_frames():
  while True:
    success, frame = camera.read()
    if not success:
      break
    else:
      _, buffer = cv2.imencode('.jpg', frame)
      frame = buffer.tobytes()
      yield (b'--frame\r\n'
             b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def WebcamStreamTest(request):
  return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

@login_required()
def WebcamStreamTestPage(request):
  return render(request, 'stream_test.html')