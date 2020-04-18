# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GLib, Gtk
from widgets.basics import Button, Entry, TextView, StarEntry
from appdata import _

escape = GLib.markup_escape_text


class WriteReview(Gtk.VBox):
    def __init__(self, app):
        Gtk.VBox.__init__(self)

        self.set_border_width(25)
        self.set_spacing(10)

        h = Gtk.HBox()
        h.set_spacing(10)
        self.pack_start(h, False, False, 0)

        # summary
        summary = Entry(_("Summary"))
        h.pack_start(summary, True, True, 0)

        # rating
        rating = StarEntry()
        h.pack_end(rating, False, False, 0)

        # review
        f = Gtk.Frame()
        self.pack_start(f, True, True, 0)

        sw = Gtk.ScrolledWindow()
        f.add(sw)

        review = TextView(_("Review"))
        review.set_border_width(5)
        sw.add(review)

        # legalities
        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_line_wrap(True)
        markup = _("By submitting your review, you give permission for your na"
                   "me and review to be published. Your review is not a bug re"
                   "port, nor a support request. Furthermore your review is re"
                   "spectable towards the developers and others.")
        l.set_markup('<small>%s</small>' % escape(markup))
        self.pack_start(l, False, False, 0)

        # go
        h = Gtk.HBox()
        h.set_spacing(10)
        self.pack_start(h, False, False, 0)

        error = Gtk.Label()
        h.pack_start(error, False, False, 0)

        def on_button_clicked():
            if not summary.get_text():
                error.set_text(_("Summary required"))
                return
            if not rating.get_rating():
                error.set_text(_("Rating required"))
                return
            if not review.get_text():
                error.set_text(_("Review required"))
                return
            b.set_text(_("Submitting…"))
            error.set_text('')
            summary.set_sensitive(False)
            review.set_sensitive(False)

            import distro
            import apt_pkg
            apt_pkg.init_config()
            import locale
            o = app.origin_id
            if o.startswith('U/'):
                origin = 'ubuntu'
            elif o.startswith('S/'):
                origin = 'lp-ppa-' + '-'.join(o.split('/')[1:])
            elif o == 'P':
                origin = 'canonical'
            else:  # shouldn't happen
                origin = 'ubuntu'

            try:
                lang = locale.getdefaultlocale()[0].split('_')[0]
            except:
                lang = 'en'

            ds = distro.linux_distribution()[2]

            body = {
                'package_name': app.id,
                'summary': summary.get_text(),
                'version': app.version[1],
                'review_text': review.get_text(),
                'rating': {1: 1, 2: 3, 3: 5}[rating.get_rating()],
                'language': lang,
                'origin': origin,
                'distroseries': ds,
                'arch_tag': apt_pkg.config.find('Apt::Architecture'),
            }
            from appdata.helpers import request
            from accountmanager import am
            request('https://reviews.ubuntu.com/reviews/api/1.0/reviews/',
                    oauth=am.get_oauth(), data=body, content_type='json')
            self.hide()
            # refresh
        b = Button()
        b.set_text(_("Submit"))
        b.set_callback(on_button_clicked)
        h.pack_end(b, False, False, 0)

        self.show_all()
