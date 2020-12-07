#!/usr/bin/env python3
import sys
import time
import socket

import dbx_xfr as dbx

#
#   A distillation of Dropbox's python-api examples. 
#   
#   What little original code that may exist here is 
#   Copyright (c) 2020 Coburn Wightman
#


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Puts a file on dropbox.')
        print('Usage: python3 dbx_put.py filename.ext')
        exit(0)
        
    filename = sys.argv[1]
    
    with dbx.DropBox() as db:
        hostname = socket.gethostname()
        db.path = '/{}'.format(hostname)
        print('uploading {} to {} dropbox folder'.format(filename, db.path))
        
        if not db.status:
            print('Failed to connect to dropbox')
            exit()

        datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
        print('{}: Uploading {} to dropbox...'.format(datestamp, filename))
        db.put(filename)
        print('{}: Upload complete.'.format(datestamp))
        print('success?')
