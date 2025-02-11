from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Device
from .forms import DeviceForm

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
  device = Device.objects.get(id=pk)
  form = DeviceForm(instance=device)

  if request.method == 'POST':
    form = DeviceForm(request.POST, instance=device)
    if form.is_valid():
      form.save()
      return redirect('admin')
    
  context = {'form': form}
  return render(request, 'update_device.html', context)

