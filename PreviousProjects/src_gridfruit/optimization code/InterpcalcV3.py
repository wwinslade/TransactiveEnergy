import sys
import datetime

# theory
#We want to ensure that going into the high cost period, we are at the lowest allowable value. The goal then is too find how long it will take to cool to the low boundary from the current temp.
#During the high price period, we move the low boundary and desired temp to ensure the compressor turns on as little as possible. Process is like this


# if interpoplation type==0 in main code
# 1. Find how long it would take in seconds for the system to heat up from zero to the low boundary temp (heating curves, time on x, temp on y)
# 2. From this value, subtract the duration of period to be shaved.
# 3. Input this time value to find the optimal temp to precool to.
# 4. Find time it would take to reach current temp from 22C, use cooling temperature on x, time on y
# 5. Find time it would take to reach pre-cooling temp from 22C, use cooling temp on x, time ony
# 6. Subtract time to current from time to precool temp (Timelow-Timecurrent) to find length of time needed to cool down to precool
# 7. Interpolate between load conditions to find cooling time
# 8. Given event start time, subtract cooling time from event start time to find time at which pre-cooling should begin.


# if interpolation type==1 in main code
# 1. Find time it would take to reach current temp from 20C, use cooling temperature on x, time on y
# 2. Find time it would take to reach low bound, interpolated pre-cooling temp, or precooling temp from settings from 20C, use cooling temp on x, time ony
# 3. Subtract time to current from time to low bound (Timelow-Timecurrent) to find length of time needed to cool down to low temp
# 4. Interpolate between load conditions to find cooling time
# 5. Given event start time, subtract cooling time from event start time to find time at which pre-cooling should begin.

#### heating functions

def time2heatlow(temp):
    time2heat=0.6306*temp**4 - 22.295*temp**3 + 245.64*temp**2 - 43.156*temp + 1061.1
    return time2heat
def time2heatmed(temp):
    time2heat=291.94*temp*temp - 692.49*temp + 6705
    return time2heat
def time2heatfull(temp):
    time2heat=99.057*temp**2+8701.1*temp-8309.8
    return time2heat

def temp2heatlow(time):
    temp2heat=-3e-8*time**2 + 0.0017*time - 2.0997
    return temp2heat
def temp2heatmed(time):
    temp2heat=-9e-10*time*time + 0.0003*time + 2.3445
    return temp2heat
def temp2heatfull(time):
    temp2heat=-7e-11*time**2+0.0001*time+1.0776
    return temp2heat

#### cooling functions
def time2coollow(temp):#input desired temp to cool to, find time that would take if starting at 22 C
    time2cool=5.0545*temp**2 - 327.08*temp + 4958
    return time2cool
def time2coolmed(temp):
    time2cool=-1.4173*temp**4 - 66.641*temp**3 + 1214.5*temp**2 - 12632*temp + 72062
    return time2cool
def time2coolfull(temp):
    time2cool= -17.245*temp**3 + 752.47*temp**2 - 13388*temp + 101000
    return time2cool

def temp2coollow(time):
    temp2cool=5e-7*time**2-0.0068*time+22.787
    return temp2cool
def temp2coolmed(time):
    temp2cool=-2e-22*time**5+4e-17*time**4-3e-12*time**3+1e-7*time**2-0.0018*time+21.526
    return temp2cool
def temp2coolfull(time):
    temp2cool=4e-7*time**2-0.0052*time+18.248
    return temp2cool


### interpolation functions
def coolingtimelow(currenttemp, lowbound):#find length of time it will take to cool from current temp to lowboundary
    coolingtime=time2coollow(lowbound)-time2coollow(currenttemp)
    return coolingtime
def coolingtimemed(currenttemp, lowbound):
    coolingtime=time2coolmed(lowbound)-time2coolmed(currenttemp)
    return coolingtime
def coolingtimehigh(currenttemp, lowbound):
    coolingtime=time2coolfull(lowbound)-time2coolfull(currenttemp)
    return coolingtime

def interpolateheating(highbound, duration, loadmass):
    if loadmass>0 and loadmass<8000:#interp between low and medium mass curves, x1=0, x2=8000
        lowtime=time2heatlow(highbound) #y1
        medtime=time2heatmed(highbound) #y2
        precooltemplow=temp2heatlow(lowtime-duration.seconds)
        precooltempmed=temp2heatmed(medtime-duration.seconds)
        optprecooltemp=precooltemplow+(loadmass-0)*(precooltempmed-precooltemplow)/(8000)
    else:#interp between medium and high curves
        medtime=time2heatmed(highbound) #y1
        fulltime=time2heatfull(highbound) #y2
        precooltempmed=temp2heatlow(medtime-duration.seconds)
        precooltempfull=temp2heatmed(fulltime-duration.seconds)
        optprecooltemp=precooltempmed+(loadmass-0)*(precooltempfull-precooltempmed)/(8000)
    
    if optprecooltemp<=0:
        optprecooltemp=1
    return optprecooltemp

def interpolatecooling(lowbound,currenttemp,loadmass):
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

def interpolatetemp(currenttemp, pi, pi1, loadmass, tstep):#pi is current compressor state, pi1 is compressor state in next timestep, this was for the optimization code turns out gurobi doesn't like function calls in constraint definitions
    #tstep is short cycle time from optimizationcode
    #heatcool tf is p[i+1]-p[i]. Possible conditions are 1-0=1, 0-0=0, 0-1=-1, 1-1=0; 1-0=1 and 0-0=0 will continue heating for next ten minutes
    #general process find time it would take to heat or cool to current temp, then find temp heated or cooled to after that amount of time 
    if pi1-pi==1:#heating for next ten minutes
        if loadmass>0 and loadmass<8000:
            nexttempa=temp2heatlow(time2heatlow(currenttemp)+tstep)
            nexttempb=temp2heatmed(time2heatmed(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)
        else:
            nexttempa=temp2heatmed(time2heatmed(currenttemp)+tstep)
            nexttempb=temp2heatfull(time2heatfull(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)

    elif pi1-pi==0 and pi==0:#heating for next ten minutes
        if loadmass>0 and loadmass<8000:
            nexttempa=temp2heatlow(time2heatlow(currenttemp)+tstep)
            nexttempb=temp2heatmed(time2heatmed(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)
        else:
            nexttempa=temp2heatmed(time2heatmed(currenttemp)+tstep)
            nexttempb=temp2heatfull(time2heatfull(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)
    elif pi1-pi==0 and pi==1:#cooling for next ten minutes
        if loadmass>0 and loadmass<8000:
            nexttempa=temp2coollow(time2coollow(currenttemp)+tstep)
            nexttempb=temp2coolmed(time2coolmed(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)
        else:
            nexttempa=temp2coolmed(time2coolmed(currenttemp)+tstep)
            nexttempb=temp2coolfull(time2coolfull(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)
    else:#cooling for next ten minutes
        if loadmass>0 and loadmass<8000:
            nexttempa=temp2coollow(time2coollow(currenttemp)+tstep)
            nexttempb=temp2coolmed(time2coolmed(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)
        else:
            nexttempa=temp2coolmed(time2coolmed(currenttemp)+tstep)
            nexttempb=temp2coolfull(time2coolfull(currenttemp)+tstep)
            return nexttempa+(loadmass-0)*(nexttempb-nexttempa)/(8000)



print('end')