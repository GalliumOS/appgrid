# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file


class BaseApp(object):
    def __init__(self):
        pass  # for test suite

    @property
    def addons(self):
        """ List of Application objects which are considered to be addons of
            the application. """
        return []

    @property
    def category(self):
        """ String containing the identifiers of the category and subcategory
            in which the application can be found separated by a ';'. """
        return ''

    @property
    def description(self):
        """ String containing the description of the application. """
        return ''

    @property
    def id(self):
        """ String containing the unique identifier of the application. """
        return ''

    @property
    def keywords(self):
        """ List of keywords identifying the application. """
        return []

    @property
    def license(self):
        """ String containing the license of the application. """
        return ''

    @property
    def name(self):
        """ String containing the display name of the application. """
        return self.id

    @property
    def origin(self):
        """ String identifying the origin of the application. """
        return 'Unknown'

    @property
    def origin_id(self):
        """ String identifying the origin of the application. """
        return ''

    @property
    def rating(self):
        """ Integer representing the average rating of the application. """
        return 0

    @property
    def state(self):
        """ String containing the current state of the application. Should use
            the predefined values. """
        return 'available'

    @property
    def summary(self):
        """ String containing the summary of the application. """
        return ''

    @property
    def version(self):
        """ List containing strings representing the available and the
            installed version number of the application. """
        return ['', '']

    @property
    def website(self):
        """ String containing the website of the application. """
        return ''

    def __repr__(self):
        return self.id
