from numpy.lib.shape_base import apply_over_axes
from APIClass import APIHelper 
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline

def plot_price():
  apiHelper = APIHelper()

  # data to be plotted
  x = apiHelper.timeArray[0::2]
  y = apiHelper.priceArray[0::2]

  # formatting and smoothing
  xlabel = apiHelper.timeArray[0::12]
  xnew = np.linspace(0,len(x), 800)
  spl = make_interp_spline(np.arange(0,len(x)),y)
  ynew = spl(xnew)
  
  # plotting
  plt.title("Today's Estimated Hourly Electricity Price")
  plt.xlabel("Time")
  plt.ylabel("Price (Cents)")
  plt.xticks(np.arange(0,len(x), step = 6), xlabel, rotation = '35')
  plt.plot(x, y, color ="green")
  figure = plt.gcf()
  figure.set_size_inches(12,7)
  plt.savefig("static/img/myplot.png", dpi = 100)
