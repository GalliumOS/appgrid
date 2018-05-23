# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GLib, Gtk
from widgets.basics import Button
from aptdaemon import enums
from appdata import _

escape = GLib.markup_escape_text


class TransactionFailed(Gtk.VBox):
    def __init__(self, trans):
        Gtk.VBox.__init__(self)

        self.set_border_width(25)
        self.set_spacing(10)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        markup = enums.get_error_string_from_enum(trans.error.code)
        l.set_markup('<big>%s</big>' % escape(markup))
        self.pack_start(l, False, False, 0)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        markup = enums.get_error_description_from_enum(trans.error.code)
        l.set_markup(escape(markup))
        self.pack_start(l, False, False, 0)

        # details
        sw = Gtk.ScrolledWindow()
        self.pack_start(sw, True, True, 0)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_markup(escape(trans.error_details))
        sw.add_with_viewport(l)

        # go
        h = Gtk.HBox()
        h.set_spacing(10)
        self.pack_start(h, False, False, 0)

        error = Gtk.Label()
        h.pack_start(error, False, False, 0)

        b = Button()
        b.set_text(_("OK"))
        b.set_callback(lambda: self.hide())
        h.pack_end(b, False, False, 0)

        self.show_all()
