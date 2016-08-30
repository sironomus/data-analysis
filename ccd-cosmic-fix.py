#!/usr/bin/env python
"""
open slect O type files (only display o type unless asked.
make list [pos,O ,L,D] for each file each list is list of counts
check that file L all exist
make O,L  read file and fill lists
make D by L-O   for point in range O, D.append( [O[point][0],L[point][1]-O[point][1]])
start/end fix all  (pop of top and bottom of list?)
scan L and D for cosmic rays, D can be very sctrict, cut out using only points that have already been processed.  
remake O


New change
calculate list left and calculate list from right, only keeping points that dont meet criteria, points that appear in both lists get averaged down.  points in 1 list only get to stay.  should lead to small peaks staying but more agressive cutting percentile.


"""
from Tkinter import *
from tkFileDialog import askopenfilenames
from os import system, remove, path

'''
creates a gui to allow selecting of multiple files using Ctrl or Shift.  to switch to one file one use askopenfilename  also need:
from Tkinter import *
from tkFileDialog import askopenfilenames
'''
def openfile():
  filenames = askopenfilenames(filetypes =(('data files','O*.PRN'),('all files','*.*')),initialdir = "/home/nelson/Documents/lab/",parent=Tk())
  return filenames


'''
takes data file name (str) and puts it into a list form that python can read.  The file should consits of two sets of numbers.  no other info should be in the file.  it does not check that the numbers make sense.  The out put list is a list of lists.  each sub list is a data point with a position (float) and a count (int)
'''
def readdata(lfilename):
  data=[]
  f= open(lfilename,"r")
  for line in f:
    datum=(line.strip()).split()
    datum[0] = float(datum[0])
    datum[1] = int(float(datum[1]))
    data.append(datum)
  f.close()
  return(data)


'''
the first and last point in a data set are often too high (sometimes too low) this script takes the very first and very last point and sets them equal to the adjacent point.  no check is done to make sure this make sense
'''
def processfirstlast(data):
  data[0][1]=data[1][1]
  data[-1][1]=data[-2][1]
  return(data)



'''
writes data out into a .DAT format file
'''
def dataout(data,lfilename):
  fn = lfilename[:-3]+"DAT"
  f = open(fn,"w")
  for line in data:
    datastring = str(line[0])+" "+str(line[1])+"\n"
    f.write(datastring)
  f.close()


'''
find average of a list
'''
def avg(numlist):
  return (float(sum(numlist)/len(numlist)))

'''

do comic ray removal looking for points that are a certain % higher then previouse data
Add in direction for future so can do both backwards and forwards
'''
def rmcosmic(database,percent=.2,prevpoint=2):
  for n in range(prevpoint,len(database)):
    prevnumlist=[]
    for m in range(prevpoint):
      prevnumlist.append(database[n-m-1][1])
    prevaverage = avg(prevnumlist)
    if database[n][1] > (1+percent)*prevaverage:
      database[n][1] =prevaverage
  return database


'''
plots the graph in gnuplot
'''
def gnuplot(data,lfilename,pngout = False):
  if pngout == False:
    f=open("plot.gnu","w")
    f.write('plot "%s.DAT" using 1:2 title "modified %s" with lines, \\' % (lfilename[:-4],path.basename(lfilename)[:-4]))
    f.write('\n"%s" using 1:2 title "original" with lines' %lfilename)
    f.close()
    system('gnuplot plot.gnu -persist')
    remove("plot.gnu")
  elif pngout ==True:
    f=open("plot.gnu","w")
    f.write('set term png')
    f.write('\nset output "%s.png"' %lfilename[:-4])
    f.write('\nplot "%s.DAT" using 1:2 title "modified %s" with lines, \\' % (lfilename[:-4],path.basename(lfilename)[:-4]))
    f.close()
    system('gnuplot plot.gnu -persist')
    remove("plot.gnu")
   


'''
check for file existance of L* if selecting O* and vice versa
'''
def fileexist(lfilename):
  filename = path.basename(lfilename)
  filepath = path.dirname(lfilename)
  Llfilename = filepath+"/L"+filename[1:]
  Olfilename = filepath+"/O"+filename[1:]
  Dlfilename = filepath+"/D"+filename[1:]
  return (path.exists(Olfilename) and path.exists(Llfilename)) , [Olfilename,Llfilename,Dlfilename]

'''
make a newdatabase by subtracting 2 other databases db1-db2
'''
def subtractdatabases(db1,db2):
  db3=[]
  for i in range(len(O)):
    db3.append([db1[i][0],db1[i][1]-db2[i][1]])
  return db3
  
  
  
'''
begin program
'''
lfilenames = openfile()
#lfilenames=["OPVKT08.PRN"]

percent = raw_input("enter percent jump aloud i.e. .2\n")
percent = float(percent)
plotpng = raw_input("save files as png instead of displaying?(y/n)\n")
if plotpng == 'y':
  pngout= True
else:
  pngout = False
for lfilenm in lfilenames:
  lfilenames=fileexist(lfilenm)
  if lfilenames[0] ==1:
    db,O,L,D = [],[],[],[]
    O= readdata(lfilenames[1][0])
    L= readdata(lfilenames[1][1])
    D= subtractdatabases(L,O)
    db =[O,L,D]
    for database in db:
      database= processfirstlast(database)
    L = rmcosmic(L,percent,2)
    D = rmcosmic(D,.05,2)
    O = subtractdatabases(L,D)
    dataout(O,lfilenm)
    gnuplot(O,lfilenm,pngout)
  else:
    print "error with file "+lfilenm+"\npartner file(s) could not be found"
  

  
