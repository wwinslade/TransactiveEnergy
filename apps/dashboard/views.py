from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from apps.devices.models import Device, KasaSwitch, Fridge
from .forms import DeviceForm

import cv2
from django.http import StreamingHttpResponse, JsonResponse

from django.db.models import OuterRef, Subquery, Value, CharField
from django.db.models.functions import Coalesce

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests
import json
from datetime import datetime, timedelta, timezone

from .models import ComedPriceData

# Create your views here.
def home(request):
  return render(request, 'home.html')

def fetch_comed_data(previous_days):

  # Create datetime objects for window start and end
  end_date_obj = datetime.now(timezone.utc)
  begin_date_obj = datetime.now(timezone.utc) - timedelta(days=previous_days)

  # See if most recent entry is older than end of needed window
  query_end_date = end_date_obj.strftime('%Y%m%d%H%M')

  latest_entry = ComedPriceData.objects.latest('timestamp')

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
    date_obj = datetime.datetime.fromisoformat(wd[0])
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
  context = {
    'weeklyLoadLabels': json.dumps(weekly_load_labels),
    'weeklyLoadData': json.dumps(system_weekly_load),
  }


  return render(request, 'dashboard.html', context)

def update_dashboard_state(request):
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
  
  new_state = {
    'system_current_power': fridge + recepticles,
    'critical_load_current_power': recepticles,
    'fridge_current_power': fridge,
    'device_states': {},
    'battery_current_power': battery,
    'battery_charge': 100,
    'battery_remaining_time': 3.1,
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
      
      form.save()
      return redirect('admin')
    
  context = {'form': form}
  return render(request, 'new_device.html', context)

@login_required()
def UpdateDevice(request, pk):
  device = Device.objects.get(uuid=pk)
  form = DeviceForm(instance=device)

  if request.method == 'POST':
    form = DeviceForm(request.POST, instance=device)
    if form.is_valid():
      form.save()
      return redirect('admin')
    
  context = {'form': form}
  return render(request, 'update_device.html', context)

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