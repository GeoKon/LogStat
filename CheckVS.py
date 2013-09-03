from classMeter import meter 
from classComm1 import Comm1

from tkinter import *

def main():
   
    root = Tk()                 
    root.title("CheckVS Rev 1.0: VisioStat Checking Utility")
    
    # Draw frames
    f1 = Comm1( root )
    f2 = meter( root, "percent", radius=80, row=0, col=1, maxscale=100)    

    mf = Frame( root, pady=1, bd=2, relief='groove' )
    mf.grid( sticky='n', column=1, row=1 )
    en = Label( mf, text="", fg='red', width=10, font=('Arial black',22) )
    en.grid( column=0, row=0 )
    Button( mf, text='EXIT', width=5, command=lambda: exit(0) ).grid( row=0, column=1 )
    
    # Polling loop called ever 10ms
    def poll():
        global scan, vs
        
        # Check if the OPEN button has just pressed
        if f1.opened:
          
            # the following, reads a line, displays result
            (serial, seng, value)=f1.decodeline()
            if serial >=0:
                f2.update( value*100/255 )
                en.config( text=seng+'uA' )
                
        # In all cases, re-register this routine to be called again by mainloop
        root.after( 10, poll )

    # Register for the first time the poll() routine
    root.after( 10, poll )
    root.mainloop()
    
main()