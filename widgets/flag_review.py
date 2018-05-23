# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GLib, Gtk
from widgets.basics import Button, TextView
from appdata import _

escape = GLib.markup_escape_text


class FlagReview(Gtk.VBox):
    def __init__(self, review_id):
        Gtk.VBox.__init__(self)

        self.set_border_width(25)
        self.set_spacing(10)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        markup = _("Why does this review require our attention:")
        l.set_markup('<big>%s</big>' % escape(markup))
        self.pack_start(l, False, False, 0)

        # reason
        f = Gtk.Frame()
        self.pack_start(f, True, True, 0)

        sw = Gtk.ScrolledWindow()
        f.add(sw)

        reason = TextView(_("Reason"))
        reason.set_border_width(5)
        sw.add(reason)

        # go
        h = Gtk.HBox()
        h.set_spacing(10)
        self.pack_start(h, False, False, 0)

        error = Gtk.Label()
        h.pack_start(error, False, False, 0)

        def on_button_clicked():
            if not reason.get_text():
                error.set_text(_("Reason required"))
                return
            b.set_text(_("Submitting…"))
            error.set_text('')
            reason.set_sensitive(False)

            data = {'reason': reason.get_text(),
                    'text': 'null',
                    }
            from appdata.helpers import request
            from accountmanager import am

            request('https://reviews.ubuntu.com/reviews/api/1.0/reviews/%d/fla'
                    'gs/' % review_id, oauth=am.get_oauth(), data=data)
            self.hide()
            # refresh
        b = Button()
        b.set_text(_("Submit"))
        b.set_callback(on_button_clicked)
        h.pack_end(b, False, False, 0)

        self.show_all()
