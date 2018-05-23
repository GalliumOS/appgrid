# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GLib, Gtk

escape = GLib.markup_escape_text


class Addons(Gtk.VBox):
    def __init__(self, pkgnames):
        Gtk.VBox.__init__(self)

        self.hbox = Gtk.HBox()
        self.hbox.set_border_width(20)
        self.pack_start(self.hbox, False, False, 0)

        cb = Gtk.ComboBoxText()
        self.hbox.pack_start(cb, False, False, 0)

        self.show_all()

        self.sw = Gtk.ScrolledWindow()
        self.pack_start(self.sw, True, True, 0)

        for pkgname in sorted(pkgnames):
            cb.append_text(pkgname)

        def on_changed(widget, self):
            for child in self.hbox.get_children():
                if type(child) != Gtk.ComboBoxText:
                    self.hbox.remove(child)
            self.sw.hide()
            for child in self.sw.get_children():
                self.sw.remove(child)
            GLib.idle_add(self.set_pkg, widget.get_active_text())
        cb.connect('changed', on_changed, self)

        cb.set_active(0)

    def set_pkg(self, pkgname):
        from appdata.clients import get_client
        app = get_client(pkgname)

        from widgets.magicbutton import MagicButton
        mb = MagicButton(app)
        mb.subscript.hide()  # meh
        self.hbox.pack_end(mb, False, False, 0)

        l = Gtk.Label()
        l.set_alignment(0, 0)
        l.set_margin_bottom(10)
        l.set_margin_left(20)
        l.set_margin_right(20)
        l.set_line_wrap(True)
        l.set_markup(escape(app.summary + '\n\n' + app.description))
        self.sw.add_with_viewport(l)
        self.sw.show_all()
