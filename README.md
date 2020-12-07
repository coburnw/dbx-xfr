# dbx-xfr
Dead simple dropbox file transfer library in Python

# Description
A dead simple python library for getting and putting files on Dropbox.  Heavily leans on example code found in the dropbox [python sdk](https://github.com/dropbox/dropbox-sdk-python)

On first run, leads the user thru the pairing sequence allowing the app access to the users dropbox Apps/dbx-xfr folder with file read/write access, and saves the refresh token returned by dropbox in a config file in the apps directory.  On subsequent runs, the refresh token is retrieved from the config file without need of user intervention unless the refresh token has be invalidated for some reason.

Developed and tested on raspberry pi zero with python 3.7.3

# Dependencies
pip3 install dropbox
python3

# Example
    import dbx_xfr as dbx
    
    filename = 'junk.txt'
    
    with dbx.DropBox() as db:
       if db.put(filename):
          print('success')
       else:
	  print('failure')
