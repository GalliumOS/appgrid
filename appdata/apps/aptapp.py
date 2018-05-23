# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from appdata import _, d_
from appdata.apps import BaseApp
from appdata.categories import get_cat_for_pkg, get_cat_for_app

from apt.cache import Cache
import os
import re

addons = {}
cache = Cache()


class AptApp(BaseApp):
    def __init__(self, pkgname, force=False, desktop=None):
        if force:
            cache.open()
        self._pkg = cache[pkgname]
        self._pkgc = self._pkg.candidate or self._pkg.installed
        self._pkgname = pkgname
        self._desktop = ''
        if desktop:
            if os.path.exists('/usr/share/applications/' + desktop):
                path = '/usr/share/applications/' + desktop
            elif os.path.exists('/usr/share/app-install/desktop/' + desktop):
                path = '/usr/share/app-install/desktop/' + desktop
            if path:
                try:
                    f = open(path)
                    self._desktop = f.read()
                    f.close()
                except:
                    pass

    def get_field(self, key):
        try:
            return re.findall(r'\n%s=(.*)\n' % key, self._desktop)[0]
        except IndexError:
            return ''

    @property
    def addons(self):
        """ List of Application objects which are considered to be addons of
            the application. """
        if self._pkgname in addons:
            return addons[self._pkgname]
        else:
            return []

    @property
    def category(self):
        """ String containing the identifiers of the category and subcategory
            in which the application can be found separated by a ';'. """
        if self._desktop:
            return get_cat_for_app(self.get_field('Categories').rstrip(';'))
        return get_cat_for_pkg(self._pkgc.section.split('/')[-1],
                               self._pkgname)

    @property
    def description(self):
        """ String containing the description of the application. """
        return self._pkgc.description
        # FIXME: format the bullet points nicely

    @property
    def id(self):
        """ String containing the unique identifier of the application. """
        return self._pkgname

    @property
    def keywords(self):
        """ List of keywords identifying the application. """
        if self._desktop:
            keywords = self.get_field('Keywords')
            if keywords:
                return d_('app-install-data',
                          keywords).rstrip(';').lower().split(';')
        return []

    @property
    def license(self):
        """ String containing the license of the application. """
        origin = self.origin_id
        if '/' in origin:
            o = origin.split('/')[0]
            c = origin.split('/')[1]
            if o == 'U' and c in ['M', 'U']:
                return _("Open Source")
            if o == 'U' and c in ['R', 'V']:
                return _("Proprietary")
        if origin == 'P':
            return _("Proprietary")
        return _("Unknown")

    @property
    def name(self):
        """ String containing the display name of the application. """
        if self._desktop:
            n = d_('app-install-data', (
                self.get_field('X-GNOME-FullName') or
                self.get_field('Name')))
            if n:
                return n
        return ' '.join([w.capitalize() for w in self._pkgname.split('-')])

    @property
    def origin(self):
        """ String containing the display name of the origin. """
        id = self.origin_id
        if id == 'U' or id.startswith('U/'):
            return _("Ubuntu")
#        elif id.startswith('S/'):
#            return _("Canonical Store")
        elif id == 'P':
            return _("Canonical Partners")
        elif id == 'E':
            return _("Ubuntu Extras")
        if ';' in id:
            return id.split(';')[1]
        return _("Unknown")

    @property
    def origin_id(self):
        """ String identifying the origin of the application. """
        o = self._pkgc._cand.file_list[0][0]
        origin = o.origin
        if origin == 'Ubuntu':
            return 'U/' + {'main': 'M',
                           'universe': 'U',
                           'restricted': 'R',
                           'multiverse': 'V'}[o.component]
        if origin == 'Canonical':
            return 'P'
#        if origin.startswith('LP-PPA-commercial-ppa-uploaders-'):
#            return 'S'
        if origin == 'LP-PPA-app-review-board':
            return 'E'
        label = o.label
        if label:
            origin += ';' + label
        return origin or 'Unknown'

    @property
    def state(self):
        """ String containing the current state of the application. Should use
            the predefined values. """
        if self._pkg.is_installed:
            return 'installed'
        return 'available'

    @property
    def summary(self):
        """ String containing the summary of the application. """
        if self._desktop:
            s = d_('app-install-data', self.get_field('Comment'))
            if s:
                return s
        return self._pkgc.summary

    @property
    def version(self):
        """ List containing strings representing the available and the
            installed version number of the application. """
        if self._pkg.installed:
            return [self._pkgc.version, self._pkg.installed.version]
        else:
            return [self._pkgc.version, '']

    @property
    def website(self):
        """ String containing the website of the application. """
        return self._pkgc.homepage


suffs = ['dbg', 'doc', 'dev', 'data', 'base', 'common', 'examples', 'tools',
         'gtk', 'bin', 'server', 'core', 'gui', 'plugins', 'utils', 'extra',
         'mysql', 'client', 'el', 'lib']


def strip(pkgname, rear=True):
    if not rear:
        suf = ''
        if '-' in pkgname:
            if pkgname.split('-')[-1] in suffs:
                suf = pkgname.split('-')[-1]
                pkgname = '-'.join(pkgname.split('-')[:-1])
    i = len(pkgname) - 1
    change = False
    while i > 0 and (pkgname[i].isdigit() or pkgname[i] == '.' or
                     pkgname[i] == '-'):
        change = True
        i -= 1
    pkgname = pkgname[:i + 1]
    if not rear:
        if suf:
            pkgname += '+' + suf
        if change and not suf:
            pkgname = pkgname + '"'
        if pkgname.startswith('lib'):
            if change and not suf:
                pkgname = pkgname.replace('"', '#')
            pkgname = pkgname[3:]
    return pkgname


def is_digits(text):
    for t in text:
        if not (t.isdigit() or t == '.' or t == '-'):
            return False
    return True


def get_apt_pkgnames():
    path = '/usr/share/appgrid/blacklist-%s.json'
    import platform
    import os
    if os.path.exists(path % platform.linux_distribution()[2]):
        filename = path % platform.linux_distribution()[2]
    else:
        filename = path % 'xenial'

    import json
    blacklist = set(json.loads(open(filename).read()))
    keys = cache.keys()
    keys = [k for k in keys if not (':' in k and k.split(':')[0] in cache)]
    keys = sorted(set(keys) - blacklist,
                  key=lambda k: strip(k, rear=False))

    i = 0
    global addons
    to_index = set()
    while i < len(keys):
        ext = set()
        j = 1
        ki = keys[i]
        base = strip(ki)
        if base.startswith('lib'):
            base = base[3:]
            ki = ki[3:]
        source = ''
        while i + j < len(keys):
            ij = keys[i + j]
            if ((ij.startswith(base + '-') and
                    ij.split(base + '-')[1] in suffs) or
                ij.startswith('lib' + base + '-') or
                ij.startswith('lib' + ki + '-') or
                (ij.startswith('lib' + base) and
                    is_digits(ij.split(base)[1])) or
                (ij.startswith('lib' + base) and '-' in ij and
                    is_digits(ij.split(base)[1].split('-')[0])) or
                (ij.startswith(base) and is_digits(ij.split(base)[1])) or
                (ij.startswith(ki + '-') and
                    ij.split(ki + '-')[1] in suffs)):
                ext.add(ij)
                j += 1
            elif ij.startswith(base):
                if not source:
                    try:
                        source = cache[keys[i]].candidate.source_name
                    except:
                        source = ''
                if (source and cache[ij].candidate and
                        source == cache[ij].candidate.source_name):
                    ext.add(ij)
                    j += 1
                else:
                    break
            else:
                break
        if ext:
            addons[keys[i]] = list(ext)
        to_index.add(keys[i])
#        if j == 1:
#            print(keys[i])
#        else:
#            print('*', keys[i], addons[keys[i]])
        i += j
    return to_index


def get_desktop_files():
    filenames = {}
    tmpfilenames = {}
    for filename in sorted(os.listdir('/usr/share/app-install/desktop/')):
        cl = filename.split('.desktop')[0]
        if ':' in cl:
            pkg, des = cl.split(':')
            des = des.lower()
            if des.startswith('kde4__'):
                des = des[6:]
            if pkg == des:
                filenames[pkg] = filename
            elif pkg in tmpfilenames:
                tmpfilenames[pkg].append(filename)
            else:
                tmpfilenames[pkg] = [filename]
        else:
            try:
                f = open('/usr/share/app-install/desktop/' + filename)
                pkg = re.findall(r'\n%s=(.*)\n' % 'X-AppInstall-Package',
                                 f.read())[0]
                filenames[pkg] = filename
                f.close()
            except:
                pass
    for pkg in tmpfilenames:
        if len(tmpfilenames[pkg]) == 1 and pkg not in filenames:
            if (pkg.endswith('-common') and
                    tmpfilenames[pkg][0] == pkg + ':' + pkg[:-7] + '.desktop'):
                filenames[pkg[:-7]] = tmpfilenames[pkg][0]
            elif (pkg.endswith('-data') and
                    tmpfilenames[pkg][0] == pkg + ':' + pkg[:-5] + '.desktop'):
                filenames[pkg[:-5]] = tmpfilenames[pkg][0]
            elif (pkg.endswith('-core') and
                    tmpfilenames[pkg][0] == pkg + ':' + pkg[:-5] + '.desktop'):
                filenames[pkg[:-5]] = tmpfilenames[pkg][0]
            else:
                filenames[pkg] = tmpfilenames[pkg][0]
    for p in ['fretsonfire-game', 'vim-gui-common', 'epiphany-browser-data']:
        if p in filenames:
            del filenames[p]
    for filename in os.listdir('/usr/share/applications/'):
        if filename.endswith('.desktop'):
            pkgname = filename.split('/')[-1].split('.desktop')[0]
            filenames[pkgname] = filename
    return filenames
