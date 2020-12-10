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
import requests

# feel free to use this app key.
# But understand it might go away sometime, either intentionally or by mistake.
# Any inconvience that may cause is your own fault

APP_KEY = 'rdouezhyvocju81'
CONFIG_FILE_NAME = 'dbx-xfr.cfg'

class XfrError(Exception):
    pass

class HttpError(XfrError):
    def __init__(self, error):
        self.error = error
        return

    def __repr__(self):
        print(self.body)
        return

class UploadError(XfrError):
    def __init__(self, error):
        self.error = error
        return

    def __repr__(self):
        if (self.error.is_path() and self.error.get_path().reason.is_insufficient_space()):
            # ApiError.error contains dropbox.files.UploadError
            # get_path() returns a dropbox.files.UploadWriteFailed
            # get_path().reason returns a dropbox.files.WriteError
            print('ERROR: copy failed; insufficient space.')
        elif self.error.user_message_text:
            print(self.error.user_message_text)
        else:
            print('ERROR: upload error', self.error)
        return

class DownloadError(XfrError):
    def __init__(self, error):
        self.error = error
        return

    def __repr__(self):
        if (self.error.is_path() and self.error.get_path().is_not_found()):
            # ApiError.error contains dropbox.files.DownloadError
            # error.get_path() returns a file_properties.LookupError
            #print('ERROR: {} not found on dropbox'.format(source))
            print(self.error.get_path())
        else: 
            print('ERROR: download error', self.error)

        return

class Config(object):
    #DEFAULT_CONFIG = {'_app_key':APP_KEY, '_refresh_token':None}

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

    def authenticate(self):
        success = False
        self.app_key = self.get_app_key()
        self._refresh_token = self.get_refresh_token()
        
        if self._refresh_token is not None:
            self.persist()
            success = True
            
        return success

    @property
    def app_key(self):
        return self._app_key

    @app_key.setter
    def app_key(self, key):
        if len(key) > 1:
            self._app_key = key
        return

    def get_app_key(self):
        if self.app_key:
            print('current app_key is {}'.format(self.app_key))
            print('at prompt, enter <cr> to keep existing app_key')

        app_key = input('Enter app_key here: ').strip()
        return app_key

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, token):
        self._refresh_token = token
        return

    def get_refresh_token(self):
        refresh_token = None
        
        auth_flow = DropboxOAuth2FlowNoRedirect(self._app_key, use_pkce=True, token_access_type='offline')
        authorize_url = auth_flow.start()
        
        print()
        print('1. Go to: ' + authorize_url)
        print('2. Click "Allow" (you might have to log in first).')
        print('3. Copy the authorization code.')
        auth_code = input('Enter the authorization code here: ').strip()

        try:
            oauth_result = auth_flow.finish(auth_code)
            refresh_token = oauth_result.refresh_token
        except Exception as e:
            print('Error: %s' % (e,))

        return refresh_token

class Dropbox(object):
    def __init__(self):
        self.config = Config()
        self.dbx = None
        self._path = '/'
        return

    def __enter__(self):
        refresh_token = self.config.refresh_token
        app_key = self.config.app_key

        self.dbx = dropbox.Dropbox(oauth2_refresh_token=refresh_token, app_key=app_key)
        return self

    def __exit__(self, *args):
        self.dbx.close()
        self.dbx = None
        return

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        str.strip(path, '/\\')
        path = os.path.join('/', path)
        self._path = path
        return

    @property
    def status(self):
        status = False

        try:
            self.dbx.users_get_current_account()
            status = True
        except dropbox.exceptions.HttpError as err:
            #raise HttpError(err) from None
            pass

        return status

    def authenticate(self):
        success = self.config.authenticate()
        return success

    def put(self, filename, local_path='.'):
        success = False
        
        source = os.path.join(local_path, filename)
        destination = os.path.join(self.path, os.path.basename(filename))

        # Upload contents of source to Dropbox
        with open(source, 'rb') as f:
            # We use WriteMode=overwrite to make sure that the settings in the file
            # are changed on upload
            mode = dropbox.files.WriteMode.overwrite
            try:
                self.dbx.files_upload(f.read(), destination, mode=mode)
                success = True
            except requests.exceptions.HTTPError as err:
                raise HttpError(err) from None
            except dropbox.exceptions.HttpError as err:
                raise HttpError(err) from None
            except dropbox.exceptions.ApiError as err:
                raise UploadError(err.error) from None

        return success

    def get(self, filename, local_path='.'):
        success = False
        
        source = os.path.join(self.path, filename)
        destination = os.path.join(local_path, filename)

        try:
            md = self.dbx.files_download_to_file(destination, source)
            success = True
        except requests.exceptions.HTTPError as err:
            raise HttpError(err) from None
        except dropbox.exceptions.HttpError as err:
            raise HttpError(err) from None
        except dropbox.exceptions.ApiError as err:
            raise DownloadError(err.error) from None
        
        return success

if __name__ == '__main__':
    db = Dropbox()
    if not db.authenticate():
        print('authenticate failed')

    with Dropbox() as db:
        if db.status:
            print('connected.')
        else:
            print('Failed to connect to dropbox')

    exit()


