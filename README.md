# dbx-xfr
Dead simple Dropbox file transfer library in Python

# Description
A simple python library for getting files on and off Dropbox.  Heavily leans on example code found in the dropbox [python sdk](https://github.com/dropbox/dropbox-sdk-python)

On first run, leads the user thru the pairing sequence allowing the app access to the users dropbox Apps/dbx-xfr folder with file read/write access, saving the refresh token returned by dropbox in a config file in the local directory.  On subsequent runs, the refresh token is retrieved from the config file without need of user intervention unless the file or the token has be invalidated in some way.

Developed and tested on Raspberry Pi Zero with Python 3.7.3

# Dependencies
pip3 install dropbox

# Example
    import dbx_xfr as dbx
    
    filename = 'junk.txt'
    
    with dbx.DropBox() as db:
       if db.put(filename):
          print('success')
       else:
          print('failure')
