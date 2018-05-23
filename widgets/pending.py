# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import Gdk, GLib, Gtk
from appdata import _
from aptdaemon import client, enums

escape = GLib.markup_escape_text
icontheme = Gtk.IconTheme.get_default()
icontheme.append_search_path('/usr/share/app-install/icons')


class Pending(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.vbox = Gtk.VBox()
        self.vbox.set_border_width(25)
        self.add_with_viewport(self.vbox)

        import dbus
        ad = client.get_aptdaemon(bus=dbus.SystemBus())

        def on_transactions_changed(now, later):
            self.set_queue([tid for tid in ([now] + later) if tid])
        ad.connect_to_signal('ActiveTransactionsChanged',
                             on_transactions_changed)
        now, later = ad.GetActiveTransactions()
        self.set_queue([tid for tid in ([now] + later) if tid])

    def set_queue(self, tids):
        for child in self.vbox.get_children():
            self.vbox.remove(child)

        transactions = []
        for tid in tids:
            trans = client.get_transaction(tid)
            pkgs = trans.packages
            if pkgs[0]:
                pkgname = pkgs[0][0]
            elif pkgs[1]:
                pkgname = pkgs[1][0]
            elif pkgs[2]:
                pkgname = pkgs[2][0]
            elif pkgs[3]:
                pkgname = pkgs[3][0]
            elif pkgs[4]:
                pkgname = pkgs[4][0]
            elif pkgs[5]:
                pkgname = pkgs[5][0]
            else:
                continue
            if trans.status == enums.STATUS_WAITING_LOCK:
                status = trans.status_details
            else:
                status = enums.get_status_string_from_enum(trans.status)
            transactions.append((pkgname, status, trans))

        if not transactions:
            l = Gtk.Label()
            m = '<small>(%s)</small>'
            l.set_markup(m % escape(_("no pending apps")))
            self.vbox.pack_start(l, True, True, 0)
            self.show_all()
            return

        from appdata.clients import get_client
        for pkgname, status, trans in transactions:
            app = get_client(pkgname)
            h = Gtk.HBox()
            self.vbox.pack_start(h, False, False, 0)
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
            box.connect('draw', draw_icon, pkgname)
            box.set_size_request(48, 48)
            h.pack_start(box, False, False, 0)
            l = Gtk.Label()
            l.set_alignment(0, 0.5)
            l.name = app.name if app else pkgname
            l.set_markup('%s\n<small>%s</small>' % (
                escape(l.name),
                escape(status)))
            h.pack_start(l, False, False, 0)

            def on_property_changed(trans, progress):
                status = enums.get_status_string_from_enum(trans.status) or ''
                if trans.status == enums.STATUS_WAITING_LOCK:
                    status = trans.status_details
                status += (' (%d%%)' % progress) if progress else ''
                l.set_markup('%s\n<small>%s</small>' % (
                    escape(l.name),
                    escape(status)))
                l.show()
            trans.connect('progress-changed', on_property_changed)

        self.show_all()
