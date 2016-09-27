'''
use python3
read is .csv file with multiple columns, 1st columns should be temperature (in K)
all following columns should be raman peak position (in cm-1)
can have multiple header lines, will try to use top one as label, should have one for each column
'''
from tkinter import *
from tkinter.filedialog import askopenfilename
from os import system, remove, path
import math
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

############### functions for opening file dialog and reading data  ###############
def openfile():
  filename = askopenfilename(filetypes =(('data files','*.csv'),('all files','*.*')),initialdir = "/home/nelson/Documents/lab/",parent=Tk())
  return filename

def readdata(filename):
  data=[]
  with open(filename,'r')as f:
    for line in f:
      line=(line[:].replace('\t',','))#replace tabs with comma's
      datum=(line.strip()).split(',')
      data.append(datum)
  return(data)

################# take out header(s), make floats, transmute  #################
def processdata(data):
  header=[]
  for line in data:
    try:
      x=float(line[0])
      break
    except:
      header.append(line)
      data=data[1:]  
  numcols=len(data[0])
  dat=[]
  for i in range(numcols):
    dat.append([])
  for i,row in enumerate(data):
    for n in range(numcols):
      dat[n].append(float(row[n]))
  xdat=dat[0]
  ydat=dat[1:]
  return xdat,ydat,header  


################  actaul functions  for fitting  #######################
h=6.62607004*10**-34 #Plancks constant J*s
k=1.38064852*10**-23 #Boltzman constant J/K
c=2.99792458*10**10  #speep of light cm/s, assume vavg, w, w0 are in cm-1
Const=1.438777354 #hc/k
def w(T,w0,slope,vavg):
  func = w0+(slope*Const*vavg/2)*(1+2/(np.exp(Const*vavg/T)-1))
  return func

def Delta(slope,vavg):
  return -(slope*Const*vavg/2)

############# plot in matplotlib  #######################

################  program main  #######################
filename=openfile()
dat=readdata(filename)
xdata,ydata,header=processdata(dat)
if len(header) <=len(ydata):
  header.append(['no label'])
  for i in ydata:
    header[0].append(['no label'])
for i,data in enumerate(ydata):
  print('\n',header[0][i+1])
  popt,pcov=curve_fit(w,xdata,data,bounds=([1,-1,1],[1000,1,1000]))

  out=["v_0\t","Delta\t","v_an\t","high-T slope"]
  outdat=[popt[0],Delta(popt[1],popt[2]),popt[2],popt[1]]

  for l,item in enumerate(out):
    print(item,'\t',outdat[l])

  plxdat= np.arange(xdata[0],xdata[-1],.5)  	# makes a list start, stop, step
  plt.title(header[0][i+1])			# chart title
  plt.plot(xdata,data,"ko",plxdat,w(plxdat,popt[0],popt[1],popt[2]),'b')	#makes plot
  plt.show()					#shows plot


