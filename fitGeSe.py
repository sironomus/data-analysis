''' 
read in fisrt file and select stron scan with no xtal.  then it smooths, subtracts base line and normalizes on Se A1 peak(or whatever is highest.
Next select target file to analyze.  column by colmun smooths, subtracts baseline, normalizes, then subtracts uncrystalized from target.  inegrates area under the curve, then fits two lorentzians and integrates their area.

prints area under curve, area under fit, and with width of each lorenzian
can plot to show you the "fit"

still to do:
  change so area is a percentage of original Se peak area
  monitor total peak area with time
  add bounds to fitting

'''
from tkinter import filedialog
from os import system, remove, path
import math
import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import quad

#dialog box to select file
def openfile(title):
  filenames = filedialog.askopenfilename(filetypes =(('data files','*.TXT'),('all files','*.*')),initialdir = "/home/nelson/Documents/lab/GeSe/data/",title=title)
  return filenames

def readfile(filename):#read in all of a data file.  works on stuff exported from PMT spectrasuite
  data=[]
  with open(filename,"r") as f:
    for line in f:
      data.append(line.split())
  return data

def writefile(filename,data):#data should be a list of strings
  with open(filename,'w') as f:
    for line in data:
      f.write(line)
      f.write("\n")

def listoflisttostringlist(ll):#format lists of lists to be writeable using the write file function above
  stringlist=[]
  for sublist in ll:
    line=""
    for item in sublist:
      line+=str(item)+"\t"
    stringlist.append(line)
  return stringlist

def average(data,index,columnnum,points):#data input as a arbitrary length list of list, finds average for a certatin number of points/2 on either side of index point for specified column
  rsum=0
  for i in range(points):
    rsum+=float(data[index+i-int(points/2)][columnnum])
  return rsum/points

def smooth(data,index,columnnum,points=5):#together with average, allows for x point AAv smoothing
  dataout=[]
  if index < int(points/2):
    return(smooth(data,index,columnnum,points-2))
  elif index > (len(data)- int(points/2)-1):
    return(smooth(data,index,columnnum,points-2))
  else:
    return(average(data,index,columnnum,points))

def buildcoldata(xlist,ylist):#takes a 2 lists and makes a list of lists (frequently named coldata from now on)
  coldat=[]
  for index,value in xlist:
    coldat.append([value,ylist[index]])
  return coldat

  
def baseline(coldata,startpt=170,endpt=285,size=5):#uses specified endpoints to subtract a baseline from each column
  startavg,endavg=0,0
  startindex,endindex=0,0
  for index,point in enumerate(coldata):
    if float(point[0])== float(startpt):
      startindex=index
    elif float(point[0]) == float(endpt):
      endindex=index
  for i in range(size):
    startavg+=coldata[startindex+i][1]
    endavg+=coldata[endindex+i][1]
  startavg=startavg/size
  endavg=endavg/size
  slope =(endavg-startavg)/(endpt-startpt)
  subdata=[]
  x1,y1=startpt,float(coldata[startindex][1])
  for x,y in coldata:
    subdata.append([float(x),y-(slope*(float(x)-x1)+y1)])
  return subdata

def normalize(coldata): #normalizes a column 0:1
  minv,maxv= 0,0
  normdata=[]
  for x,y in coldata:
    if minv > y:
      minv = y
    elif maxv < y:
      maxv = y
  for x,y in coldata:
    normdata.append([x,(y-minv)/(maxv-minv)])
  return normdata

def subtract(coldata1,coldata2):#subtract coldata1 y's from coldata2 y's
  if len(coldata1)==len(coldata2):
    subtracted=[]
    for index,point in enumerate(coldata1):
      subtracted.append([point[0],coldata2[index][1]-point[1]])
    return(subtracted)

def integrate(coldata,startregion=222,endregion=244):# calulates area under the curve within a specified region
  area=0
  for index,point in enumerate(coldata[:-1]):
    x1,y1=point[0],point[1]
    x2,y2=coldata[index+1][0],coldata[index+1][1]
    if x1 >= startregion and x2 <=endregion:
      area += ((x2-x1)*y1+.5*(x2-x1)*(y2-y1))
  return area

def doublelorentz(x,A1,w1,xc1,A2,w2,xc2,y0):#two lorentz functions
  return (y0 + (2*A1/np.pi)*(w1/(4*(x-xc1)**2+w1**2)))+ (2*A2/np.pi)*(w2/(4*(x-xc2)**2+w2**2))




#config variables
showplots=True
startintegrationregion=222
endintegrationregion=244




#START MAIN
#read in first "reference" spectrum.  select column and file
print("Select file containing column to use as normalization\n")
filename=openfile("choose normalization file with no xtal")
data=readfile(filename)
data=data[1:]
numcol= len(data[-1])
#gnuplot gives you a preview
gnuplotstr='plot for [col=2:%s] "%s" using 1:col with linespoints title "%s col# ".(col-1)' % (numcol,filename,filename[-10:-4])
gnuplotls=[gnuplotstr]
writefile("tempgnuplot.gp",gnuplotls)
system("gnuplot tempgnuplot.gp -persist")
remove("tempgnuplot.gp")
standcol=int(input("enter number of column to use for normalization subtraction\n"))
ysmooth=[]
smoothed=[]
#smooth the refernce spectrum
try:
  for index,line in enumerate(data):
    ysmooth.append(smooth(data,index,standcol,5))
  for i,point in enumerate(ysmooth):
    smoothed.append([float(data[i][0]),point])
  #baseline and normalize reference
  baselined=baseline(smoothed,)
  normalized=normalize(baselined)
  totalarea=integrate(normalized,220,280)
except:
  print("error with normalization file")
#choose target file to analyze (all columns)
print("Select file to be analyzed\n")
filename2=openfile("select file to be analyzed")
data2=readfile(filename2)
data2=data2[1:]
outputlist=["Percentage(fit),Percentage(integrate),w1,w2,area as percentage of total"]
numcol2= len(data2[-1])#get number of colums from the last row of target file
for standcol2 in range(1,numcol2):#go column by coloumn for analysis
  try:
    ysmooth2=[]
    smoothed2=[]#smooth target column
    for index,line in enumerate(data2):
      ysmooth2.append(smooth(data2,index,standcol2,5))
    for i,point in enumerate(ysmooth2):
      smoothed2.append([float(data2[i][0]),point])
    #baseline and normalize target column
    baselined2=baseline(smoothed2)
    normalized2=normalize(baselined2)
    totalarea2=integrate(normalized2,220,280)
    #subtract refernce spectrum from target spectrum
    subtracted=subtract(normalized,normalized2)
    #find area under curve using straig lines between points
    areaundercurve =(integrate(subtracted,startintegrationregion,endintegrationregion))
    xdata=[]
    ydata=[]
    #make data and fit two lorentzians to target spectrum
    for x,y in subtracted:
      xdata.append(x)
      ydata.append(y)
    popt, pcov= curve_fit(doublelorentz,xdata,ydata,p0=(1,.5,233,1,.5,236,0))#popt is function variables, pcov is ???
    #print("A1,w1,xc1,A2,w2,xc2,y0")
    #integrate to find area in region
    fitarea=quad(doublelorentz,startintegrationregion,endintegrationregion,args=(popt[0],popt[1],popt[2],popt[3],popt[4],popt[5],popt[6]))
    #output results
    print("area undercurve: ,",areaundercurve,",fit: ",fitarea[0],",w1: ,",popt[1],",w2: ,",popt[4],"\npercentage(integrate): ,",100*areaundercurve/totalarea,"\npercentage(fit): ,",100*fitarea[0]/totalarea,"\n")
    outputlist.append("%s,%s,%s,%s,%s" % (100*fitarea[0]/totalarea,100*areaundercurve/totalarea,popt[1],popt[4],totalarea2/totalarea))
    #below is formating and printing stuff for gnuplot
    if showplots ==True:
      writefile("tempdata.dat",listoflisttostringlist(subtracted))
      gnuplotstr2='A1=%s\nw1=%s\nxc1=%s\nA2=%s\nw2=%s\nxc2=%s\ny0=%s\n'%(popt[0],popt[1],popt[2],popt[3],popt[4],popt[5],popt[6])
      gnuplotstr2+="f(x)= (y0 + (2*A1/3.141592)*(w1/(4*(x-xc1)*(x-xc1)+w1**2)))+ (2*A2/3.141592)*(w2/(4*(x-xc2)*(x-xc2)+w2**2))\n"
      gnuplotstr2+="g(x)= (y0 + (2*A1/3.141592)*(w1/(4*(x-xc1)*(x-xc1)+w1**2)))\n"
      gnuplotstr2+="h(x)= (y0 + (2*A2/3.141592)*(w2/(4*(x-xc2)*(x-xc2)+w2**2)))\n"
      gnuplotstr2+='plot "tempdata.dat"  with linespoints title "%s col # %s",\\\n'% (filename2[-10:-4],standcol2)
      gnuplotstr2+='   f(x) with lines, g(x) with lines,h(x) with lines'
      gnuplotls2=[gnuplotstr2]
      writefile("tempgnuplot2.gp",gnuplotls2)
      system("gnuplot tempgnuplot2.gp -persist")
      remove("tempgnuplot2.gp")
      remove("tempdata.dat")
  except:
    print("\n\n\n\n\nerror with ",filename2)
outputfilename=filename2[-10:-4]+"_analysis.csv"
writefile(outputfilename,outputlist) 
