from classVisioStat import VisioStat, open1Port, toeng 

from tkinter import *
import serial 
from serial.tools.list_ports_windows import *

# The following class is used by the CheckVisio
# This class only uses the open1Port and toeng() from classVisioStat

class Comm1:

    mf = None               # frame handle
    vs = None               # VisioStat handle
    
    portsfound=8*[""]       # name of comm ports found
    portshandl=8*[0]            # check-box handles
    portscount=0            # number of ports found
    
    portscheck=0            # IntVar().get() is the index of the port to open
    vs=0                    # VisioStat handle when port is opened

    bstart=None             # handle of the start button
    bstop =None             # handle of the stop button
    ldata =None             # handle of data displayed
    lerr  =None             # error information
    
    opened= False            # flips True if START is pressed
    
    def __init__(self, root ):

        mf = Frame( root, padx=5, pady=5, bd=4, relief='groove' )
        mf.grid( sticky='n', column=0, row=0 )

        # Use the Serial module to find all available comports
        i = 0
        for port, desc, hwid in comports():
            self.portsfound[i] = port
            i+=1
        self.portscount = i
        
        self.portscheck = IntVar()

        i = 0
        while i<self.portscount:
            x = Radiobutton( mf, text=self.portsfound[i], variable=self.portscheck, value=i, padx=20 )
            x.grid( sticky='w', row=i+2, column=0 )
            self.portshandl[i]=x
            i+=1

        r = i+2
        self.bstart=Button( mf, text='Open port', width=12, command=self._start )
        self.bstart.grid( row=r, column=0, pady=5 )

        self.bstop=Button( mf, text='Close port', width=12, state='disabled',command=self._stop )
        self.bstop.grid( row=r+1, column=0, pady=5 )
        
        # Label with the 'raw' data
        self.ldata = Label( mf, text="", width=30 )
        self.ldata.grid( row=r+2, column=0, pady=2)

        # Label with the 'einfo' data
        self.lerr = Label( mf, text="" )
        self.lerr.grid( row=r+3, column=0 )

        mf.update()
    
    def _start( self ):
        
        pname = self.portsfound[ self.portscheck.get() ]
        print("Port to open: ", pname )
        
        self.vs=open1Port( pname )
        
        # Disable all check buttons and enable Stop scanning
        i=0
        while i<self.portscount:
            self.portshandl[i].config( state='disabled' )
            i +=1
        self.bstart.config( state='disabled' )
        self.bstop .config( state='active' )
       
        # start scanning the ports. Make sure that the main loop includes polling
        
        self.opened  = True

    def _stop( self ):
        
        self.vs.close1Port()
        print( "Closed..." )
        # Enable all check buttons and Start
        i=0
        while i<self.portscount:
            self.portshandl[i].config( state='normal' )
            i +=1
        self.bstart.config( state='active' )
        self.bstop .config( state='disabled' ) 
        self.lerr  .config( text='' )
        self.ldata .config( text='' )
        
        self.opened  = False

    def decodeline( self ):
        (idx, pname, raw) = self.vs.read1Port()
        # if idx<0, data were not received in-time
        
        if idx<0:
            print( "--- waiting for data ---" ) 
            self.lerr.config( text='Timeout, no data received for 2 sec' )
            return (-1, "     ", 0)   
            
        else:            
            print( raw )
            self.ldata.config( text=raw )
            
            # try to decode the data
            (serial, seng, feng, value) = toeng( raw )
            if serial < 0:
                self.lerr.config( text='decoding error' )                
            else:
                self.lerr.config( text='ok' )                            
            
            return (serial, seng, value)
            
            # serial = Visiostat serial number 
            #          if -2, that's a decoding error
            # pname = portname
            # raw = raw data as read from VisioStat
            # seng = eng units in ASCII
            # feng = eng units in float
            # value = 0...255 reading
            

        