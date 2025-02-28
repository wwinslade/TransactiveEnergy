from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from apps.devices.models import Device, KasaSwitch, Fridge
from .forms import DeviceForm

import cv2
from django.http import StreamingHttpResponse

from django.db.models import OuterRef, Subquery, Value, CharField
from django.db.models.functions import Coalesce

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Create your views here.
def home(request):
  return render(request, 'home.html')

def dashboard(request):
  return render(request, 'dashboard.html')

def notify_dashboard_update(new_state):
  channel_layer = get_channel_layer()
  
  async_to_sync(channel_layer.group_send)('smarthome_updates', {
    'type': 'smarthome_state_update',
    'state': new_state
  })

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