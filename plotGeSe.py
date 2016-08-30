''' 
to plot stuff with python

gnuplot command  plot for [col=2:12] "filename here" using 1:col with linespoints



in python open file get file name, scan in file line by line check number of columbs (len of last in list)
output to temp file and plot

'''
from tkinter import filedialog
from os import system, remove, path
import math


#dialog box to select file,files
def openfile():
  filenames = filedialog.askopenfilenames(filetypes =(('data files','*.TXT'),('all files','*.*')),initialdir = "/home/nelson/Documents/lab/GeSe/data/")
  return filenames

def readfile(filename):
  data=[]
  with open(filename,"r") as f:
    for line in f:
      data.append(line.split())
  return data

def writefile(filename,data):
  with open(filename,'w') as f:
    for line in data:
      f.write(line)


filenames=openfile()
for filename in filenames:
  data=readfile(filename)
  numcol= len(data[-1])
  gnuplotstr='plot for [col=2:%s] "%s" using 1:col with linespoints title "%s col# ".(col-1)' % (numcol,filename,filename[-10:-4])
  gnuplotls=[gnuplotstr]
  writefile("tempgnuplot.gp",gnuplotls)
  system("gnuplot tempgnuplot.gp -persist")
  remove("tempgnuplot.gp")
