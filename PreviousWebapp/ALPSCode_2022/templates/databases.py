import MySQLdb
from datetime import datetime
from PricingAPI import PricingAPIHelper
import sys

class Data:
    
    
    def __init__(self):
        self.api = PricingAPIHelper() 
        
    def datePrice(self):
        
        #Gets prices and times of the electricity from 8 days ago for 1 day starting at 11pm and ending the next day at 10:55pm
        self.times = self.api.timeArray[:]
        self.price = self.api.priceArray[:]
        self.day = self.api.time.date()

    def sendQuery(self,queries):
        #Mysql hookup
        db=MySQLdb.connect(user="root",passwd="root",db="testDB")
        cursor = db.cursor()
        counter = 0
        for q in queries:
            #cursor.execute(q)
            #db.commit()
            counter += 1
            #if counter % 12 == 0:
                #print(q)
        print("sent queries over")
    
    def EnergyStats(self):
        self.datePrice()
        qList = []
        
        for i in range(len(self.times)):
            
            time = datetime.strptime(self.times[i], "%H:%M:%S").time() #grabs the time from string
            date = datetime.combine(self.day,time) #creates DATETIME variable

            #convert date to string for query
            date = str(date)
            qList.append(str.format("INSERT INTO Energy_Stats VALUES ('{0}', '{1}');", date, self.price[i]))
        
        self.sendQuery(qList)
            
def main():
    arg = sys.argv[1]
    print(arg)
    data = Data()
    data.EnergyStats()
    
    return
main()