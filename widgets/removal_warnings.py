# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import Gdk, GLib, Gtk
from widgets.basics import Button
from appdata import _

escape = GLib.markup_escape_text
icontheme = Gtk.IconTheme.get_default()
icontheme.append_search_path('/usr/share/app-install/icons')


class RemovalWarnings(Gtk.VBox):
    def __init__(self, pkgnames):
        Gtk.VBox.__init__(self)

        self.set_border_width(25)
        self.set_spacing(10)
        self.approved = False

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        markup = _("The following apps will be removed:")
        l.set_markup('<big>%s</big>' % escape(markup))
        self.pack_start(l, False, False, 0)

        # apps
        sw = Gtk.ScrolledWindow()
        v = Gtk.VBox()
        sw.add_with_viewport(v)
        self.pack_start(sw, True, True, 0)

        from appdata.clients import get_client
        for pkgname in pkgnames:
            app = get_client(pkgname)
            h = Gtk.HBox()
            v.pack_start(h, False, False, 0)
            box = Gtk.Box()

            def draw_icon(widget, cr, pn):
                if icontheme.has_icon(pn):
                    pb = icontheme.load_icon(pn, 32,
                                             Gtk.IconLookupFlags.FORCE_SIZE)
                    Gdk.cairo_set_source_pixbuf(cr, pb, 8, 8)
                    cr.paint()
                else:
                    cr.set_source_rgb(0.7, 0.7, 0.7)
                    cr.arc(24, 24, 16, 0, 7)
                    cr.fill()
            box.connect('draw', draw_icon, app.id)
            box.set_size_request(48, 48)
            h.pack_start(box, False, False, 0)
            l = Gtk.Label()
            l.set_alignment(0, 0.5)
            l.set_markup('%s (%s)\n<small>%s</small>' % (
                escape(app.name),
                escape(app.id),
                escape(app.summary)))
            h.pack_start(l, False, False, 0)

        # go
        h = Gtk.HBox()
        h.set_spacing(10)
        self.pack_start(h, False, False, 0)

        def on_button_clicked():
            self.approved = True
            self.hide()
        b = Button()
        b.set_text(_("Continue"))
        b.set_callback(on_button_clicked)
        h.pack_end(b, False, False, 0)

        self.show_all()
