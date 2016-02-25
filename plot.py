"""

"""
import sys
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue
import signal
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Plotter (threading.Thread):
    ''''''
    def __init__(self):
    
        self.fig, ax = plt.subplots()
        
        self.xAxist = np.arange(0, 2*np.pi, 0.01)
        self.line, = ax.plot( self.xAxist, np.sin( self.xAxist)+2)
        self.line2, = ax.plot( self.xAxist, np.cos( self.xAxist))

    def animate(self,i):
        print(i)
        self.line.set_ydata(np.sin( self.xAxist + i/10.0))  # update the data
        self.line2.set_ydata(np.cos( self.xAxist + i/10.0))  # update the data
        return self.line,


    # Init only required for blitting to give a clean slate.
    def init(self):
        self.line.set_ydata(np.ma.array( self.xAxist, mask=True))
        self.line2.set_ydata(np.ma.array( self.xAxist, mask=True))
        return self.line,

    def run(self):
        ani = animation.FuncAnimation(self.fig, self.animate, np.arange(1, 200), init_func=self.init,
                              interval=50)
        plt.show()

if __name__ == '__main__':
    p= Plotter()
    p.run()
    