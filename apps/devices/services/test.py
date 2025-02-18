from .kasa import KasaSwitchAPI
from .fridge import FridgeAPI
import asyncio
from time import sleep

from .ubibot import UbibotSensor
from config import UBIBOT_API_KEY, UBIBOT_CHANNEL

async def main():
  sw = KasaSwitchAPI("192.168.0.108")
  await asyncio.sleep(5)
  await sw.on()
  await asyncio.sleep(5)
  await sw.off()

# def main():
#   fridge = Fridge("Fridge")
#   sleep(5)
#   fridge.on()
#   sleep(5)
#   fridge.off()

# def getTempSensor():
#   fridge = Fridge("Fridge")
#   fridge.on()
#   sleep(60)
#   fridge.off()

if __name__ == '__main__':
  asyncio.run(main())
  # main()
  # getTempSensor()


