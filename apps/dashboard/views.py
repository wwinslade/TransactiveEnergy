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

# Create your views here.
def home(request):
  return render(request, 'home.html')

def dashboard(request):
  return render(request, 'dashboard.html')

def update_dashboard_state(request):
  url = f'http://192.168.0.111/query?select=[time.iso,input_0,Fridge,Solar,Recepticles]&begin=s-5s&end=s&group=5s&format=json&header=yes'
  response = requests.get(url)
  if response.status_code != 200:
    print('Error fetching data from IotaWatt')
    return redirect('dashboard')

  data = response.json().get('data', [])

  if not data:
    print('No data returned from IotaWatt')
    return redirect('dashboard')
  
  for d in data:
    input_0 = float(d[1])
    fridge = float(d[2])
    battery = float(d[3])
    recepticles = float(d[4])
    break

  battery = 10

  if battery >= 0.5:
    power_source = 'Battery'
  else:
    power_source = 'Grid'
  
  new_state = {
    'system_current_power': fridge + recepticles,
    'critical_load_current_power': recepticles,
    'fridge_current_power': fridge,
    'device_states': {},
    'battery_current_power': 0,
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