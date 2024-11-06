from ast import Pass
import logging
import sys
import random
import numpy as np
import threading
import time
import datetime

def bound4clow(highbound):
    time25c=16.782*highbound**2+208.84*highbound-913.24
    return time25c
def bound4cmed(highbound):
    time25c=2.9507*highbound**4-94.166*highbound**3+977.99*highbound**2-3051*highbound-686.38
    return time25c
def bound4chigh(highbound):
    time25c=-11.495*highbound**4+677.83*highbound**3-13177*highbound**2+105381*highbound-296337
    return time25c

def tempcooltolow(eventlength, time25c):
    x=time25c-eventlength
    temp2cool2=-8*10**-8*x**2+0.0024*x+3.8073
    return temp2cool2
def tempcooltomed(eventlength, time25c):
    x=time25c-eventlength
    temp2cool2=-1*10**-16*x**4+10**-11*x**3-2*10**-7*x**2+0.0027*x+6.2406
    return temp2cool2
def tempcooltohigh(eventlength, time25c):
    x=time25c-eventlength
    temp2cool2=-9*10**-20*x**4+3*10**-14*x**3-3*10**-9*x**2+0.0002*x+11.29
    return temp2cool2

def tempxtimeylow(temp2cool2):
    secb4event=-0.7729*temp2cool2**2-97.053*temp2cool2+2446.5
    return secb4event
def tempxtimeymed(temp2cool2):
    secb4event=-4.6249*temp2cool2**3+224.58*temp2cool2**2-3742.1*temp2cool2+22289
    return secb4event
def tempxtimeyhigh(temp2cool2):
    secb4event=-1.4278*temp2cool2**3+156.69*temp2cool2**2-4267.6*temp2cool2+34489
    return secb4event

def timeneedcool(Y0,Y1,loadmass,subtractval):
    timeneededtocool=(loadmass-subtractval)*(Y1-Y0)/8000+Y0
    return timeneededtocool
def tempcoolto(T0,T1,loadmass,subtractval):
    #T0,T1 are just temp we need to cool to for the two conditions
    temptocoolto=(loadmass-subtractval)*(T1-T0)/8000+T0
    return temptocoolto

def interpolate(highbound,currenttemp,eventstart,eventend,loadmass):
    if loadmass>0 and loadmass<8000:#interp between low and medium mass curves
        eventlength=datetime.timedelta.total_seconds(eventend-eventstart)#length of event seconds
        fiveclow=bound4clow(highbound)-eventlength
        fivecmed=bound4cmed(highbound)-eventlength
        Temp0=tempcooltolow(eventlength,fiveclow)#temp we need to cool to for low condition
        Temp1=tempcooltomed(eventlength,fivecmed)#temp we need to cool to for high condition
        
        Time0=tempxtimeylow(Temp0)-tempxtimeylow(currenttemp)
        Time1=tempxtimeymed(Temp1)-tempxtimeymed(currenttemp)
        timeneededtocool=timeneedcool(Time0,Time1,loadmass,0)
        temptocoolto=tempcoolto(Temp0,Temp1,loadmass,0)
    else:#interp between medium and high curves
        eventlength=datetime.timedelta.total_seconds(eventend-eventstart)#length of event seconds
        fivecmed=bound4cmed(highbound)-eventlength
        fivechigh=bound4chigh(highbound)-eventlength
        Temp0=tempcooltomed(eventlength,fivecmed)#temp we need to cool to for low condition
        Temp1=tempcooltohigh(eventlength,fivechigh)#temp we need to cool to for high condition
        
        Time0=tempxtimeymed(Temp0)-tempxtimeymed(currenttemp)
        Time1=tempxtimeyhigh(Temp1)-tempxtimeyhigh(currenttemp)
        timeneededtocool=timeneedcool(Time0,Time1,loadmass,8000)
        temptocoolto=tempcoolto(Temp0,Temp1,loadmass,8000)
    return [timeneededtocool,temptocoolto]