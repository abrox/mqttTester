"""

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Plotter ():
    ''''''
    def __init__(self):
        xCount=500
        self.fig, ax = plt.subplots()
        self.value = float(0.0);
        self.value2 = float(0.0);

        self.myList=[0 for x in range(xCount)]
        self.myList2=[0 for x in range(xCount)]

        self.xAxist = np.arange(0, xCount)

        self.line, = ax.plot( self.xAxist, self.xAxist)
        self.line2, = ax.plot( self.xAxist, self.xAxist)

        ax.axis([0.0,xCount, 500.0,500000.0])
        self.ax = ax

    def setValue(self,id,value):
        '''Setting one value should be thread safe'''
        if id == 1:
            self.value = float(value)
        else:
            self.value2 = float(value)
        #print(self.value )

    def animate(self,i):
        self.myList.append(self.value)
        self.myList2.append(self.value2)

        if len(self.myList)> 20:
            self.myList.pop(0)
            self.myList2.pop(0)

        myarray = np.asarray(self.myList)
        myarray2 = np.asarray(self.myList2) 

        self.line.set_ydata(myarray)  # update the data
        self.line2.set_ydata(myarray2)  # update the data
        return self.line,


    # Init only required for blitting to give a clean slate.
    def init(self):

        self.line.set_ydata(np.ma.array( self.xAxist, mask=True))
        self.line2.set_ydata(np.ma.array( self.xAxist, mask=True))
        return self.line,

    def runMe(self):
        ani = animation.FuncAnimation(self.fig, self.animate, np.arange(1, 1000), 
                                      init_func=self.init,interval=50)
        plt.show()

if __name__ == '__main__':
    p = Plotter()
    p.runMe()
    