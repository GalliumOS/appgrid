# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GLib, Gtk
from widgets.basics import Button, Entry
from appdata import _

escape = GLib.markup_escape_text


class Login(Gtk.VBox):
    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_border_width(25)
        self.set_spacing(10)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        markup = _("Sign in with your Ubuntu One account:")
        l.set_markup('<big>%s</big>' % escape(markup))
        self.pack_start(l, False, False, 0)

        # e-mail
        e = Entry(_("E-mail address"))
        self.pack_start(e, False, False, 0)

        # password
        p = Entry(_("Password"), True)
        self.pack_start(p, False, False, 0)

        # otpassword
        otp = Entry(_("One-time password"), True)
        self.pack_start(otp, False, False, 0)

        # go
        h = Gtk.HBox()
        h.set_spacing(10)
        self.pack_start(h, False, False, 0)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_line_wrap(True)
        markup = _("Don't have an account?")
        lmarkup = _("An Ubuntu One account is free and gives access  to many U"
                    "buntu-related services. You can create your account at %s"
                    ".")
        link = "<a href='https://login.ubuntu.com/+new_account'>ubuntu.com</a>"
        l.set_markup('<big>%s</big>\n%s' % (escape(markup),
                     escape(lmarkup) % link))
        self.pack_end(l, False, False, 0)

        self.show_all()
        otp.hide()

        error = Gtk.Label.new(_("Verification failed - please try again."))
        h.pack_start(error, False, False, 0)

        pad = Gtk.Box()
        pad.show()
        h.pack_start(pad, True, True, 0)

        def on_button_clicked():
            b.set_text(_("Signing In…"))
            error.hide()
            e.set_sensitive(False)
            p.set_sensitive(False)
            otp.set_sensitive(False)
            from accountmanager import am

            am.connect('signedin', lambda w, u: self.hide())

            def on_failed_login(w, c):
                if c == 'TWOFACTOR_REQUIRED':
                    b.set_text(_("Sign In"))
                    otp.set_sensitive(True)
                    otp.show()
                else:
                    b.set_text(_("Sign In"))
                    if c == 'TWOFACTOR_FAILURE':
                        otp.set_text('')
                        otp.set_sensitive(True)
                    else:
                        e.set_sensitive(True)
                        p.set_text('')
                        p.set_sensitive(True)
                    error.set_text('✘ ' + c.replace('_', ' '))
                    error.show()
            am.connect('failed', on_failed_login)

            while Gtk.events_pending():
                Gtk.main_iteration()

            am.signin(e.get_text(), p.get_text(), otp=otp.get_text())
        b = Button()
        b.set_text(_("Sign In"))
        b.set_callback(on_button_clicked)
        h.pack_start(b, False, False, 0)
        b.show_all()
        p.connect('activate', lambda w: on_button_clicked())
