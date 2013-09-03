import sqlite3 as sq
from os.path import isfile, getsize
import time
        
# Checks the file system if the database exists
# Returns 0 if an SQLite database is found

class logDB:

    con = None
    cur = None

    # Opens an SQL database
    
    def __init__( self ):
        pass

    def find( self, filename ):

        if not isfile(filename):
            return 1
        if getsize(filename) < 100: # SQLite database file header is 100 bytes
            return 2
        else:
            fd = open(filename, 'rb')
            Header = fd.read(16)
            fd.close()

        if Header == b'SQLite format 3\x00':
            return 0
        else:
            print("header is", Header )
            return 3

    def connect( self, dbname ):
        e = self.find( dbname )
        if e > 0:
            print("Database ",dbname,"not found. Error", e)
            return e
       
        try:
            con = sq.connect( dbname )
            print("Connected")
            con.row_factory = sq.Row
            cur = con.cursor()
            self.con = con
            self.cur = cur
            return 0;
            
        except sq.Error:
            print("Cannot connect to", dbname )
            return -1
         
    def save( self, portname, sernum, raw, feng, fmin, fmax ):
        tmstamp = time.time()
        t = time.localtime( tmstamp )
        d=( tmstamp, t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, 
            portname, sernum, raw, feng, fmin, fmax )
        # print( d )
            
        self.cur.execute("INSERT INTO EngData VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", d )
        self.con.commit()
    
if __name__ == "__main__":
    db = logDB()
    print( db.find( "VisioLog.sqlite") )
    x = db.connect( "VisioLog.sqlite" )
    
    db.save( "GEO", 100, "test1", 20.3, 1, 2 )
    db.save( "GEO", 200, "test2", 10.1, 3, 4 )

    
