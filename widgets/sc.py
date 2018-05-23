# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import Gtk


class SoftwareCenter(Gtk.Overlay):
    def __init__(self):
        Gtk.Overlay.__init__(self)
        self.home = None
        self.show()

    def clear(self):
        for child in self.get_children():
            self.remove(child)

    def show_home(self):
        self.clear()

        if not self.home:
            from widgets.home import Home
            self.home = Home()
        self.add(self.home)

    def show_details(self, pkgname):
        self.clear()

        from widgets.details import Details
        self.add(Details(pkgname))

    def login(self, next=None, prev=None, force=False):
        from accountmanager import am
        self.login_count = 0
        self.signedin_signal = None

        def on_signed_out(*args, **kwargs):
            if not self.login_count:
                from widgets.login import Login
                login = Login()

                def on_unmapped(widget):
                    if am.get_state() == 'signedout' and self.signedin_signal:
                        if prev:
                            prev()
                        am.disconnect(self.signedin_signal)
                login.connect('unmap', on_unmapped)

                self.add_small_overlay(login)
                self.login_count += 1
        am.connect('signedout', on_signed_out)

        def on_signed_in(*args, **kwargs):
            if next:
                next()
        self.signedin_signal = am.connect('signedin', on_signed_in)

        if force:
            on_signed_out()
        else:
            s = am.get_state()
            if s == 'signedout':
                on_signed_out()
            elif s.startswith('signedin:'):
                on_signed_in()

    def add_widget_as_overlay(self, widget, force=False):
        ev = Gtk.EventBox()
        ev.add(widget)
        if not force:
            ev.connect('button-press-event', lambda w, e: self.remove(ev))

        def draw_shading(widget, cr):
            cr.set_source_rgba(0, 0, 0, 0.5)
            cr.paint()
        ev.connect('draw', draw_shading)
        ev.secret_hide = lambda: self.remove(ev)
        ev.hide = lambda: self.remove(ev)
        ev.show()
        self.add_overlay(ev)

    def add_small_overlay(self, widget, width=480, height=320, force=False):
        a = Gtk.Alignment.new(0.5, 0.5, 0, 0)

        class ForcedBox(Gtk.EventBox):
            def do_get_preferred_width(self):
                return width, width
        box = ForcedBox()
        box.connect('button-press-event', lambda w, e: True)
        a.add(box)
        a.show()
        box.show()
        self.add_widget_as_overlay(a, force=force)

        box.set_size_request(width, height)
        box.add(widget)
        widget.hide = a.get_parent().hide

        def draw_bg(widget, cr):
            a = widget.get_allocation()
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(0, 0, a.width, a.height)
            cr.fill()
        box.connect('draw', draw_bg)


sc = SoftwareCenter()
