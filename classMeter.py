from tkinter import *
import math

# window dimensions are: WIDTH = 2*(XMARG+R), HEIGHT = BMARG+TMARG+R

TMARGIN = 60    # top margin in pixels  
BMARGIN = 40    # bottom margin in pixels
XMARGIN = 50    # left and right horizontal margin in pixel
DELTA   = 12    # size of the tic marks
MAXA    = 1.2   # in radiants. Needle moves from -MAXA to +MAXA
NTICS   = 20    # minor tics
MTICS   =  5    # major tics

class meter:
    """Class to display and control a METER widget."""
    w   = None
    org = None
    R   = None
    t1, t2, t3, t4 = None, None, None, None

    RANGE= [ ['0','20','40','60','80','100'],\
             ['0', '5','10','15','20', '25'],\
             ['0','10','20','30','40','50' ]]

    TICSP= [20,25,25]               # number of minor tic marks
    TICMX= [5, 5, 5 ]               # number of major tic marks
    maxsc = {100:0, 25:1, 50:2}     # associative array of max values
    scale = None                    # takes values 0, 1 or 2 as an index of the arays above
    
    def __init__( self, master, note, row=0, col=0, radius=150, maxscale=100 ):
        """Constractor displaying the METER using positioning parameters.
        
        master = as returned by Tk
        note = string displayed at the panel of the METER
        [radius] = size of the needle in pixels. Use 70...200
        [gridr], [gridc] = optional grid row and column
        [maxscale]  = maximum value indicated by the meter. Must be 100, 25 or 50

        """
        self.R = radius
        self.org = (XMARGIN+self.R, self.R+TMARGIN)

        self.scale = maxscale
        indsc = self.maxsc[ maxscale ]
        self.num   = self.RANGE[ indsc ]  
               
        self.w = Canvas( master, width = 2*(XMARGIN+self.R), height=BMARGIN+self.R+TMARGIN )
        self.w.grid( row=row, column=col )

        self.w.create_rectangle( (0+4, BMARGIN+self.R+TMARGIN-4, 2*(XMARGIN+self.R)-4, 0+4 ), width=3, fill='mint cream')
        
        self._drawradial( -MAXA )       # initial position (from -MAXA to +MAXA)
        self._drawnote( note )
        self._drawcircle( 5 )
        self._drawticks()
        self._drawscale()
        
        self.w.update()

    def update( self, value  ):
        """Updates the METER to a new position specified by 'value', using 'format'."""
        percent = value*100.0/self.scale
        angle = -MAXA + percent*2*MAXA/100.0
        self._drawradial( angle )
        self.w.update()
        
    def _drawnote( self, str ):     # displays the numeric value on the face of the meter
        self.w.delete( self.t4 )
        if self.R > 100:            # smart change of the font size
            siz = 18
        else:
            siz = 12
        self.t4 = self.w.create_text( (self.org[0], TMARGIN+self.R/2), text=str, \
        justify='center', fill="blue", font=("Arial", siz))
    
    def _drawradial( self, a ):     # draws the needle to a specific angle from -MAXA to +MAXA in radians
        self.w.delete( self.t1)
        self.w.delete( self.t2)     # erase the previous needle
  
        self.t1 = self.w.create_line( self.org, self._getxy( self.R, a), width=3, fill="red" )
        self.t2 = self.w.create_line( self.org, self._getxy(-self.R*0.1, a), width=5, fill="red" )
        
    def _drawcircle( self, dR ):    # draws a little circle at the origin of the needle
        self.w.create_oval( \
        self.org[0]-dR, self.org[1]-dR, self.org[0]+dR, self.org[1]+dR, fill='red')

    def _drawticks( self ):                 # draws the tic marks
        indsc = self.maxsc[self.scale]      # get the index of the tic marks
        MTICS = self.TICMX[ indsc ]         # major tic marks
        NTICS = self.TICSP[ indsc ]         # minor tic marks
        
        i = 0
        a = -MAXA
        da = 2.0 * MAXA / NTICS
        while i<= NTICS:
            fr = self._getxy( self.R-DELTA, a )
            to = self._getxy(     self.R, a )
            self.w.create_line( fr, to, fill="black" )    
            i += 1
            a += da

        i = 0
        a = -MAXA
        da = 2.0 * MAXA / MTICS
        while i<= MTICS:
            fr = self._getxy(  self.R-DELTA, a )
            to = self._getxy(  self.R+DELTA, a )
            self.w.create_line( fr, to, fill="black", width=3 )    
            i += 1
            a += da
            
    def _drawscale( self ):     # draws the scale of the instrument
        indsc = self.maxsc[self.scale]      # get the index of the tic marks
        MTICS = self.TICMX[ indsc ]         # major tic marks
 
        a = -MAXA
        da = 2.0 * MAXA / MTICS
        i = 0
        while i<=MTICS:
            self.w.create_text( self._getxy( self.R+2*DELTA, a ), text=self.num[i], fill='black', justify='center' ) 
            a += da
            i += 1

    def _getxy( self, R, angle ):   # helper function to return the (x,y) coordinates of a given R and angle
        return \
        ( self.org[0]+R*math.sin(angle), self.org[1]-R*math.cos(angle) )
            
# -------------------------------------------------------------------------------------------------------------
def main():            
    master = Tk()
    m1 = meter( master, "Volts",radius=200, row=0, col=0, maxscale=50)
    m2 = meter( master, "uA",   radius=100, row=0, col=1, maxscale=25)
    m3 = meter( master, "W",    radius=70,  row=1, col=1, maxscale=100)
    
    def doScale(x):     # to get the slider, use sc.get() or the passed argument
        i = int(x)
        m1.update( "%.1fV", i )
        m2.update( "%.1fuA", i )
        m3.update( "%.1fW", i )
        
    sc = Scale(master, from_=0, to=25, orient=HORIZONTAL, length=200, command=doScale)
    #sc = Scale(master, from_=0, to=100, orient=HORIZONTAL, length=200, command=lambda x: m1.update("%.0fV", sc.get()) )
    
    sc.grid( row=1, column=0)

    master.mainloop()


if __name__ == '__main__':
    main()
