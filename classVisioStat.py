import serial 
from serial.tools.list_ports_windows import *
import time

class VisioStat:
    
    phndl = [0,0,0,0,0,0,0,0]           # class array to contain the handles of all ports
    pbuff = ["","","","","","","",""]   # class array of string buffers; one per port
    pmax  = 0
                                
    
    def __init__( self, plist ):
        i=0
        for port in plist:
            if i>7:
                break
            try:
                serhdl = serial.Serial( port, 9600, timeout=0.01, interCharTimeout=None)
                serhdl.flushInput()
                print("Port %s opened" % port )
            except:
                serhdl = 0
                print("Port %s cannot open" % port)
            VisioStat.phndl[i]= serhdl
            i+=1
        VisioStat.pmax = i                     # number of ports scanned

    def readport( self ):                          # poll for 1000 times, return if data received
    
        loops = 0
        while loops<200:
     
            i=0
            while i<VisioStat.pmax:
                hd = VisioStat.phndl[i]
                if hd==0:                       # port is not open!
                    i +=1
                    continue
               
                s  = VisioStat.pbuff[i]        # buffered stream from i-th port
                try:
                    n = hd.inWaiting()          # number of bytes waiting in i-th port
                except:
                    VisioStat.phndl[i]= 0       # port out of service
                    return (i, hd.name, "! Out of service")
                    i +=1
                    continue
                    
                if n>0:
                    try:
                        new = (hd.read(1)).decode("utf-8")
                        if new=='\r':
                            VisioStat.pbuff[i] =""
                            # print("RECEIVED at ", hd.name, "STRING: ", s )
                            return (i, hd.name, s )
                        elif new=='\n':
                            pass
                        else:
                            VisioStat.pbuff[i] =s+new
                    except:
                        pass                    # ignore decoding errors
                    
                else:
                    time.sleep(0.01)
                i+=1
            loops+=1
        return (-1,"","")                      # this means that 100 loops were done

    def closeall( self ):                       # poll for 1000 times, return if data received
        i = 0
        while i<VisioStat.pmax:
            serhdl = VisioStat.phndl[i]
            if serhdl !=0:
                serhdl.close()
            i+=1
    
class open1Port:                    
    serhdl = 0  
    def __init__( self, pname ):
        try:
            self.serhdl = serial.Serial( pname, 9600, timeout=3 )
            self.serhdl.flushInput()
            print("Port %s opened" % pname )
        except:
            self.serhdl = 0
            print("Port %s cannot open" % pname)
    
    def close1Port( self ):
        if self.serhdl:
            self.serhdl.close()

    def read1Port( self ):                      # poll for 1000 times, return if data received
        hd = self.serhdl
        try:
            raw = (hd.readline()).decode("utf-8")
            if raw.index('\n')>=0:
                raw = raw[:-1]
            return (0, hd.name, raw )          # 0 means no errors
        except:
            return (-1,"","")                  # this means timeout waiting for data
            

def toeng( s ):   #   decodes Visiostat data and returns engineering values
    
    # Expacted format is III,CCC,X,VVV
    #   III= S/N, CCC=0-255 wrap-around counter, X=scale, VVV=value
    
    BLANK = "    "
    if len( s ) <13:
        return (-2, BLANK, 0.0, 0)
        
    dec = re.split( ',', s)            

    if len( dec ) <4:
        return (-3, BLANK, 0.0, 0)    
    try:
        serial  = int(dec[0])
        seq     = int(dec[1])
        scale   = int(dec[2])
        value   = int(dec[3])
    except:
        return (-4, BLANK, 0.0, 0)    # -3 "implies error in decoding"


    if scale == 0:                  # 0...25 uA
        max = 25
        feng = value*max/255.0
        seng = '%4.0f'%feng
    elif scale == 1:                # 0...16.6 uA
        max = 16.666
        feng = value*max/255.0
        seng = '%4.0f'%feng
    elif scale == 2:                # 0.0 - 10.0 uA
        max = 10.0
        feng = value*max/255.0            
        seng = '%4.1f'%feng
    elif scale == 3:                # 0.0 - 5.0 uA
        max = 5
        feng = value*max/255.0            
        seng = '%4.1f'%feng      
    elif scale == 4:                # 0.0 - 2.5 uA
        max = 2.5
        feng = value*max/255.0            
        seng = '%4.1f'%feng
    elif scale == 5:                # 0.00 - 2 uA
        max = 2
        feng = value*max/255.0            
        seng = '%4.2f'%feng
    elif scale == 6:                # 0.00 - 1 uA
        max = 1
        feng = value*max/255.0            
        seng = '%4.2f'%feng
    else:                           # 0.00 - 0.5 uA
        max = 0.5
        feng = value*max/255.0
        seng = '%4.2f'%feng
    
    return (serial, seng, feng, value)
                
if __name__ == "__main__":
    import sys

# If command arguments do not work, check registry HKEY_CLASSES_ROOT\Applications\. use: "D:\PYZO\python.exe" "%1" %*
 
#     print( "Command args: sys.argv" )
#     
#     if len(sys.argv)>1:
#         ports = sys.argv[1:]
#     else:
#         ports = ['COM14', 'COM15', 'COM16']     # settings of my machine
#         
#     vs = VisioStat( ports )
#     print("Scanning %s ports" % vs.pmax )
#     
#     for (name,s) in vs.readport():
#         print(name, s, vs.toeng(s)[0] )
#         time.sleep(0.01)

    ports = ['COM4'] 
    vs = VisioStat( ports )
     
    while True:
        (indx, name, s) = vs.readport()
        if indx >=0:
            print(name, s, toeng(s)[1] )
        time.sleep(0.01)
        


        
    
 

