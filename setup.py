# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
import os
import sys
from DistUtilsExtra.auto import setup

if len(sys.argv) >= 2 and sys.argv[1] == 'clean':
    import urllib.request
    import gzip

    u = 'http://archive.ubuntu.com/ubuntu/dists/%s/%s/binary-i386/Packages.gz'

    for release in ['xenial', 'bionic', 'cosmic', 'disco']:
        blacklist = []
        for comp in ['main', 'restricted', 'universe', 'multiverse']:
            data = gzip.GzipFile(fileobj=urllib.request.urlopen(
                u % (release, comp))).readlines()
            for line in data:
                if line.startswith(b'Package: '):
                    p = line.split(b'Package: ')[1]
                elif line.startswith(b'Description: '):
                    d = line.split(b'Description: ')[1].lower()
                    if (b'transitional package' in d or
                            b'transitional dummy package' in d):
                        blacklist.append(p.decode('utf8').strip())
        f = open('blacklist-%s.json' % release, 'w')
        import json
        f.write(json.dumps(blacklist))
        f.close()

setup(name='appgrid',
      version='0.1',
      scripts=['appgrid'],
      packages=['appdata', 'appdata.apps', 'widgets'],
      data_files=[
          ('/lib/systemd/system', ['debian/appgrid.service']),
          ('/usr/share/appgrid', ['LEGAL', 'accountmanager.py', 'appdata.py',
                                  'appgrid.css', 'appgrid.py']),
          ('/usr/share/appgrid', [g for g in os.listdir() if
                                  g.startswith('blacklist-') and
                                  g.endswith('.json')]),
          ('/usr/share/appgrid/data', ['data/99appgrid', 'data/appgrid',
                                       'data/appgrid.conf']),
          ('/usr/share/applications', ['appgrid.desktop']),
          ('/usr/share/apport/package-hooks/', ['data/source_appgrid.py']),
      ],
      )
