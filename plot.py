"""

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from threading import Lock

class Plotter ():
    ''''''
    def __init__(self,lines):
        self.xCount=500
        self.fig, ax = plt.subplots()
        self.data ={}
        self.values ={}
        self.maxY = 10.0
        self.xAxist = np.arange(0, self.xCount)
        self.lock = Lock()
        
        
        for id, name in lines:
            p = ax.plot( self.xAxist, self.xAxist,label=name )
            l=list([0 for x in range(self.xCount)])
            self.values[id]=0.0
            self.data[id]=[l,p]
              

        ax.axis([0.0,self.xCount, self.maxY/10.0,self.maxY])
        self.ax = ax

    def setValue(self,key,value):
        rc = True
        self.lock.acquire()
        if self.values.has_key(key):
            self.values[key]=value
        else:
            rc = False  
        self.lock.release()
        return rc
        
    def getValue(self, key):
        self.lock.acquire()
        val = self.values[key]
        self.lock.release()
        return val

    def animate(self,i):
        line=None
        maxY = self.maxY
        for key in self.data:
            l,line = self.data[key]
            val = self.getValue(key)
            l.append(val)
            myarray = np.asarray(l[-self.xCount:]).astype(np.float)
            yVal = np.nanmax(myarray)
            if yVal > maxY:
                maxY = yVal
            line[0].set_ydata(myarray)
        #Set correct max value + 10% space
        if maxY > self.maxY:
            self.maxY = maxY+0.1*maxY
            self.ax.set_ylim(0,self.maxY)
            
        return line[0],

    # Init only required for blitting to give a clean slate.
    def init(self):
        pass
    
    def runMe(self):
        ani = animation.FuncAnimation(self.fig, self.animate, np.arange(1, 1000), 
                                      init_func=self.init,interval=100)
        plt.show()

if __name__ == '__main__':
    p = Plotter()
    p.runMe()
    