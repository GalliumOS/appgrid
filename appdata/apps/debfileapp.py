# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from appdata import _
from appdata.apps import BaseApp


class DebFileApp(BaseApp):
    def __init__(self, filename):
        BaseApp.__init__(self)

        self._filename = filename

        import subprocess

        self._control = subprocess.check_output(['dpkg-deb', '-f', filename],
                                                stderr=subprocess.STDOUT
                                                ).decode('utf8').split('\n')

        self._filenames = subprocess.check_output(['dpkg-deb', '-c', filename],
                                                  stderr=subprocess.STDOUT
                                                  ).decode('utf8').split('\n')
        self._filenames = [line.split(' ')[-1] for line in self._filenames]

        desktop_path = ''
        for _filename in self._filenames:
            if ((_filename.startswith('./usr/share/applications') or
                 _filename.startswith('./opt')) and
                    _filename.endswith('.desktop')):
                if (desktop_path and
                        len(_filename.split('/')[-1].split('.desktop')[0]) <=
                        len(desktop_path.split('/')[-1].split('.desktop')[0])):
                    desktop_path = _filename
                elif not desktop_path:
                    desktop_path = _filename

        import os
        if desktop_path and os.path.getsize(self._filename) < 32000000:
            if os.path.exists('/tmp/appgrid'):
                import shutil
                shutil.rmtree('/tmp/appgrid')
            else:
                os.mkdir('/tmp/appgrid')
            subprocess.check_output(['dpkg-deb', '-x', filename,
                                    '/tmp/appgrid'], stderr=subprocess.STDOUT)
            import codecs
            f = codecs.open('/tmp/appgrid' + desktop_path[1:], 'r', 'utf8')
            self._desktop = f.readlines()
            f.close()
        else:
            self._desktop = []

    def get_control(self, key):
        i = 0
        answer = ''
        while i < len(self._control):
            line = self._control[i]
            if line.startswith(key + ': '):
                answer = line.split(': ')[1]
                j = 1
                while i + j < len(self._control):
                    otherline = self._control[i + j]
                    if otherline.startswith(' '):
                        answer += '\n' + otherline
                    else:
                        break
                    j += 1
            i += 1
        return answer.rstrip(';')

    def get_desktop(self, key):
        for line in self._desktop:
            if line.startswith(key + '='):
                return line.split('=')[1].rstrip('\n').rstrip(';')
        return ''

    @property
    def description(self):
        """ String containing the description of the application. """
        # FIXME: deal with other types of bullet points
        description = ''
        for line in self.get_control('Description').split('\n')[1:]:
            if line.strip() == '.':
                if description:
                    description += '\n\n'
            elif line.startswith('  '):
                if (not line.lstrip().startswith('* ') and
                        description.split('\n')[-1].startswith('* ')):
                    description += ' ' + line.lstrip()
                elif description.endswith('\n'):
                    description += line[2:]
                else:
                    description += '\n' + line[2:]
            elif line.startswith(' * '):
                # meh - people not following the debian policy
                if description.endswith('\n'):
                    description += line[1:]
                else:
                    description += '\n' + line[1:]
            elif line.startswith(' '):
                if not description or description.endswith('\n'):
                    description += line[1:]
                else:
                    description += line
        return description

    @property
    def id(self):
        """ String containing the unique identifier of the application. """
        return self.get_control('Package')

    # keywords not used

    @property
    def license(self):
        """ String containing the license of the application. """
        return _("Unknown")

    @property
    def name(self):
        """ String containing the display name of the application. """
        return (self.get_desktop('Name') or
                ' '.join([w.capitalize() for w in self.id.split('-')]))

    @property
    def origin(self):
        """ String containing the display name of the origin. """
        return _("Unknown")

    @property
    def state(self):
        """ String containing the current state of the application. Should use
            the predefined values. """
        return 'available'

    @property
    def summary(self):
        """ String containing the summary of the application. """
        return (self.get_desktop('Comment') or
                self.get_control('Description').split('\n')[0])

    @property
    def version(self):
        """ List containing strings representing the available and the
            installed version number of the application. """
        return [self.get_control('Version'), '']

    @property
    def website(self):
        """ String containing the website of the application. """
        return self.get_control('Homepage')
