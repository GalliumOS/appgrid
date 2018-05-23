# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from appdata import _
from appdata.apps import BaseApp


class SQLiteApp(BaseApp):
    def __init__(self, row):
        self._row = row

    @property
    def addons(self):
        """ List of Application objects which are considered to be addons of
            the application. """
        addons = self._row[0]
        if addons:
            return addons.split(';')
        return []

    @property
    def category(self):
        """ String containing the category in which the application can be
            found. May be suffixed by ;subcategory. """
        return self._row[1]

    @property
    def description(self):
        """ String containing the description of the application. """
        return self._row[2]

    @property
    def id(self):
        """ String containing the unique identifier of the application. """
        return self._row[6]

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
        return self._row[4]

    @property
    def origin(self):
        """ String containing the display name of the origin. """
        id = self.origin_id
        if id == 'U' or id.startswith('U/'):
            return _("Ubuntu")
        elif id.startswith('S/'):
            return _("Canonical Store")
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
        return self._row[5]

    @property
    def rating(self):
        """ Integer representing the average rating of the application. """
        return self._row[7] or 0

    @property
    def state(self):
        """ String containing the current state of the application. Should use
            the predefined values. """
        return {'': 'available',
                'i': 'installed'}[self._row[8]]

    @property
    def summary(self):
        """ String containing the summary of the application. """
        return self._row[9]

    @property
    def version(self):
        """ List containing strings representing the available and the
            installed version number of the application. """
        return self._row[11].split(';')

    @property
    def website(self):
        """ String containing the website of the application. """
        return self._row[12]
