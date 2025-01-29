# ubibot.py
# Created by William Winslade on 28 Jan 2025

# Ubibot API docs: https://www.ubibot.com/platform-api/1232/quick-start/

import requests
import json
import os

class UbibotSensor:
  def __init__(self, api_key, channel):
    self.api_key = api_key
    self.channel = channel
  
  def get_temp(self):
    api_url = str("https://api.ubibot.com/channels/%s?account_key=%s"%(self.channel, self.api_key))
    api_response = requests.get(api_url)
    
    if api_response.status_code == 200:
      data = api_response.json()
      with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

      tmp = data["channel"]["field1"]

      if type(tmp) == float:
        print(f"DEBUG: Ubibot API returned temp of {tmp}")
      else:
        print(f"WARN: Ubibot API returned a non-numerical temp value")      

      return tmp
    
    else:
      print(f"Ubibot API call failed with status code {api_response.status_code}")
      return None


    

    
