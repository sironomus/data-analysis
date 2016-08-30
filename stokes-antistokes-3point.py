#!/usr/bin/env python
#positions of three data points
from sys import argv
if len(argv) ==5:
  spos1 = int(argv[1])
  spos2 = int(argv[2])
  spos3 = int(argv[3])
  apos1 = int(argv[1])
  apos2 = int(argv[2])
  apos3 = int(argv[3])
  tempK = int(argv[4])
else:
  spos1=205# baseline 1 of stokes
  spos2=252# postion of peak of stokes
  spos3=295# baseline 2 of stokes
  apos1=205# baseline 1 of anti stokes
  apos2=252# postion of peak of anti stokes
  apos3=295# baseline 2 of anti stokes
  tempK=293# temperature of exp
"""
comments describing how it works
"""
from Tkinter import *
from tkFileDialog import askopenfilenames
from os import system, remove, path
import math
#dialog box to select file,files
def openfile():
  filenames = askopenfilenames(filetypes =(('data files','*A1*.TXT'),('all files','*.*')),initialdir = "/home/nelson/Documents/lab/GeSe/temperature data/",parent=Tk())
  return filenames

'''
check for file existance of all files
'''
def fileexist(filename):
  sfilename = path.basename(filename)
  filepath = path.dirname(filename)
  AA1filename = filepath+"/"+sfilename[0]+"A1"+sfilename[3:]
  AA2filename = filepath+"/"+sfilename[0]+"A2"+sfilename[3:]
  AA3filename = filepath+"/"+sfilename[0]+"A3"+sfilename[3:]
  AS1filename = filepath+"/"+sfilename[0]+"S1"+sfilename[3:]
  AS2filename = filepath+"/"+sfilename[0]+"S2"+sfilename[3:]
  AS3filename = filepath+"/"+sfilename[0]+"S3"+sfilename[3:]
  return (path.exists(AA1filename) and path.exists(AS1filename) and path.exists(AA1filename) and path.exists(AS1filename) and path.exists(AA1filename) and path.exists(AS1filename)) , [AA1filename,AA2filename,AA3filename,AS1filename,AS2filename,AS3filename]
#read data
'''
takes data file name (str) and puts it into a list form that python can read.  The file should consits of a single header line followed by two sets of numbers.  no other info should be in the file.  it does not check that the numbers make sense.  The output is a list of data points in float.
'''
def readdata(filename):
  data=[]
  f= open(filename,"r")
  for line in f:
    datum=(line.strip()).split()
    data.append(datum)
  f.close()
  data.pop(0)
  for i in range(len(data)):
    data[i] = float(data[i][1])
  return(data)

#remove everything over 2 sigma deviation
''' 
for now just remove 5%(2 sigma if normal distro) of points farthest from the average.  in future actually calcuate 2 sigma based on data and remove appropriately 
'''
def removeoutliers(data):
  outlierpercent=.32
  rmpoints= int(math.ceil((outlierpercent*len(data))/2))#crude number of points to remove from top and bottom
  data.sort()
  for i in range(rmpoints):
    data.pop(0)
    data.pop()
  return data

#RMS. find rms of some data
def rms(data):
  avg = sum(data)/len(data)
  rmslist=[]
  for point in data:
    rmslist.append(math.pow((point-avg),2))
  rms = math.pow((sum(rmslist)/len(rmslist)),.5)
  return avg,rms

#calculate intensities

def intensity(data):
  aslope = ((data[0][0] - data[2][0])/(-apos1+apos3)) #slope between anti stokes baseline points
  sslope = ((data[3][0] - data[5][0])/(spos1-spos3))  #slope between stokes baseline points
  #if abs(aslope) > 0.2 or abs(sslope)>0.2:
    #print "warning high slope between baseline points"
  ab2 = sslope*(apos2-apos1)+data[0][0]# baseline under anti-stokes peak
  sb2 = sslope*(spos2-spos1)+data[3][0]# baseline under stokes peak
  aslopee = ((data[0][1] - data[2][1])/(-apos1+apos3)) #slope between anti stokes baseline error points
  sslopee = ((data[3][1] - data[5][1])/(spos1-spos3))  #slope between stokes baseline error points
  ab2e = sslopee*(apos2-apos1)+data[0][1]# error baseline under anti-stokes peak
  sb2e = sslopee*(spos2-spos1)+data[3][1]# error in baseline under stokes peak
  Ias = data[1][0]-ab2 #antistokes intensity
  Is = data[4][0]-sb2  #stokes intensity
  Iase = pow(pow(data[1][1],2) + pow(ab2e,2),.5) # anti stokes error
  Ise = pow(pow(data[4][1],2) + pow(sb2e,2),.5) # stokes error
  err= (Is/Ias)*pow(pow(Ise/Is,2)+pow(Iase/Ias,2),0.5)
  return Is/Ias, err

#calculate temperateure from Stokes/anti-Stokes ratio
def tempcalc(IsoverIas,laser,peakpos,T0):#laser in nm, peak pos in Rcm-1, T0 in K
	#h*c/kb  constant with c in cm/s, h and kb in SI
	hck = 1.360869565
	v= (1.0/laser)*math.pow(10,7)
	return(hck*peakpos*(1.0/math.log((IsoverIas)*math.pow(((v+peakpos)/(v-peakpos)),4)))-T0)
	#return(hck*peakpos*(1.0/math.log(Is/Ias)))

#print tempcalc(348.57,125.38,676.457,250.0,293)

filenames=openfile()
#filenames=['/home/nelson/Documents/lab/GeSe/temperature data/AA1020.TXT','/home/nelson/Documents/lab/GeSe/temperature data/AA1021.TXT']
for filename in filenames:
  scanfiles=fileexist(filename)
  if scanfiles[0]==1:
    data=[] #containst the raw data
    avgrms=[] #contains the average and rms of each data set
    for i in range(len(scanfiles[1])):
	data.append(readdata(scanfiles[1][i])) #data in order [A1,A2,A3,S1,S2,S3]
    for dataset in data:
      dataset = removeoutliers(dataset)
      avgrms.append(rms(dataset))
    intensities =intensity(avgrms) # (Is/Ias, err)
    print (path.basename(filename)[3:-4] + " temp: "+ str(tempcalc((intensities[0]),676.457,spos2,tempK)) + " K range: "+str(tempcalc(intensities[0]+intensities[1],676.457,spos2,tempK))+ " K - " +str(tempcalc(intensities[0]-intensities[1],676.457,spos2,tempK))+" K" ) 
  else: print "Error. File(s) don't exist"
