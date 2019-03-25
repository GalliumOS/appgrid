# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GObject, GLib

import gi
gi.require_version('GnomeKeyring', '1.0')
from gi.repository import GnomeKeyring as gk  # nopep8


class AccountManager(GObject.GObject):

    __gsignals__ = {'signedin': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
                    'signedout': (GObject.SignalFlags.RUN_FIRST, None, ()),
                    'failed': (GObject.SignalFlags.RUN_FIRST, None, (str,)), }

    def __init__(self):
        GObject.GObject.__init__(self)

        self.oauth = {}
        self.state = 'unknown'

        GLib.idle_add(self.find_credentials)

    def find_credentials(self):
        """ Check to see if the credentials are stored in the keyring. """
        for i in gk.list_item_ids_sync('login')[1]:
            info = gk.item_get_info_sync('login', i)[1]
            if info and info.get_display_name() == 'App Grid':
                from urllib.parse import parse_qsl
                self.oauth = dict(parse_qsl(info.get_secret()))

        if self.oauth:
            self.verify_credentials()
        else:
            self.set_state('signedout')

    def verify_credentials(self):
        """ Check that the credentials are valid and note the user's name. """
        # unfortunately the v2 api doesn't provide the username which will
        # presumably be required for more advanced rnr operations
        # https://login.ubuntu.com/api/1.0/accounts?ws.op=me
        from appdata.helpers import request
        url = 'https://login.ubuntu.com/api/v2/accounts/%s'
        req = request(url % self.oauth.get('openid', ''),
                      asyn=True, cache=0, oauth=self.oauth)

        def on_downloaded(widget, content):
            import json
            data = json.loads(content or '{}')
            if data.get('displayname'):
                self.set_state('signedin', data.get('displayname'))
            elif data:
                self.signout()
        req.connect('downloaded', on_downloaded)
        req.download()

    def signin(self, email, password, otp=''):
        """ Sign with your Ubuntu SSO and store your credentials. """
        from appdata.helpers import request
        data = {'email': email, 'password': password, 'token_name': 'App Grid'}
        if otp:
            data['otp'] = otp
        req = request('https://login.ubuntu.com/api/v2/tokens/oauth',
                      asyn=True, cache=0, content_type='json', data=data)

        def on_downloaded(widget, content):
            import json
            data = json.loads(content or '{}')
            if data.get('token_name'):
                self.oauth = data
                from urllib.parse import urlencode
                gk.item_create_sync('login', gk.ItemType.GENERIC_SECRET,
                                    'App Grid', gk.Attribute.list_new(),
                                    urlencode(self.oauth), True)
                self.verify_credentials()
            else:
                self.emit('failed', data.get('code') or '?')
        req.connect('downloaded', on_downloaded)
        req.download()

    def signout(self):
        """ Sign out and stop storing your credentials. """
        self.oauth = {}
        for i in gk.list_item_ids_sync('login')[1]:
            info = gk.item_get_info_sync('login', i)[1]
            if info and info.get_display_name() == 'App Grid':
                gk.item_delete_sync('login', i)
        self.set_state('signedout')

    def get_state(self):
        return self.state

    def set_state(self, state, displayname=''):
        if state == 'signedin':
            self.state = state + ':' + displayname
            self.emit(state, displayname)
        elif state == 'signedout':
            self.state = state
            self.emit(state)

    def get_oauth(self):
        return self.oauth


am = AccountManager()
