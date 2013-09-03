from classDatabase  import logDB

from tkinter import *
import serial 
from serial.tools.list_ports_windows import *

# The following classes are is used by the LogStat
# These classes only use use the VisioStat from classVisioStat

def _toplabel( root, header, col ):
    mf = Frame( root, padx=5, pady=5, bd=4, relief='groove' )
    mf.grid( sticky='n', column=col, row=0 )
    Label( mf, text=header, fg='blue', font=('Arial black',12) ).grid( row=0, column=0, columnspan=2)
    Frame( mf, padx=5, pady=5, height=5, width=140, bg='white', bd=4, relief='groove' ).grid( row=1,column=0, columnspan=2)
    return mf
    
class Comms:

    mf = None               # frame handle
    vs = None               # VisioStat handle
    
    portsfound=8*[""]       # name of comm ports found
    portscheck=8*[0]        # 0 or 1 depending if checked
    portshandl=8*[0]        # check-box handles
    portscount=0            # number of ports found
    
    portsopend=[]           # list of ports to open (selection of portsfound[]

    bstart=None             # handle of the start button
    bstop =None             # handle of the stop button

    scanon  = False         # flips True if START is pressed
    scanoff = False
    
    def __init__(self, root ):

        mf = _toplabel( root, "Connections", col=0 )
        Comms.mf = mf
        
        # Use the Serial module to find all available comports
        i = 0
        for port, desc, hwid in comports():
            Comms.portsfound[i] = port
            Comms.portscheck[i] = IntVar() 
            Comms.portshandl[i]    
            i+=1
        Comms.portscount = i
            
        i = 0
        while i<Comms.portscount:
            x = Checkbutton( mf, text=Comms.portsfound[i], variable=Comms.portscheck[i], padx=20 )
            x.grid( sticky='w', row=i+2, column=0 )
            Comms.portshandl[i]=x
            i+=1

        r = i+2
        Comms.bstart=Button( mf, text='Start scanning', width=12, command=self._start )
        Comms.bstart.grid( row=r, column=0, pady=5 )

        Comms.bstop=Button( mf, text='Stop scanning', width=12, state='disabled',command=self._stop )
        Comms.bstop.grid( row=r+1, column=0, pady=5 )
        mf.update()
        
    def _start( self ):
        
        # Create a list of the ports to open
        i=0
        Comms.portsopend=[]
        while i<Comms.portscount:
            if Comms.portscheck[i].get()>0:
                name = Comms.portsfound[i]
                Comms.portsopend.append( name )
            i +=1
        print("Ports to open: ", Comms.portsopend )
        
        # Disable all check buttons and enable Stop scanning
        i=0
        while i<Comms.portscount:
            Comms.portshandl[i].config( state='disabled' )
            i +=1
        Comms.bstart.config( state='disabled' )
        Comms.bstop .config( state='active' )
       
        # start scanning the ports. Make sure that the main loop includes polling
        
        Comms.scanon  = True
        Comms.scanoff = False

    def justStarted( self ):
        if Comms.scanon == True:
            Comms.scanon = False
            return True
        else:
            return False
    
    def _stop( self ):
        
        # Enable all check buttons and Start
        i=0
        while i<Comms.portscount:
            Comms.portshandl[i].config( state='normal' )
            i +=1
        Comms.bstart.config( state='active' )
        Comms.bstop .config( state='disabled' ) 

        Comms.scanon  = False
        Comms.scanoff = True
        
    def justStopped( self ):
        if Comms.scanoff == True:
            Comms.scanoff = False
            return True
        else:
            return False
               
class Measure:
    mf = None
    
    h1=8*[0]           # handle of eng units string
    h2=8*[0]           # handle of raw string
      
    def __init__(self, root, n ):
        mf = _toplabel( root, "Measurements", col=1 )
        self.mf=mf
        
        i=0
        while i<n:
            x=Label( mf, text="", relief='flat', fg='red', width=7, font=('Arial black',20) )
            x.grid( row=i+2, column=0 )
            y=Label( mf, text="", relief='flat', fg='black', width=24, font=('Arial',10) )
            y.grid( row=i+2, column=1) 
            
            self.h1[ i ]=x
            self.h2[ i ]=y
            i+=1
            
        #mf.update()

    def eng( self, indx, svalue, raw ):
      
        if svalue.strip()!="":
            svalue += 'uA'
        self.h1[ indx ].config( text = svalue, relief='raised' )
        self.h2[ indx ].config( text = raw )
        # self.mf.update()
    
    def closeall( self ):
        i=0
        while i<8:
            if self.h1[i]!=0:
                self.h1[i].config( text="", relief='flat')
                self.h2[i].config( text="", relief='flat')
            i+=1
        self.mf.update()

class Logger:
    mf = None
    
    logon = False   # True if logging is active
    db = None       # db connection handle
    added=0         # number of records added
    
    toaverage = ""    # max records used for statistics
    nraverage = 60  # number of records to average
    
    statmin=8*[0]   # statistics min
    statmax=8*[0]   # statistics min
    statsum=8*[0]   # statistics min
    statcnt=8*[0]   # statistics min
        
    baverd = 0
    bstart = 0      # handle of the start button
    bstop = 0       # handle of the stop button
    
    lstatus = ''    # handle of database status
    lnrec = 0       # handle to number of records
    lstat = 0       # statistics counter of 1st port
    eaverd = 0
    
    def _toave( self ):
        try:
            self.nraverage = int(self.toaverage.get())
            if self.nraverage < 10:
                self.nraverage = 10
        except:
            self.nraverage = 10
        self.toaverage.set( self.nraverage )
        
        self.bstart.focus()
        
        
    
    def __init__(self, root ):
        mf = _toplabel( root, "Logger", col=3 )
        
        # Code to display Averaged Records
        self.toaverage = StringVar()
        self.toaverage.set( str( self.nraverage ) )
        
        Label(  mf, text='Averaged records' ).grid( sticky='e', row=2, column=0)
        x = Entry(  mf, textvariable=self.toaverage, width=3, fg='black',font=('Arial',12))
        x.grid( row=2, column=1)
        self.eaverd = x
        x = Button( mf, text='ok', command=self._toave )
        x.grid( row=2, column=3 )
        self.baverd = x
        
        # Code to display START and STOP buttons
        self.bstart = Button( mf, text='Start logging', width=12, command=self._start )
        self.bstart.grid( row=3, column=0, pady=5 )
        
        self.bstop = Button( mf, text='Stop logging', width=12, state='disabled', command=self._stop)
        self.bstop.grid( row=4, column=0, pady=5 )
        
        # Placeholder to display db Status
        x = Label(  mf, width=7, text='' )
        x.grid( row=3, column=1)
        self.lstatus = x
        
        # Label and counter for statistics
        Label(  mf, text='Statistics' ).grid(  sticky='e', row=5, column=0)

        x = Label(  mf, text='0', fg='black',font=('Arial',12))
        x.grid( row=5, column=1)
        self.lstat = x
        
        # Label and counter for records written
        Label(  mf, text='Records added' ).grid( sticky='e', row=6, column=0)

        x = Label(  mf, text='0', fg='black',font=('Arial',12))
        x.grid( row=6, column=1)
        self.lnrec = x
        
        mf.update()
        self.mf = mf
    
    def _start( self ):
        
        # start scanning the ports. Make sure that the main loop includes polling
        
        db = logDB()
        e = db.connect( "VisioLog.sqlite" )
        
        if e:
            self.lstatus.config( text="Err %d"%e )
        else:
            print( "Logging started...")
            self.db = db
            self.lstatus.config( text="OK") 
            self.bstart.config( state='disabled' )
            self.baverd.config( state='disabled' )
            self.eaverd.config( state='disabled' )
            self.bstop.config( state='active' ) 
             
            self.added = 0    
            self.lnrec.config( text=str(0) )
            self._resetstat()     
            self.logon = True

    def _stop( self ):
        
        self.bstart.config( state='active' )
        self.bstop .config( state='disabled' )
        self.baverd.config( state='active' )
        self.eaverd.config( state='normal' )
            
        self.lstatus.config( text="") 
        print( "Logging stopped...")
        self.logon = False
        
    def lograw( self, pname, raw, seng ):
        
        if self.logon==False:
            return
        self.db.save( pname, raw, float( seng ), 0, 0 )
        self.added += 1
        self.lnrec.config( text=str(self.added) )

    # resets statistic accumulators for all ports
    def _resetstat( self ):       
        i = 0
        while i<8:
            self.statmin[i] = +1.0E+10
            self.statmax[i] = -1.0E+10
            self.statsum[i] = 0.0
            self.statcnt[i] = 0
            i += 1
            
    # Updates statistics, and if it is time to save them, does so
    def logstats( self, idx, pname, sernum, raw, feng ):
        if self.logon==False:
            return
        x = feng
        if x < self.statmin[idx]:
            self.statmin[idx] = x
        if x > self.statmax[idx]:
            self.statmax[idx] = x
        self.statsum[idx] += x
        self.statcnt[idx] +=1
        if idx == 0:
            c = self.statcnt[0]
            self.lstat.config( text=str( c ) )
            
        if self.statcnt[idx] > self.nraverage:
            ave = self.statsum[idx]/self.statcnt[idx]
            self.db.save( pname, sernum, raw, 
                                round( ave,3),
                                round( self.statmin[idx],3),
                                round( self.statmax[idx], 3 ) )
            self.statmin[ idx ] = +1.0E+10
            self.statmax[ idx ] = -1.0E+10
            self.statsum[ idx ] = 0.0
            self.statcnt[ idx ] = 0
            
            self.added += 1
            self.lnrec.config( text=str(self.added) )
                
                  
class AllDone:
    def __init__( self, root ):
        mf = Frame( root, padx=5, pady=5 )
        mf.grid( column=3, row=1 )
        Button( mf, text='EXIT', width=12, command=self._done ).grid(column=0,row=0)
    def _done( self ):
        print("All done")
        exit(0)
    


    
