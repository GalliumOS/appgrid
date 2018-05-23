#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file


if __name__ == '__main__':
    from argparse import ArgumentParser

    ap = ArgumentParser()
    ap.add_argument('--force-rtl', action='store_true', help="force rtl mode")
    ap.add_argument('request', help="package name or path to deb file",
                    nargs='?')

    args = vars(ap.parse_args())

    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk

    if args['force_rtl']:
        Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL)

    window = Gtk.Window()
    window.connect('destroy', Gtk.main_quit)
    window.set_position(Gtk.WindowPosition.CENTER)
    ds = Gdk.Screen.get_default()
    if ds.get_width() > 1440 and ds.get_height() > 900:
        window.set_default_size(1440, 900)
        window.set_size_request(880, 660)
    else:
        window.maximize()
        window.set_default_size(880, 660)
        window.set_size_request(880, 550)

    window.set_title('App Grid')

    provider = Gtk.CssProvider()
    provider.load_from_path('/usr/share/appgrid/appgrid.css')
    window.get_style_context().add_provider_for_screen(
        Gdk.Screen.get_default(), provider, 800)

    from widgets.sc import sc
    window.add(sc)
    window.show_all()

    if args['request']:
        r = args['request'].split('?')[0]
        if r.startswith('apt:///'):
            args['request'] = r[7:]
        elif r.startswith('apt://'):
            args['request'] = r[6:]
        elif r.startswith('apt:'):
            args['request'] = r[4:]
        sc.show_details(args['request'])
    else:
        sc.show_home()

    import os.path
    path = os.path.expanduser('~') + '/.config/appgrid/bsd2_accepted'
    if not os.path.exists(path):
        from widgets.tos import TermsOfService
        sc.add_small_overlay(TermsOfService(), width=600, force=True)

    Gtk.main()
