import math
import numpy as np
def countPointsOverLine(pool,lineValue):
    count = 0
    i = 0

    while(i<len(pool)):
        #print("@",pool[i],lineValue)
        if(pool[i]>lineValue):
            count = count+1
        i = i+1
  
    threshold = 5
    if(abs(pool[0] - pool[1])<threshold or abs(pool[1]-pool[2])<threshold):
        return count
    
    return 0

def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]



def findOrientation(data, orientation):
   
    y = np.array(data)
   
    pointsIncluded = []
 
   
 
    if(len(y)!=7):
        return int(-1)

    d = reject_outliers(y)
    if(d.size != 4):
        return -1
    pointsIncluded = np.setdiff1d(y, d);
    if(len(pointsIncluded)!=3):
       # print("NOT 3!")
        return -1
    
    average = math.floor(sum(d)/len(d))

    pointCount = countPointsOverLine(pointsIncluded,average)


    
    #print(pointCount)

    if(orientation == "y"):
        if(pointCount == 2):
            #print("Up arrow")
            return int(1)
        elif(pointCount == 1):
           # print("Down arrow")
            return int(2)
        else:
           # print("Unknown Y")
            return int(-1)
    elif(orientation == "x"):
        if(pointCount == 2):
           # print("Left arrow")
            return int(3)
        elif(pointCount == 1):
           # print("Right arrow")
            return int(4)
        else:
           # print("Unknown X")
            return int(-1)
    else:
       # print("Unknown Orientation")
        return int(-1)
        

    return int(-1)




#v = [13 ,17 ,39 ,43 ,61 ,37 ,35]
#findOrientation(v,"x")
#findOrientation(v,"y")
