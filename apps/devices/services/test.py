from .kasa_switch import KasaSwitch
from .fridge import Fridge
import asyncio
from time import sleep

from .ubibot import UbibotSensor
from config import UBIBOT_API_KEY, UBIBOT_CHANNEL

# async def main():
#   sw = KasaSwitch("test1", "192.168.0.108")

#   await sw.off()

# def main():
#   fridge = Fridge("Fridge")
#   sleep(5)
#   fridge.on()
#   sleep(5)
#   fridge.off()

def getTempSensor():
  fridge = Fridge("Fridge")
  sleep(5)
  fridge.on()
  sleep(30)
  fridge.off()

if __name__ == '__main__':
  # asyncio.run(main())
  # main()
  getTempSensor()


