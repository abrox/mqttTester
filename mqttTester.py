#!/usr/bin/env python
'''
The MIT License (MIT)
Copyright (c) 2016  Jukka-Pekka Sarjanen
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''
import argparse
import Queue
import signal
import threading
import paho.mqtt.client as mqtt
from threading import Timer
from datetime import datetime
from timeit import default_timer as timer
from random import uniform

stayingAlive=True

def signal_handler(signal, frame):
        global stayingAlive
        stayingAlive = False
        print('You pressed Ctrl+C!')
        
class Connector (threading.Thread):
    ''' '''
    def __init__(self, cfg, callBackIf,myId):
        threading.Thread.__init__(self)
        self.cb        = callBackIf
        self.alive     = True
        self.myId      = myId
        self.cfg       = cfg
        self.startTime = 0
        self.date = None
        
        self.state  = 'disconnected'
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self,client, userdata, flags, rc):
        #print("Connector... Connected with result code "+str(rc))
        self.state  = 'connected'
        t = timer()*1000000
        delta = t-int(self.startTime)
        m =  'c,'+str(self.date)+ ','+str(self.myId) +','+str(int(delta))
        self.cb.putQ(m)
        
        self.startTimer()
    

    def startTimer(self):
        t = uniform(1.0, 6.0)
        self.sendTimer = Timer(t, self.on_timer)
        self.sendTimer.start()

    def on_disconnect(self,client, userdata, rc):
        #print("Connector...Disconnected with result code "+str(rc)) 
        self.state  = 'disconnected'
        self.startTimer()
        
    def on_timer(self):
        if self.state  == 'disconnected':
            self.client.connect(self.cfg.host)
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.startTime = timer()*1000000
        elif self.state  == 'connected':
            self.client.disconnect()
         
    def run(self):
        
        self.startTimer()
        
        while self.alive:
            self.client.loop()
        self.sendTimer.cancel()
        self.client.disconnect()
           
    def __del__(self):
        self.alive = False
        
############################################################    
class Publisher (threading.Thread):
    ''' '''
    def __init__(self, cfg, callBackIf):
        threading.Thread.__init__(self)
        self.cb        = callBackIf
        self.alive     = True
        self.cfg       = cfg
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.sendTimer=Timer(self.cfg.pubt,self.on_timer)
        
    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.sendTimer.start()
        
    def on_timer(self):
        self.sendTimer = Timer(self.cfg.pubt,self.on_timer)
        self.sendTimer.start()
        t= timer()
        t=t*1000000
        self.cb.putQ('p,'+str(int(t)))
        self.client.publish(self.cfg.topic, int(t), self.cfg.qos)
      
        
    def run(self):
        self.client.connect(self.cfg.host)
        while self.alive:
            self.client.loop()
        self.sendTimer.cancel()
        self.client.disconnect()
           
    def __del__(self):
        self.alive = False
        
############################################################
class Subscriber (threading.Thread):
    ''' '''
    def __init__(self, cfg, callBackIf,myId):
        threading.Thread.__init__(self)
        self.cb        = callBackIf
        self.alive     = True
        self.myId      = myId
        self.cfg       = cfg
         
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_message(self,client, userdata, msg):
        t = timer()*1000000
        delta = t-int(msg.payload)
        m =  's,'+str(msg.payload)+ ','+str(self.myId) +','+str(int(delta))
        self.cb.putQ(m)
        
    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.client.subscribe(self.cfg.topic,qos=self.cfg.qos)   
        
    def run(self):
        self.client.connect(self.cfg.host)
        
        while self.alive:
            self.client.loop()    
        self.client.disconnect()
                                  
    def __del__(self):
        self.alive = False
   
###################################################################################
class Tester():
    def __init__(self,args):
        self.queue      = Queue.Queue( maxsize=20 )# Just prevent's increase infinity... 
        self.threads=[]
        self.cfg=args
        #Create subscriper threads
        for num in range(0,args.subs,1):
            s = Subscriber(args,self,str(num))
            self.threads.append(s)
        #create publisher    
        p = Publisher(args,self) 
        self.threads.append(p)
        #Create connectors if any
        for num in range(0,args.conn,1):
            c = Connector(args,self,str(num))
            self.threads.append(c)
            
    def putQ(self, msg):
        '''Callback function handling incoming messages'''
        try:
            self.queue.put(msg,False)
        except Queue.Full,e:
            global stayingAlive
            print( 'Queue overflow: '+ str(e))
            stayingAlive = False #No reason to continue 
            
    def runMe(self):
        global stayingAlive
        results={}
        
        for t in self.threads:
            t.start() 
        
        s='time;'
        for num in range(0,self.cfg.subs,1):
            s+='Subs'+ str(num)+';'
        outFile = open(self.cfg.file,'w')
        outFile.write(s+'\n')      
      
        
        while(stayingAlive):
            try:
                msg = self.queue.get(block=True,timeout=1.0)
                l=msg.split(',')
                mType = l[0]
                timeStamp = l[1]
                if mType =='p':
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    results[timeStamp]=[date,{}]
                    #print results
                elif mType == 's':
                    myId   = l[2]
                    delta  = l[3]
                    row    = results[timeStamp]
                    values = row[1]
                    values[myId]= delta
                    if len(values) == self.cfg.subs:
                        s=str(row[0])+';'
                        for num in range(0,self.cfg.subs,1):
                            s+=values[str(num)] + ';'
                        #print( s)
                        outFile.write(s+'\n')
                        del   results[timeStamp]
                elif mType == 'c':
                    print msg
            except Queue.Empty:
                pass
        
        outFile.close()
        for t in self.threads:
            t.alive=False
            
        print( "Alive is False")  
                      
        for t in self.threads:
            t.join()
        print ("All threas joined")    
############################################################################################
def handleCmdLineArgs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--file', '-f',help='outfile',default='mqttTester.dat')
    parser.add_argument('--host', '-H',help='broker address',default='localhost')
    parser.add_argument('--qos',  '-q',help='Quality of service',default=0 ,type=int, choices=[0, 1, 2])
    parser.add_argument('--subs', '-s',help='Number of subscribers',default=1 ,type=int)
    parser.add_argument('--topic','-t',help='topic used',default='myTest')
    parser.add_argument('--pubt', '-p',help='timeout for publishing s',default=3 ,type=int)
    parser.add_argument('--conn', '-c',help='connectors',default=0 ,type=int)
    return parser.parse_args()

def main( args ):
    t=Tester( args )
    t.runMe()
    
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main(handleCmdLineArgs())