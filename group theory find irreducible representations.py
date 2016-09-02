#python3 program
'''
This program will output the only possible combinations of squares to reach a 
certain target number using a given number of squares.  e.g to reach a 
sum of squares = 24, the sum squres of the numbers 1,1,2,3,3 is the only solution

this is usefull in group theory to determine the number and dimmension of 
the irreducible representations
'''
import itertools

#function just finds sum of squares in a list
def sumsquares(lsquares):
  mag=0
  for i in lsquares:
    mag+=i*i
  return mag


'''
call funct to increment current index. if incrementing that index will bring
list squares over target, reset current index to 1 and call self with index +1,
chugs through all valid combinations of target
'''
def increment(lsquares,index=0):
  if index >= numSquares:
    index=0
  lsquares[index]+=1
  if sumsquares(lsquares) > target:
    lsquares[index]=1
    increment(lsquares,index+1)


#target is the size of the number you want to hit size of the point group   
target=24
#numSquares is the number of squares you can use(in group theory the number of classes) to get to the target
numSquares=5




answers=[]
lsquares=[1]*numSquares #make a list of 1's the length of numSquares
maxtries=(int(target**.5))**numSquares #max number of permutaions needed (overshoots)

for i in range(maxtries):
  increment(lsquares,0)
  #print(lsquares,sumsquares(lsquares))
  if sumsquares(lsquares)== target:
    newans=lsquares[:]
    newans.sort()
    answers.append(newans)
answers.sort()
print(list(answers for answers,_ in itertools.groupby(answers))) #print out only unique lists
