# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
import json
import hashlib
import os
import time

import gi
gi.require_version('Soup', '2.4')
from gi.repository import GLib, GObject, Soup  # nopep8

if os.geteuid() != 0:
    dd = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
    downloads_dir = dd + '/appgrid/'
    os.makedirs(downloads_dir, exist_ok=True)
else:
    downloads_dir = '/tmp/appgrid-downloads/'
ss = Soup.Session()


class Downloadable(GObject.GObject):
    """ Wrapper representing an object that needs downloading. You can detect
        this object by checking if it's equal to 'needs-download'. To download
        the contents first connect to the 'downloaded' signal, then call
        self.download(). The download signal passes an argument which is either
        the filename, or an empty string if the download failed. """

    __gsignals__ = {'downloaded': (GObject.SignalFlags.RUN_FIRST, None,
                                   (str,))}

    def __init__(self, sm, filename, cache):
        GObject.GObject.__init__(self)

        self._sm = sm
        self._filename = filename
        self._cache = cache

    def download(self):
        ss.queue_message(self._sm, self.on_download_complete, None)

    def on_download_complete(self, session, sm, user_data):
        self.emit('downloaded', get_response_from_sm(sm, self._filename,
                                                     self._cache))

    def __eq__(self, other):
        if other == 'needs-download':
            return True
        return False

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return 'needs-download'


def get_response_from_sm(sm, filename, cache):
    cd, d, p = sm.response_headers.get_content_disposition()
    fake404 = cd and 'filename' in p and p['filename'] == 'thumbnail404.png'
    content = sm.response_body.flatten().get_data()
    if (sm.get_property('status-code') != 404 and
            sm.get_property('status-code') < 500 and
            content and not fake404):
        if cache:
            if os.geteuid() == 0:
                if os.path.exists(filename):
                    return filename
                return ''  # never write as root
            f = open(filename, 'wb')
            f.write(content)
            f.close()
            return filename
        else:
            return content.decode('utf8')
    elif os.path.exists(filename):
        if cache:
            return filename
        else:
            import codecs
            return codecs.open(filename, 'r', 'utf8').read()
    return ''


def request(url, asyn=False, oauth=None, data=None, cache=1,
            content_type='x-www-form-urlencoded'):
    if data is None:
        sm = Soup.Message.new('GET', url)
    else:
        sm = Soup.Message.new('POST', url)
        if content_type == 'json':
            sm.request_headers.append('Content-Type', 'application/json')
            sm.request_body.append(json.dumps(data).encode('utf8'))
        elif content_type == 'x-www-form-urlencoded':
            sm.request_headers.append('Content-Type',
                                      'application/x-www-form-urlencoded')
            import urllib.parse
            enc = urllib.parse.urlencode(data or '')
            sm.request_body.append(enc.encode('utf8'))
        cache = 0

    filename = downloads_dir + hashlib.md5(url.encode('utf8')).hexdigest()

    if (cache and os.path.exists(filename) and
            time.time() - os.path.getmtime(filename) < cache * 60 * 60 * 60):
        return filename

    if oauth:
        from oauthlib.oauth1 import Client
        oauth_client = Client(oauth['consumer_key'],
                              oauth['consumer_secret'],
                              oauth['token_key'],
                              oauth['token_secret'],
                              signature_method='PLAINTEXT')
        uri, signed_headers, body = oauth_client.sign(
            url, sm.get_property('method'), sm.request_body, [])
        sm.request_headers.append('Authorization',
                                  signed_headers['Authorization'])

    sm.request_headers.append('Accept-Encoding', 'gzip')

    if asyn:
        return Downloadable(sm, filename, cache)
    else:
        ss.send_message(sm)
        return get_response_from_sm(sm, filename, cache)

#        def _show_header(name, value, data):
#            print(name, value)
#        sm.request_headers.foreach(_show_header, None)
#        print(sm.get_property('status-code'))
#        return r
