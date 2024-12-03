import asyncio
from kasa import SmartPlug

# switch1_IP = "192.168.4.13"
# switch2_IP = "192.168.4.2"
# switch3_IP = "192.168.4.12"
# switch4_IP = "192.168.4.9"
# switch5_IP = "192.168.4.4"
# switch6_IP = "192.168.4.15"
# switch7_IP = "192.168.4.19"
# switch8_IP = "192.168.4.7"
switch1_IP = "192.168.0.102"
switch2_IP = "192.168.0.103"
switch3_IP = "192.168.0.104"
switch4_IP = "192.168.0.105"
switch5_IP = "192.168.0.106"
switch6_IP = "192.168.0.107"
switch7_IP = "192.168.0.108"
switch8_IP = "192.168.0.109"
on_off = "off"
#on_off = "on"

async def main():
    p = SmartPlug(switch5_IP)

    await p.update()  # Request the update

    if(on_off == "on"): await p.turn_on()
    elif(on_off == "off"): await p.turn_off()

if __name__ == "__main__":
    asyncio.run(main())