from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from apps.devices.models import Device, KasaSwitch, Fridge
from .forms import DeviceForm

import cv2
from django.http import StreamingHttpResponse

# Create your views here.
def home(request):
  return render(request, 'home.html')

@login_required()
def admin(request):
  devices = Device.objects.all().order_by('-updated_at')
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