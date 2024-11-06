import pandas as pd
import datetime
import xml.etree.ElementTree as ET

def extractxmldates(filename):
    tree=ET.parse(filename)
    tree=extractxmldates("CPPpayload.txt") 
    root=tree.getroot()

    startdt=root[0][0][2][0][1][0][0][0].text
    startdt=startdt.split('T')
    dateinfo=startdt[0].split('-')
    dateinfo=[int(dateinfo[0]),int(dateinfo[1]),int(dateinfo[2])]
    timeinfo=startdt[1].replace('Z','')
    timeinfo=timeinfo.split(':')
    timeinfo=[int(timeinfo[0]),int(timeinfo[1]),int(timeinfo[2])]
    startdt=datetime.datetime(dateinfo[0],dateinfo[1],dateinfo[2],timeinfo[0],timeinfo[1],timeinfo[2])

    duration=root[0][0][2][0][1][0][1][0].text
    Htrue=duration.find('H')
    Mtrue=duration.find('M')
    Strue=duration.find('S')
    duration=duration.replace("PT","")

    if Htrue!=-1 and Mtrue!=-1 and Strue!=-1: #Hours, minutes, seconds included
        Hours=duration.split('H')
        Minutes=Hours[1].split('M')
        Seconds=Minutes[1].replace("S","")
        Hours=int(Hours[0]); Minutes=int(Minutes[0]); Seconds=int(Seconds)
    elif Htrue!=-1 and Mtrue!=-1 and Strue==-1: #Hours and minutes included
        Hours=duration.split('H')
        Minutes=Hours[1].replace('M',"")
        Hours=int(Hours[0]); Minutes=int(Minutes); Seconds=0
    elif Htrue!=-1 and Mtrue==-1 and Strue==-1: #Hours only
        Hours=duration.split('H')
        Hours=int(Hours[0]); Minutes=0; Seconds=0
    elif Htrue==-1 and Mtrue==-1 and Strue!=-1: #Seconds only
        Seconds=duration.split('S')
        Hours=0; Minutes=0; Seconds=int(Seconds[0])
    elif Htrue==-1 and Mtrue!=-1 and Strue!=-1: #minutes and seconds
        Minutes=duration.split('M')
        Seconds=Minutes[1].replace("S","")
        Hours=0; Minutes=int(Minutes[0]); Seconds=int(Seconds)
    else: #minutes only
        Minutes=duration.replace('M',"")
        Hours=0; Seconds=0

    duration=datetime.timedelta(hours=Hours,minutes=Minutes,seconds=Seconds)

    return(startdt,duration)

