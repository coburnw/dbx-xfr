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

def usage():
    print('Dropbox file transfer.')
    print('Usage: python3 dbx.py pair')
    print('       python3 dbx.py put filename.ext')
    print('       python3 dbx.py get filename.ext')
    return

def put(db, filename):
    success = False

    print('uploading {} to {} dropbox folder'.format(filename, db.path))
    datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
    print('{}: Upload begun...'.format(datestamp))
    
    try:
        db.put(filename)
        print('{}: Upload complete.'.format(datestamp))
        success = True
    except dbx.XfrError as err:
        datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
        print('{}: Upload failed. {}'.format(datestamp, err))
    except FileNotFoundError:
        datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
        print('{}: Upload failed. {}'.format(datestamp, 'file not found.'))
        
    return success

def get(db, filename):
    success = False
    
    print('downloading {} from {} dropbox folder'.format(filename, db.path))
    datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
    print('{}: Download begun...'.format(datestamp))

    try:
        db.get(filename)
        print('{}: Download complete.'.format(datestamp))
        success = True
    except dbx.XfrError as err:
        datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
        print('{}: Download failed. {}'.format(datestamp, err))
        
    return success

def pair():
    success = False
    config = dbx.Config()
    config.authenticate()

    with dbx.DropBox() as db:
        if db.status:
            print('connected.')
            success = True
        else:
            print('Failed to connect to dropbox')
            
    return success

if __name__ == '__main__':
    if len(sys.argv) == 1:
        status = 1
        usage()
        exit(status)

    command = sys.argv[1].lower()
    if len(sys.argv) == 2:
        status = 2
        if command == 'pair':
            if pair():
                status = 0
        else:
            usage()

    elif len(sys.argv) == 3:
        status = 3
        filename = sys.argv[2]
        with dbx.DropBox() as db:
            hostname = socket.gethostname()
            db.path = '/{}'.format(hostname)
            if command == 'get':
                if get(db, filename):
                    status = 0
            elif command == 'put':
                if put(db, filename):
                    status = 0
            else:
                print('unrecognized command: {}.'.format(command))
                usage()
            
    exit(status)
