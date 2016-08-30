from Tkinter import *
from tkFileDialog import askopenfilenames
from os import system, remove, path
'''
creates a gui to allow selecting of multiple files using Ctrl or Shift.  to switch to one file one use askopenfilename  also need:
from Tkinter import *
from tkFileDialog import askopenfilenames
'''
def openfile():
  filenames = askopenfilenames(filetypes =(('data files','*.PRN'),('all files','*.*')),initialdir = "/home/nelson/Documents/lab/",parent=Tk())
  return filenames
'''
takes data file name (str) and puts it into a list form that python can read.  The file should consits of two sets of numbers.  no other info should be in the file.  it does not check that the numbers make sense.  The out put list is a list of lists.  each sub list is a data point with a position (float) and a count (int)
'''
def readdata(filename):
  data=[]
  f= open(filename,"r")
  for line in f:
    datum=(line.strip()).split()
    datum[0] = float(datum[0])
    datum[1] = int(float(datum[1]))
    data.append(datum)
  f.close()
  return(data)

'''
writes data out into a .DAT format file
'''
def dataout(data,filename):
  fn = filename[:-3]+"DAT"
  f = open(fn,"w")
  for line in data:
    datastring = str(line[0])+" "+str(line[1])+"\n"
    f.write(datastring)
  f.close()


'''
plots the graph in gnuplot
'''
def gnuplot(data,filename):
  f=open("plot.gnu","w")
  f.write('plot "%s.DAT" using 1:2 title "modified %s" with lines, \\' % (filename[:-4],path.basename(filename)[:-4]))
  f.write('\n"%s" using 1:2 title "original" with lines' %filename)
  f.close()
  system('gnuplot plot.gnu -persist')
  remove("plot.gnu")






'''
begin program
'''
filenames = openfile()
#filenames= ['/home/nelson/Documents/lab/GeSe/data/GeSemulti/GS30BA.PRN']
'''
while True:
  try:
    offset = float(raw_input("what value would you like to try?  please enter floting point number:\n") )
    break
  except:
    print "your input was invalid.  try again\n"
'''
hdat=[]
ldat=[]
for filename in filenames:
  data= readdata(filename)
  cntr=1
  for point in data:
    if cntr %2==0:
      hdat.append(point[1])
      cntr +=1
    else:
      ldat.append(point[1])
      cntr+=1
  cntr=1
  hdat.pop()
  ldat.pop()
  hdat.pop(0)
  ldat.pop(0)
  for point in data:
    if cntr %2==0:
      point[1]-=(float(sum(hdat))/len(hdat)-(float(sum(ldat))/(len(ldat)))+0)
      cntr +=1
    else:
      ldat.append(point[1])
      cntr+=1
  dataout(data,filename)
  #gnuplot(data,filename)
