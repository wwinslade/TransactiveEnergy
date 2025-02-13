from django.contrib import admin

from .models import Device, KasaSwitch, Fridge
# Register your models here.

admin.site.register(Device)
admin.site.register(KasaSwitch)
admin.site.register(Fridge)