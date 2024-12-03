import json
import requests
from datetime import datetime, timedelta

# Makes API calls to ComEd API to retreive JSON file containing hourly price info
class PricingAPIHelper:

  def __init__(self):

    # Getting the Date last Week minus a hour for time change
    time = datetime.now() - timedelta(days = 8)

    self.time = time
    year = time.strftime("%Y")
    month = time.strftime("%m")
    day = time.strftime("%d")
    date_start = str("%s%s%s2300"%(year, month, day))
    self.date_start = date_start
    time = time + timedelta(days = 1)
    year = time.strftime("%Y")
    month = time.strftime("%m")
    day = time.strftime("%d")
    date_end = str("%s%s%s2255"%(year, month, day))
    self.date_end = date_end
    
    #print("Year: "+str(year))
    #print("Month "+str(month))
    #print("Day: "+str(day))
    #print("Date Start: "+str(date_start))
    #print("Time: "+str(time))
    #print("Date End: "+str(date_end))

    # API for pulling prices from last week @https://hourlypricing.comed.com/live-prices/
    self.apiLink = str("https://hourlypricing.comed.com/api?type=5minutefeed&datestart=%s&dateend=%s"%(date_start, date_end))
    #print("Link: "+str(self.apiLink))
    #exit()  # used for testing
    self.apiData = requests.get(self.apiLink).json()

    self.timeArray = []
    self.priceArray = []

    # For loop for the JSON file, which is given backwards, so we reverse the data
    json_length = len(self.apiData)
    for i in range(json_length):
      self.timeArray.append(datetime.fromtimestamp(int(self.apiData[i]["millisUTC"])/1000).strftime("%X"))
      self.priceArray.append(float(self.apiData[i]['price']))

    self.timeArray.reverse()
    self.priceArray.reverse()
    print("\tPricing API complete.")
