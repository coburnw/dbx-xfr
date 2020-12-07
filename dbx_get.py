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
        print('Gets a file from dropbox.')
        print('Usage: python3 dbx_get.py filename.ext')
        exit(1)
        
    filename = sys.argv[1]
    
    with dbx.DropBox() as db:
        hostname = socket.gethostname()
        db.path = '/{}'.format(hostname)
        print('downloading {} from {} dropbox folder'.format(filename, db.path))
        
        if not db.status:
            print('Failed to connect to dropbox')
            exit(2)

        datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
        print('{}: Downloading {} from dropbox...'.format(datestamp, filename))
        if db.get(filename):
            print('{}: Download complete.'.format(datestamp))
            status = 0
        else:
            print('download failed')
            status = 3

    exit(status)
