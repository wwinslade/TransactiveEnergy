import sys
import datetime

# theory
#We want to ensure that going into the high cost period, we are at the lowest allowable value. The goal then is too find how long it will take to cool to the low boundary from the current temp.
#During the high price period, we move the low boundary and desired temp to ensure the compressor turns on as little as possible. Process is like this

# 1. Find time it would take to reach current temp from 20C, use cooling temperature on x, time on y
# 2. Find time it would take to reach low bound (or desired pre-cooling temp) from 20C, use cooling temp on x, time ony
# 3. Subtract time to current from time to low bound (Timelow-Timecurrent) to find length of time needed to cool down to low temp
# 4. Interpolate between load conditions to find cooling time
# 5. Given event start time, subtract cooling time from event start time to find time at which pre-cooling should begin.


def time2coollow(temp):#input desired temp to cool to, find time that would take if starting at 22 C
    time2cool=5.0545*temp**2 - 327.08*temp + 4958
    return time2cool
def time2coolmed(temp):
    time2cool=-1.4173*temp**4 - 66.641*temp**3 + 1214.5*temp**2 - 12632*temp + 72062
    return time2cool
def time2coolhigh(temp):
    time2cool= -17.245*temp**3 + 752.47*temp**2 - 13388*temp + 101000
    return time2cool

def coolingtimelow(currenttemp, lowbound):#find length of time it will take to cool from current temp to lowboundary
    coolingtime=time2coollow(lowbound)-time2coollow(currenttemp)
    return coolingtime
def coolingtimemed(currenttemp, lowbound):
    coolingtime=time2coolmed(lowbound)-time2coolmed(currenttemp)
    return coolingtime
def coolingtimehigh(currenttemp, lowbound):
    coolingtime=time2coolhigh(lowbound)-time2coolhigh(currenttemp)
    return coolingtime

def interpolate(lowbound,currenttemp,eventstart,loadmass):
    #linear interpolation formula is y=y1+(x-x1)*(y2-y1)/(x2-x1) where x is loadmass, y is cooling time
    if loadmass>0 and loadmass<8000:#interp between low and medium mass curves, x1=0, x2=8000
        lowtime=coolingtimelow(currenttemp,lowbound) #y1
        medtime=coolingtimemed(currenttemp,lowbound) #y2
        timeneededtocool=lowtime+(loadmass-0)*(medtime-lowtime)/(8000)
    else:#interp between medium and high curves
        medtime=coolingtimemed(currenttemp,lowbound) #y1
        hightime=coolingtimehigh(currenttemp,lowbound) #y2
        timeneededtocool=medtime+(loadmass-8000)*(hightime-medtime)/(8000)
    return timeneededtocool

print('end')