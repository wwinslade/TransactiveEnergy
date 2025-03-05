import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class DashboardConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.channel_layer.group_add('dashboard_updates', self.channel_name)
    await self.accept()

  async def disconnect(self, close_code):
    await self.channel_layer.group_discard('dashboard_updates', self.channel_name)

  async def receive(self, text_data):
    pass

  async def dashboard_state_update(self, event):
    await self.send(text_data=json.dumps(event))

def send_dashboard_update(data):
  channel_layer = get_channel_layer()
  async_to_sync(channel_layer.group_send)(
    'dashboard_updates', 
    {
    'type': 'dashboard_state_update',
    'system_current_power': data['system_current_power'],
    'critical_load_current_power': data['critical_load_current_power'],
    'fridge_current_power': data['fridge_current_power'],
    'device_states': data['device_states'],
    'battery_current_power': data['battery_current_power'],
    'battery_estimated_pct_charge': data['battery_estimated_pct_charge'],
    }
  )
