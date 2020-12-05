#!/usr/bin/env python3
import sys
import time
import json

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

#
#   A distillation of Dropbox's python-api examples. 
#   
#   What little original code that may exist here is 
#   Copyright (c) [2020] [Coburn Wightman]
#

# feel free to use this app key.
# But understand it might go away sometime, either intentionally or by mistake.
# Any inconvience that may cause is your own fault

APP_KEY = 'rdouezhyvocju81'
CONFIG_FILE_NAME = 'dbx-xfr.cfg'

class AWConfig(object):
    DEFAULT_CONFIG = {'_app_key':APP_KEY, '_refresh_token':None}
    
    def __init__(self):
        self._app_key = APP_KEY
        self._refresh_token = None
        try:
            self.load_config()
        except FileNotFoundError:
            self.persist_config()
        return

    def load_config(self):
        with open(CONFIG_FILE_NAME, 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = self.DEFAULT_CONFIG
            finally:
                self.__dict__.update(config)
                
        return

    def persist_config(self):
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

class AWDropBox(object):
    def __init__(self):
        self.config = AWConfig()
        return
    
    def __enter__(self):
        self.dbx = dropbox.Dropbox(oauth2_refresh_token=self.config.refresh_token, app_key=self.config._app_key )
        return self
    
    def __exit__(self, *args):
        self.dbx.close()
        return

    def status(self):
        self.dbx.users_get_current_account()
        return True

    def put(self, filename):
        if not self.status():
            print('ERROR: no connection to dropbox account')
            return False

        # Uploads contents of LOCALFILE to Dropbox
        with open(filename, 'rb') as f:
            # We use WriteMode=overwrite to make sure that the settings in the file
            # are changed on upload
            try:
                filename = '/' + filename
                mode = dropbox.files.WriteMode.overwrite
                self.dbx.files_upload(f.read(), filename, mode=mode)
            except dropbox.exceptions.ApiError as err:
                # This checks for the specific error where a user doesn't have
                # enough Dropbox space quota to upload this file
                if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
                    print("ERROR: copy failed; insufficient space.")
                    return False
                elif err.user_message_text:
                    print(err.user_message_text)
                    return False
                else:
                    print(err)
                    return False

        return True



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Puts a file on dropbox.')
        print('Usage: python3 dbx_put.py filename.ext')
        exit(0)
        
    filename = sys.argv[1]
    print('filename is {}'.format(filename))
    
    with AWDropBox() as awd:
        if not awd.status():
            print('Failed to connect to dropbox')
            exit()

        datestamp = time.strftime("%Y-%b-%d %H:%M:%S +0000", time.gmtime())
        print('{}: Uploading {} to dropbox...'.format(datestamp, filename))
        awd.put(filename)
        print('{}: Upload complete.'.format(datestamp))
        print('success?')
