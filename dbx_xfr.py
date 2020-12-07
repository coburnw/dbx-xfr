#!/usr/bin/env python3
import sys
import os
import time
import json

#
#   Copyright (c) 2020 Dropbox Inc., http://www.dropbox.com/
#   
#   A distillation of Dropbox's python-api examples. 
#   What little original code that may exist here is 
#   Copyright (c) 2020 Coburn Wightman
#

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

# feel free to use this app key.
# But understand it might go away sometime, either intentionally or by mistake.
# Any inconvience that may cause is your own fault

APP_KEY = 'rdouezhyvocju81'
CONFIG_FILE_NAME = 'dbx-xfr.cfg'

class Config(object):
    DEFAULT_CONFIG = {'_app_key':APP_KEY, '_refresh_token':None}
    
    def __init__(self):
        self._app_key = APP_KEY
        self._refresh_token = None
        try:
            self.load()
        except FileNotFoundError:
            self.persist()
        return

    def load(self):
        with open(CONFIG_FILE_NAME, 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = self.DEFAULT_CONFIG
            finally:
                self.__dict__.update(config)
                
        return

    def persist(self):
        with open(CONFIG_FILE_NAME, 'w') as f:
            json.dump(self.__dict__, f, skipkeys=True, indent=4)

        return

    @property
    def refresh_token(self):
        if self._refresh_token is None:
            self._refresh_token = self.get_refresh_token()
            if self._refresh_token is not None:
                self.persist_config()
        return self._refresh_token

    def get_refresh_token(self):
        auth_flow = DropboxOAuth2FlowNoRedirect(self._app_key, use_pkce=True, token_access_type='offline')
        authorize_url = auth_flow.start()
        
        print()
        print("1. Go to: " + authorize_url)
        print("2. Click \"Allow\" (you might have to log in first).")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()

        try:
            oauth_result = auth_flow.finish(auth_code)
        except Exception as e:
            print('Error: %s' % (e,))
            return None

        return oauth_result.refresh_token

class DropBox(object):
    def __init__(self):
        self.config = Config()
        self._path = '/'
        return
    
    def __enter__(self):
        self.dbx = dropbox.Dropbox(oauth2_refresh_token=self.config.refresh_token, app_key=self.config._app_key )
        return self
    
    def __exit__(self, *args):
        self.dbx.close()
        return

    @property
    def status(self):
        self.dbx.users_get_current_account()
        return True

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        str.strip(path, '/\\')
        path = os.path.join('/', path)
        self._path = path
        return
    
    def put(self, filename):
        if not self.status:
            print('ERROR: no connection to dropbox account')
            return False

        # Uploads contents of filename to Dropbox
        with open(filename, 'rb') as f:
            success = False
            # We use WriteMode=overwrite to make sure that the settings in the file
            # are changed on upload
            try:
                filename = os.path.join(self.path, os.path.basename(filename))
                mode = dropbox.files.WriteMode.overwrite
                self.dbx.files_upload(f.read(), filename, mode=mode)
                success = True
            except dropbox.exceptions.ApiError as err:
                # This checks for the specific error where a user doesn't have
                # enough Dropbox space quota to upload this file
                if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
                    print("ERROR: copy failed; insufficient space.")
                elif err.user_message_text:
                    print(err.user_message_text)
                else:
                    print(err)

        return success

    def get(self, filename, local_path='.'):
        if not self.status:
            print('ERROR: no connection to dropbox account')
            return False

        source = os.path.join(self.path, filename)
        destination = os.path.join(local_path, filename)
        status = False

        try:
            md = self.dbx.files_download_to_file(destination, source)
            status = True
        except dropbox.exceptions.HttpError as err:
            print('ERROR: HTTP error', err)
        except dropbox.exceptions.ApiError as err:
            if (err.error.is_path() and err.error.get_path().is_not_found()):
                print('ERROR: {} not found on dropbox'.format(source))
            else: 
                print('ERROR: download error', err)

        return status


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Puts a file on dropbox.')
        print('Usage: python3 dbx_put.py filename.ext')
        exit(0)
        
    filename = sys.argv[1]
    print('filename is {}'.format(filename))
    
    with DropBox() as db:
        if not db.status:
            print('Failed to connect to dropbox')
            exit()

        datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
        print('{}: Uploading {} to dropbox...'.format(datestamp, filename))
        db.put(filename)
        print('{}: Upload complete.'.format(datestamp))
        print('success?')
