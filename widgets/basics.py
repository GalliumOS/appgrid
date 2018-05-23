# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import Gdk, GLib, Gtk

escape = GLib.markup_escape_text


class Button(Gtk.Alignment):
    def __init__(self):
        Gtk.Alignment.__init__(self)

        self.set(0.5, 0.5, 0, 0)

        self._callback = None
        self._callback_args = None

        b = Gtk.Button()
        b.connect('clicked', self.on_clicked)
        b.set_size_request(150, 30)
        b.get_style_context().add_class('actionbutton')
        self.add(b)

        self.l = Gtk.Label()
        b.add(self.l)

    def set_text(self, text):
        self.l.set_markup("<big>%s</big>" % escape(text))

    def set_callback(self, callback, callback_args=None):
        self._callback = callback
        self._callback_args = callback_args

    def on_clicked(self, widget):
        t = self.l.get_text()
        if t.endswith('...') or t.endswith('…'):
            return
        if self._callback and self._callback_args:
            self._callback(self._callback_args)
        elif self._callback:
            self._callback()


class Entry(Gtk.Entry):
    def __init__(self, hint='', invis=False):
        Gtk.Entry.__init__(self)

        if hint:
            self.set_placeholder_text(hint)

        if invis:
            self.set_visibility(False)

    def do_get_preferred_width(self):
        return 100, 100


class TextView(Gtk.TextView):
    def __init__(self, hint=''):
        Gtk.TextView.__init__(self)

        self._hint = hint

        self.connect('focus-in-event', lambda w, e: self.clear_hint())
        self.connect('focus-out-event', lambda w, e: self.set_hint())

        c = Gdk.RGBA()
        c.parse('#888888')
        self._gr_col = c

        self.set_hint()

    def set_hint(self):
        if self.get_text():
            return

        self.get_buffer().set_text(self._hint)
        self.override_color(Gtk.StateFlags.NORMAL, self._gr_col)

    def clear_hint(self):
        if self.get_text():
            return

        self.get_buffer().set_text('')
        self.override_color(Gtk.StateFlags.NORMAL, None)

    def get_text(self):
        t = super(TextView, self).get_buffer().get_text(
            self.get_buffer().get_start_iter(),
            self.get_buffer().get_end_iter(), True)
        if t != self._hint:
            return t
        return ''

    def do_get_preferred_width(self):
        return 100, 100


class StarEntry(Gtk.HBox):
    def __init__(self):
        Gtk.HBox.__init__(self)

        self.rating = 0

        self.labels = []
        for i in range(1, 4):
            l = Gtk.Label()
            l.set_markup("<span size='xx-large'>☆</span>")
            self.labels.append(l)
            e = Gtk.EventBox()
            e.rating = i
            e.add(l)
            self.pack_start(e, False, False, 0)
            e.connect('button-press-event',
                      lambda w, e: self.set_rating(w.rating))
            e.connect('enter-notify-event',
                      lambda w, e: self.set_rating(w.rating, hint=True))
            e.connect('leave-notify-event',
                      lambda w, e: self.set_rating(self.rating, hint=True))

        self.show_all()

    def get_rating(self):
        return self.rating

    def set_rating(self, r, hint=False):
        if not hint:
            self.rating = r
        for i in [0, 1, 2]:
            if r >= i + 1:
                self.labels[i].set_markup("<span size='xx-large'>★</span>")
            else:
                self.labels[i].set_markup("<span size='xx-large'>☆</span>")
