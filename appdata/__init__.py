# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
import gettext
import locale

DB_PATH = '/var/cache/appgrid/appgrid9.db'

# set language
gettext.bindtextdomain('appgrid', '/usr/share/locale')
gettext.textdomain('appgrid')
try:
    locale.setlocale(locale.LC_ALL, '')
except:
    locale.setlocale(locale.LC_ALL, 'C')

# translation helper


def _(text):
    return gettext.gettext(text)


def d_(domain, text):
    return gettext.dgettext(domain, text)
