# displays all serial ports

from serial.tools.list_ports_windows import *
import time

i=0
while True:
        print("-------------Attempt %d---------------------------"%i)
        for port, desc, hwid in comports():
                print( port, desc, hwid )
        time.sleep( 1 )
        i +=1
        
