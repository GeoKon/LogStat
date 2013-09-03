from classFrames    import Comms, Measure, Logger, AllDone
from classVisioStat import VisioStat, toeng

from tkinter import *

scan = False        # gloabl variable defined and used by the poll()
vs = None           # same

def main():
   
    root = Tk()                 
    root.title("LogStat Rev 1.0: The VisioStat Logger")
    
    # Draw the three vertical frames
    f1 = Comms( root )
    f2 = Measure( root, f1.portscount )
    f3 = Logger( root )
    f4 = AllDone( root )
    
    # Polling loop called ever 10ms
    def poll():
        global scan, vs
        
        # Check if the START Scanning button has just pressed
        if f1.justStarted():
            vs = VisioStat( f1.portsopend )
            print("Scanning...")
            scan = True

        # Check if the STOP Scanning button has just pressed
        if f1.justStopped():
            vs.closeall()
            f2.closeall()
            print("Scanning stopped...")
            scan = False

        # Check if we need to scan all ports for VisioStat data
        if scan:
            (idx, pname, raw) = vs.readport()      # this will wait 100 loops
            (serial, seng, feng, value) = toeng( raw )
            if idx>=0: 

                # Uncomment the line below to see the records before logged
                # print( idx, pname+" "+raw, seng )
                f2.eng( idx, seng, pname+" "+raw )
                f3.logstats( idx, pname, serial, raw, feng )
            else:    
                print("--- waiting for data --------")
        
        # In all cases, re-register this routine to be called again by mainloop
        root.after( 10, poll )

    # Register for the first time the poll() routine
    root.after( 10, poll )
    root.mainloop()
    
main()
    
