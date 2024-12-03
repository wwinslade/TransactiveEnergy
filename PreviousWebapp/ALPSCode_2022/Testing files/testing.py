from databases import AppData
from ApplianceClass import Appliance

def main():
	#applianceName, currState, adrEnabled, IP_address, priceThreshold=None, userOffTime=None, userOnTime=None, prevState=None):
	appliance = Appliance("testLight", True, False, "160.45.32.20", 20)
	AppData.newAppliance(appliance, "sewellnoah@gmail.com")
	
	return 
main()
