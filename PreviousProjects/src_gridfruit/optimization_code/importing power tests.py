import xlrd
import pprint
import gurobipy as gp
from gurobipy import GRB
import itertools
import pandas as pd
import csv
import datetime as dt
import numpy as np
from gurobipy import GRB

with open('thermostatfullloadpower.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    testpower=[]
    for row in reader:
        testpower.append(float(row['power'])) #$/MWh

for i in range(len(testpower)):
    if testpower[i]<=0:
        testpower[i]=0
    else:
        testpower[i]=testpower[i]

with open('da_hrl_lmps.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    Pricedt=[]
    DAprices=[]
    for row in reader:
        DAprices.append(row['total_lmp_da']) #$/MWh
        Pricedt.append(row['datetime_beginning_utc'])
print('end')