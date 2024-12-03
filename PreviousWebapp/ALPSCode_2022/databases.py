from time import sleep, strptime
import MySQLdb
from datetime import datetime,timedelta
#from ALPSCode_2022.PricingAPI import PricingAPIHelper
from PricingAPI import PricingAPIHelper
#from ALPSCode_2022.ApplianceClass import Appliance, Fridge
from ApplianceClass import Appliance, Fridge
import sys

class Data:
    _email = None
    _password = None #temporary right now.
    
    def __init__(self):
        self.api = PricingAPIHelper() 
        
    def datePrice(self):
        
        #Gets prices and times of the electricity from 8 days ago for 1 day starting at 11pm and ending the next day at 10:55pm
        self.times = self.api.timeArray[:]
        self.price = self.api.priceArray[:]
        self.day = self.api.time.date()

    
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
    def login(self, username, password):
        qList = []
        qList.append(str.format("SELECT * FROM User WHERE email = '{0}' AND password = '{1}';", username, password))
        print(qList[0])
        user = retrieveQuery(qList, "one")
        if user is None:
            return False
        else:
            return True
    def createUser(username, password):
        #INSERT INTO User (email, password, registration_date) VALUES ("sewellnoah@gmail.com", "castle777", Now());
        qList = []
        qList.append(str.format("INSERT INTO User (email, password, registration_date) VALUES ('{0}', '{1}', Now());", username, password))
        sendQuery(qList)
#Used for sending and retrieving data on Appliances to/from the database
class AppData:
   
    #create a new Appliance and send to database
    def newAppliance(appliance, userEmail, policy):
        #send the data via a SQL call
        qList = []
        qList.append(str.format("INSERT INTO Appliance (ip_addr, app_name, policy_id, curr_state, email) VALUES ('{0}', '{1}', {2}, '{3}', '{4}');", \
                                appliance.IP_address, appliance.applianceName, policy, appliance.currState, userEmail))
        sendQuery(qList) #makes new appliance
        
        #need to check if policy is new -- if so create policy in DB
        qList = []
        qList.append(str.format("SELECT * FROM App_Policy WHERE app_name = '{0}' AND policy_id = '{1}';", appliance.applianceName, policy))
        policies = retrieveQuery(qList, "appLoad") 
        if not policies: #check for empty tuple from DB
            qList = []
            qList.append(str.format("INSERT INTO App_Policy (policy_id, off_time_start, off_time_end, on_time_start, on_time_end, app_name, ADR_enabled) VALUES \
                ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}');", policy, appliance.userOffTime[0], appliance.userOffTime[1], appliance.userOnTime[0], appliance.userOnTime[1],\
                     appliance.applianceName, appliance.adrEnabled))
            print(qList)
            sendQuery(qList) #creates policy in db

    #Return appliances array
    def getAppliances(userEmail):
        #retrieve appliances' info from database
        qList = []
        apps = [] #Appliances to be returned from SQL tuple data

        qList.append(str.format("SELECT * FROM Appliance WHERE email = '{0}';", userEmail))
        appArray = retrieveQuery(qList, "many")

        #tuple of appliances to be converted and appended to return array
        mike_count = 1
        for app in appArray:
            print("Appliance #"+str(mike_count))
            apps.append(tupleToAppliance(app))
            mike_count += 1

        return apps
    
    

    def updateAppState(appName, state):
        #setup query
        qList = []
        qList.append(str.format("UPDATE Appliance SET curr_state = '{0}' \
            WHERE app_name = '{1}';", state, appName))
        sendQuery(qList)
    
    def updateAppADR(appName, adr_enabled):
        #setup query
        qList = []
        qList.append(str.format("UPDATE App_Policy SET ADR_enabled = '{0}' \
            WHERE app_name = '{1}';", adr_enabled, appName))
        sendQuery(qList)

    #def updateOnTime:
    #def updateOffTime:
    #def updateAppADR:

class FridgeData:

    def newFridge(fridge, userEmail, policy):
        #send the data via a SQL call
        qList = []
        qList.append(str.format("INSERT INTO Fridge (app_name, policy_id, curr_state, email) VALUES ('{0}', {1}, '{2}', '{3}');", \
                                fridge.applianceName, policy, fridge.currState, userEmail))
        sendQuery(qList) #makes new appliance
        
        #update to fridge policy
        #need to check if policy is new -- if so create policy in DB
        qList = []
        qList.append(str.format("SELECT * FROM Fridge_Policy WHERE app_name = '{0}' AND policy_id = '{1}';", fridge.applianceName, policy))
        policies = retrieveQuery(qList, "appLoad") 
        if not policies: #check for empty tuple from DB
            qList = []
            qList.append(str.format("INSERT INTO Fridge_Policy (policy_id, desired_temp, app_name, ADR_enabled, high_bound, low_bound, min_before, dead_band) VALUES \
                ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}');", policy, fridge.desiredTemp, fridge.applianceName, fridge.adrEnabled, fridge.highBoundary, fridge.lowBoundary, fridge.minsBefore, fridge.deadBand))
            sendQuery(qList) #creates policy in db

    #Return Fridges array
    def getFridge(userEmail):
        #retrieve appliances' info from database
        qList = []
        fridges = [] #Appliances to be returned from SQL tuple data
        #update to Fridge
        qList.append(str.format("SELECT * FROM Fridge WHERE email = '{0}';", userEmail))
        fridge = retrieveQuery(qList, "one")

        #tuple of appliances to be converted and appended to return array
        #for fridge in fridgeArray:
            #fridges.append(tupleToFridge(fridge)) #update to tupleToFridge
        return tupleToFridge(fridge)

    def updateFridgeState(app_name, state):
        #setup query
        qList = []
        #update to Fridge DB
        qList.append(str.format("UPDATE Fridge SET curr_state = '{0}' \
            WHERE app_name = '{1}';", state, app_name))
        sendQuery(qList)
    
    def updateFridgeADR(app_name, adr):
        #setup query
        qList = []
        #update to Fridge DB
        if adr == "true":
            adrBool = 1
        else:
            adrBool = 0
        qList.append(str.format("UPDATE Fridge_Policy SET ADR_enabled = '{0}' \
            WHERE app_name = '{1}';", adrBool, app_name))
        sendQuery(qList)

    def updateFridgeTemp(app_name, temp):
        #setup query
        qList = []
        #update to Fridge DB
        qList.append(str.format("UPDATE Fridge_Policy SET current_temp = '{0}' \
            WHERE app_name = '{1}';", temp, app_name))
        sendQuery(qList)
          

def sendQuery(queries):
        #Mysql hookup
        db=MySQLdb.connect(user="root",passwd="root",db="testDB")
        cursor = db.cursor()
        counter = 0
        for q in queries:
            cursor.execute(q)          
            db.commit()
            counter += 1

        cursor.close()
        db.close()
        print("sent queries over")
        
def retrieveQuery(queries, operation):
        #Mysql hookup
        db=MySQLdb.connect(user="root",passwd="root",db="testDB")
        cursor = db.cursor()
        result = None
        for q in queries:
            if operation == "many":
                cursor.execute(q)
                result = cursor.fetchall();
                db.commit()
            elif operation == "one":
                cursor.execute(q)
                result = cursor.fetchone();
                db.commit()
                rows = list(result)
                column_names = [i[0] for i in cursor.description]
            else:
                print("Did not compute operation: ")
        cursor.close()
        db.close()

        return result

def tupleToAppliance(app):
    #get the appliance's policy info
    qList = []
    qList.append(str.format("SELECT * from App_Policy WHERE app_name = '{0}' AND policy_id = {1};", app[1], app[2]))
    policy = retrieveQuery(qList, "one")

    offArr = [policy[1], policy[2]]
    onArr = [policy[3], policy[4]]
    count = 0
    #print(offArr)
    #print(onArr)
    for off, on in zip(offArr, onArr):
        if off != "":
            offArr[count] = datetime.strptime(off,'%H:%M:%S').strftime("%I:%M%p")
        else:
            offArr[count] = ""
        if on != "":
            onArr[count] = datetime.strptime(on,'%H:%M:%S').strftime("%I:%M%p")
        else:
            onArr[count] = ""
        count+=1
    
    #going to need to set each item accordingly 
    # applianceName, currState, adrEnabled, IP_address, priceThreshold=None, userOffTime=None, userOnTime=None, prevState=None):
    #print(app) -> IP address, switchname, policy id, smartplug on/off, user email 
    #print(policy) -> policy id, on_start time, on_end time, off_start time, off_end time, switchname, adrEnabled
    #print(app[1],app[3],policy[6],app[0], [policy[1], policy[2]], [policy[3], policy[4]], policy[5]) #switchname, smartplug on/off, adrEnabled (0 or 1), IP_address, offTime list, onTime list, switchname
    return Appliance(app[1],app[3],policy[6],app[0], offArr, onArr, policy[5])

def tupleToFridge(fridge):
    #get the appliance's policy info
    qList = []
    #update to Fridge_Policy
    qList.append(str.format("SELECT * from Fridge_Policy WHERE app_name = '{0}' AND policy_id = {1};", fridge[0], fridge[1]))
    policy = retrieveQuery(qList, "one")


    #going to need to set each item accordingly 
    print("Fridge(" , fridge[0],fridge[2],policy[8], policy[1],policy[4], policy[5], policy[6], policy[5],")")
    #self, applianceName, currState, adrEnabled, desiredTemp, highBoundary, lowBoundary, deadBand, minsBefore):
                                                            #None      47        30          42
    return Fridge(fridge[0],fridge[2],policy[8], policy[1],policy[4], policy[5], policy[6], policy[5])
'''
def main():
    #AppData.getAppliances("sewellnoah@gmail.com")
    Data.createUser("sewellnoah@gmail.com","castle777")
    switch1_IP = "192.168.0.102"
    switch2_IP = "192.168.0.103"
    switch3_IP = "192.168.0.104"
    switch4_IP = "192.168.0.105"
    switch5_IP = "192.168.0.106"
    switch6_IP = "192.168.0.107"
    switch7_IP = "192.168.0.108"
    switch8_IP = "192.168.0.109"

    app1 = Appliance("Switch1", "false", 1, switch1_IP, ["",""], ["",""], "off")
    app2 = Appliance("Switch2", "false", 1, switch2_IP, ["2:13PM", "2:14PM"], ["1:01PM", "1:02PM"], "off")
    app3 = Appliance("Switch3", "false", 1, switch3_IP, ["",""], ["1:12PM", "1:13PM"], "off")
    app4 = Appliance("Switch4", "false", 1, switch4_IP, ["",""], ["",""], "off")
    app5 = Appliance("Switch5", "false", 1, switch5_IP, ["",""], ["",""], "off")
    app6 = Appliance("Switch6", "false", 1, switch6_IP, ["",""], ["",""], "off")
    app7 = Appliance("Switch7", "false", 1, switch7_IP, ["",""], ["",""], "off")
    app8 = Appliance("Switch8", "false", 1, switch8_IP, ["",""], ["",""], "off")
    #                   ?               ?                                                             ?
    #applianceName, currState, adrEnabled, desiredTemp, highBoundary, lowBoundary, deadband, minsBefore)
    fridge = Fridge("Fridge1", "default", 1, 44, 47, 42, "off", 30)

    result = None

    result = AppData.newAppliance(app1, 'sewellnoah@gmail.com', 2)
    result = AppData.newAppliance(app2, 'sewellnoah@gmail.com', 2)
    result = AppData.newAppliance(app3, 'sewellnoah@gmail.com', 2)
    result = AppData.newAppliance(app4, 'sewellnoah@gmail.com', 2)
    result = AppData.newAppliance(app5, 'sewellnoah@gmail.com', 2)
    result = AppData.newAppliance(app6, 'sewellnoah@gmail.com', 2)
    result = AppData.newAppliance(app7, 'sewellnoah@gmail.com', 2)
    result = AppData.newAppliance(app8, 'sewellnoah@gmail.com', 2)
    result = FridgeData.newFridge(fridge, 'sewellnoah@gmail.com', 1)
    sleep(1)

    #AppData.newAppliance(light2, "sewellnoah@gmail.com")

    ret = AppData.getAppliances("sewellnoah@gmail.com")
    #ret = FridgeData.getFridge("sewellnoah@gmail.com")
    for app in ret:
        print(app.currState)
    #print(ret.currentTemp)

    return
main()
'''     