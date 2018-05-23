# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from appdata import _
from appdata.helpers import request
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango

escape = GLib.markup_escape_text


class Home(Gtk.EventBox):
    def __init__(self):
        Gtk.EventBox.__init__(self)

        # header
        al = Gtk.Alignment.new(0, 0, 0, 0)
        al.set_padding(10, 0, 10, 0)

        # search
        from widgets.basics import Entry
        self.search_entry = Entry(hint=_("Search…"))
        cp = Gtk.CssProvider()
        cp.load_from_data(b"@define-color placeholder_text_color #FFFFFF;")
        sc = self.search_entry.get_style_context()
        sc.add_provider(cp, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.search_entry.get_style_context().add_class('sherlock')
        self.search_entry.set_size_request(200, -1)
        self.search_term = ''
        al.add(self.search_entry)
        self._idle = None

        def on_search_changed(widget):
            new_term = widget.get_text()
            if new_term:
                widget.set_name('sherlockishome')
            else:
                widget.set_name('sherlockisout')
            if new_term != self.search_term:
                self.search_term = widget.get_text()
                if (self._idle and
                        GLib.main_context_default().find_source_by_id(
                        self._idle)):
                    GLib.source_remove(self._idle)

                def on_wait():
                    self.page = 0
                    self.dpm = {0: 0}
                    self.do_search()
                self._idle = GLib.timeout_add(500, on_wait)
            if self.search_term:
                self.search_entry.set_icon_from_icon_name(
                    Gtk.EntryIconPosition.SECONDARY,
                    'edit-clear-symbolic')
                if self.search_entry.get_direction() == Gtk.TextDirection.RTL:
                    pb = self.search_entry.get_icon_pixbuf(
                        Gtk.EntryIconPosition.SECONDARY).flip(True)
                    self.search_entry.set_icon_from_pixbuf(
                        Gtk.EntryIconPosition.SECONDARY, pb)
            else:
                self.search_entry.set_icon_from_icon_name(
                    Gtk.EntryIconPosition.SECONDARY,
                    '')
        self.search_entry.connect('changed', on_search_changed)

        def on_icon_press(widget, icon, something):
            if icon == Gtk.EntryIconPosition.SECONDARY:
                self.search_entry.set_text('')
        self.search_entry.connect('icon-press', on_icon_press)

        # pickers
        self.category = ''
        self.state = ''
        self.sort = ''

        from appdata.categories import categories
        self.cdata = [('category', _("Category"))]
        self.cdata += sorted([(c, _(c), sorted(
            [(c + ';' + s, _(s)) for s in categories[c]], key=lambda w: w[1]))
            for c in categories], key=lambda w: w[1])

        self.sdata = [('state', _("State")),
                      ('installed', _("Installed"))]

        self.sodata = [('sort', _("Sort")),
                       ('rating', _("Top Rated"))]

        # update pending counts
        def on_transactions_changed(now, later):
            d = len([tid for tid in ([now] + later) if tid])
            for dat in self.sdata:
                if dat[0] == 'xxxpending':
                    self.sdata.remove(dat)
            if d:
                self.sdata.append(('xxxpending', _("Pending (%d)") % d))

        def init_watcher():
            from aptdaemon import client
            import dbus
            ad = client.get_aptdaemon(bus=dbus.SystemBus())
            ad.connect_to_signal('ActiveTransactionsChanged',
                                 on_transactions_changed)
            now, later = ad.GetActiveTransactions()
            on_transactions_changed(now, later)
        GLib.timeout_add_seconds(3, init_watcher)

        # account
        self.user = ''

        def update_account():
            from accountmanager import am
            self.am = am

            def on_signed_in(name):
                self.user = 'in:' + name
                self.queue_draw()
            am.connect('signedin', lambda w, name: on_signed_in(name))

            def on_signed_out():
                self.user = 'out'
                self.queue_draw()
            am.connect('signedout', lambda w: on_signed_out())

            st = am.get_state()
            if st == 'signedout':
                on_signed_out()
            elif st.startswith('signedin:'):
                on_signed_in(st.partition('signedin:')[2])
        GLib.idle_add(update_account)

        self.data = []
        self.dpm = {0: 0}
        self.page = 0
        self.scroll_time = 0

        self.connect('button-press-event', self.click)
        self.connect('draw', self.draw)
        self.connect('scroll-event', self.scroll)
        self.flop = None
        self.smile = False
        self.puser = False
        self.stack = []
        self.add(al)

        self.do_search()

        self.show_all()

    def click(self, widget, event):
        for action, arg, x1, x2, y1, y2 in self.clicks:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if action == 'details':
                    from widgets.sc import sc
                    sc.show_details(arg)
                elif action == 'page':
                    self.page = arg
                    if self.page + 2 in self.dpm:
                        del self.dpm[self.page + 2]
                    self.trigger_draws()
                elif action == 'signin':
                    from widgets.sc import sc
                    sc.login()
                elif action == 'signout':
                    self.puser = False
                    self.am.signout()
                elif action == 'setp':
                    if arg[1] == 'xxxpending':
                        self.state = ''
                        from widgets.sc import sc
                        from widgets.pending import Pending
                        sc.add_small_overlay(Pending())
                        return
                    for d in [self.cdata, self.sdata, self.sodata]:
                        if d[0][0] == arg[0]:
                            setattr(self, d[0][0], arg[1])
                    self.page = 0
                    self.dpm = {0: 0}
                    self.flop = False
                    self.do_search()
                elif action == 'flop':
                    self.flop = None
                    if arg:
                        for d in [self.cdata, self.sdata, self.sodata]:
                            if d[0][0] == arg[0]:
                                self.flop = (d, arg[1])
                    self.queue_draw()
                elif action == 'smilepop':
                    self.smile = not self.smile
                    self.queue_draw()
                elif action == 'popuser':
                    self.puser = not self.puser
                    self.queue_draw()
                elif action == 'url':
                    import subprocess
                    subprocess.Popen(['xdg-open', arg])
                return

    def scroll(self, widget, event):
        import time
        if time.time() - self.scroll_time <= 0.5:
            return
        self.scroll_time = time.time()

        if event.direction == Gdk.ScrollDirection.UP and self.page:
            self.page = max(self.page - 1, 0)
            if self.page + 2 in self.dpm:
                del self.dpm[self.page + 2]
            self.trigger_draws()
        elif (event.direction == Gdk.ScrollDirection.DOWN and
                self.page + 1 in self.dpm):
            self.page += 1
            self.trigger_draws()

    def draw(self, widget, cr):
        self.clicks = []

        a = widget.get_allocation()
        width, height = a.width, a.height
        self.drawcount += 1
        cr.set_line_width(1)
        context = widget.get_style_context()

        # background
        cr.set_source_rgb(242 / 255, 241 / 255, 240 / 255)
        cr.rectangle(0, 0, a.width, a.height)
        cr.fill()
        cr.set_source_rgba(221 / 255, 72 / 255, 20 / 255)
        cr.rectangle(0, 0, width, 50)
        cr.fill()
        # strokes
        cr.set_line_width(1)
        # pickers
        pl = widget.create_pango_layout('')

        self.search_entry.show()
        m = '<span color="#ffffff" size="large" weight="light">%s</span>'
        x = 240
        ppos = {}
        for d in [self.cdata, self.sdata, self.sodata]:
            ppos[d[0][0]] = x
            text = d[0][1]
            if getattr(self, d[0][0]):
                for dat in d[1:]:
                    if dat[0] == getattr(self, d[0][0]):
                        text = dat[1]
                    if len(dat) > 2:
                        for sdat in dat[2]:
                            if sdat[0] == getattr(self, d[0][0]):
                                text = sdat[1]
            pl.set_markup(m % escape(text))
            pla = pl.get_pixel_extents()[1]
            cr.set_source_rgba(1, 1, 1, 0.95)
            cr.set_line_width(1)
            if text == d[0][1]:
                cr.set_dash([2, 2])
                cr.move_to(x + 0.5,
                           25 + pla.height // 2 + 4.5)
                cr.line_to(x + pla.width + 20 + 0.5,
                           25 + pla.height // 2 + 4.5)
                self.clicks.append(['flop', (d[0][0], ''), x,
                                    x + pla.width + 20, 10, 40])
            else:
                cr.set_dash([1, 0])
                cr.rectangle(x + 0.5, 25 - pla.height // 2 - 4.5,
                             pla.width + 20, pla.height + 10)
                self.clicks.append(['setp', (d[0][0], ''), x,
                                    x + pla.width + 20, 10, 40])
            cr.stroke()
            Gtk.render_layout(context, cr, x + 10,
                              25 - pla.height // 2, pl)
            x += pla.width + 20 + 20
        cr.set_dash([1, 0])
        # app grid
        m = '<span color="#fff" font="22" weight="light">%s</span>'
        pl.set_markup(m % escape("☺"))
        pla = pl.get_pixel_extents()[1]
        Gtk.render_layout(context, cr, width - 25 - pla.width // 2,
                          25 - pla.height // 2, pl)
        cr.set_line_width(1)
        cr.set_source_rgba(1, 1, 1, 0.1)
        cr.move_to(width - 50 + 0.5, 0.5)
        cr.line_to(width - 50 + 0.5, 49.5)
        cr.stroke()
        self.clicks.append(['smilepop', '', width - 50, width, 0, 50])
        # user
        if self.user:
            pl = widget.create_pango_layout('')
            if self.user.startswith('in:'):
                text = self.user[3:]
                task = 'popuser'
            else:
                text = _('Sign in')
                task = 'signin'

            m = '<span color="#ffffff" size="large" weight="light">%s</span>'
            x = width - 50 - 10
            pl.set_markup(m % escape(text))
            pla = pl.get_pixel_extents()[1]
            cr.set_source_rgba(1, 1, 1, 0.95)
            cr.set_line_width(1)
            cr.set_dash([2, 2])
            cr.move_to(x - pla.width - 20 + 0.5,
                       25 + pla.height // 2 + 4.5)
            cr.line_to(x + 0.5, 25 + pla.height // 2 + 4.5)
            cr.stroke()
            self.clicks.append([task, '', x - pla.width - 20, x, 10, 40])
            Gtk.render_layout(context, cr, x - pla.width - 10,
                              25 - pla.height // 2, pl)
            cr.set_dash([1, 0])

        pl = widget.create_pango_layout('')
        pl.set_ellipsize(Pango.EllipsizeMode.END)
        pl.set_width((400 - 100 - 10) * Pango.SCALE)
        pl.set_height(-1)

        # maths
        from math import pi
        ys = 20

        # data
        x = 20
        y = 50 + ys
        if self.page + 1 in self.dpm:
            del self.dpm[self.page + 1]
        i = self.dpm[self.page]

        while x <= width and i < len(self.data):
            row = self.data[i]

            # load more data
            if row == 'more?':
                self.do_search(more=True)
                row = self.data[i]
                if not row or row == 'more?':
                    break

            # 0id, 1name, 2summary, 3rating, 4state
            # bg
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(x - 10, y - 10, 420, 120)
            cr.fill()
            cr.set_source_rgba(0, 0, 0, 0.1)
            cr.move_to(x - 10, y + 110)
            cr.line_to(x + 410, y + 110)
            cr.line_to(x + 410, y - 10)
            cr.stroke()
            # thumbnail
            t = 'https://screenshots.debian.net/thumbnail/%s/' % row[0]
            t = request(t, async=True, cache=10)
            pb = None
            if t == 'needs-download':
                if self.drawcount == 1:
                    t.download()
            elif t:
                try:
                    pb = GdkPixbuf.Pixbuf.new_from_file(t)
                except:
                    pass
            if pb:
                pbx = (x + 50 - pb.get_width() // 2 if pb.get_width() < 100
                       else x)
                pby = (y + 50 - pb.get_height() // 2 if pb.get_height() < 100
                       else y)
                Gdk.cairo_set_source_pixbuf(cr, pb, pbx, pby)
                cr.rectangle(x, y, 100, 100)
                cr.save()
                cr.clip()
                cr.paint()
                cr.restore()
                # border
                cr.set_source_rgba(0, 0, 0, 0.1)
                cr.rectangle(x + 0.5, y + 0.5, 100, 100)
                cr.stroke()
            else:
                cr.set_source_rgba(0, 0, 0, 0.05)
                cr.rectangle(x, y, 100, 100)
                cr.fill()

            # text
            m = "<span weight='light' size='large'>%s</span>" % escape(row[1])
            pl.set_markup(m, -1)
            Gtk.render_layout(context, cr, x + 110, y + 2, pl)
            theight = pl.get_pixel_extents()[1].height
            # summary text
            pl.set_height(-3)
            m = "<span weight='light' color='#444'>%s</span>" % escape(
                row[2].replace('\r\n', ' ').replace('\n', ' '))
            pl.set_markup(m, -1)
            Gtk.render_layout(context, cr, x + 110, y + 2 + theight + 3, pl)
            teheight = pl.get_pixel_extents()[1].height
            pl.set_height(-1)
            # gray text
            m = []
            if row[3]:  # ratings
                m.append("<span weight='light' color='#777'>%s"
                         "</span>" % escape(row[3] * '★'))
            if row[4] in ['i', 'u']:  # state
                m.append("<span weight='light' size='small' color='#666'>%s"
                         "</span>" % escape(_("Installed")))
            pl.set_markup(' '.join(m), -1)
            Gtk.render_layout(context, cr, x + 110,
                              y + 2 + theight + 3 + teheight + 3, pl)
            self.clicks.append(['details', row[0], x, x + 400, y, y + 100])

            i += 1
            y += 100 + ys + 10
            # fixme: push header to next line if dangling
            if y > height - 100 - ys + 10:
                x += 440
                y = 50 + ys
                if width - 400 < x <= width + 40 and i < len(self.data):
                    self.dpm[self.page + 1] = i

        # back/forward
        if self.page or self.page + 1 in self.dpm:
            x = width
            y = 50 + (height - 50) // 2
            cr.set_source_rgb(221 / 255, 72 / 255, 20 / 255)  # orange
            cr.new_path()
            cr.move_to(x + 0.5, y + 60 + 0.5)
            cr.arc(x - 25 + 0.5, y + 55 + 0.5, 5, pi / 2, pi)
            cr.arc(x - 25 + 0.5, y - 55 + 0.5, 5, pi, 3 * pi / 2)
            cr.line_to(x + 0.5, y - 60 + 0.5)
            cr.close_path()
            cr.fill()
            cr.set_line_width(1)
            cr.set_source_rgba(1, 1, 1, 0.2)
            cr.move_to(x + 0.5, y + 0.5)
            cr.line_to(x - 30 + 0.5, y + 0.5)
            cr.stroke()
            cr.set_source_rgb(1, 1, 1)
            cr.set_line_width(3)
            self.clicks.insert(0, ['', '', x - 30, x, y - 60, y + 60])  # blank
            if self.page:
                cr.move_to(x - 10, y - 30 - 15)
                cr.line_to(x - 20, y - 30)
                cr.line_to(x - 10, y - 30 + 15)
                self.clicks.insert(0, ['page', self.page - 1, x - 30, x,
                                       y - 60, y])
            if self.page + 1 in self.dpm:
                cr.move_to(x - 20, y + 30 - 15)
                cr.line_to(x - 10, y + 30)
                cr.line_to(x - 20, y + 30 + 15)
                self.clicks.insert(0, ['page', self.page + 1, x - 30, x, y,
                                       y + 60])
            cr.stroke()

        # no results
        if not self.page and not self.data:
            pl = widget.create_pango_layout('')
            m = ('<span color="#dd4814" font-size="large" font-weight="light">'
                 '%s</span>')
            pl.set_markup(m % escape(_('No results')), -1)
            Gtk.render_layout(context, cr, 20, 65, pl)

        # ### picker popup ### #
        if self.flop:
            self.clicks = []
            self.clicks.append(['flop', False, 0, width, 0, height])

            d = self.flop[0]

            # size math
            pl = widget.create_pango_layout('')
            m = '<span color="#dd4814" size="large" weight="light">%s</span>'

            w = 20 + 20
            h = 10
            for row in d[1:]:
                pl.set_markup(m % escape(row[1]))
                pla = pl.get_pixel_extents()[1]
                tw = 20 + pla.width + 20
                tw = tw + 20 if len(row) == 3 else tw
                w = max(w, tw)
                h += pla.height + 10

            x, y = ppos[d[0][0]] - 10, 50

            # draw
            cr.set_source_rgba(1, 1, 1, 0.9)
            cr.rectangle(x, y, w, h)
            cr.fill()
            sy = 50
            for row in d[1:]:
                pl.set_markup(m % escape(row[1]))
                Gtk.render_layout(context, cr, x + 20, y + 10, pl)
                pla = pl.get_pixel_extents()[1]
                self.clicks.insert(0, ['setp', (d[0][0], row[0]), x, x + w, y,
                                       y + 5 + pla.height + 10])
                if len(row) == 3:
                    if row[0] == self.flop[1]:
                        sy = y
                    pl.set_markup(m % "›")
                    Gtk.render_layout(context, cr, x + w - 20, y + 10, pl)
                    self.clicks.insert(0, ['flop', (d[0][0], row[0]),
                                           x + w - 25, x + w,
                                           y, y + 5 + pla.height + 10])
                y += pla.height + 10

            # submenu
            if self.flop[1]:
                data = [r[2] for r in d[1:] if r[0] == self.flop[1]][0]
                x, y = x + w + 1, sy
                w = 20 + 20
                h = 10
                for row in data:
                    pl.set_markup(m % escape(row[1]))
                    pla = pl.get_pixel_extents()[1]
                    w = max(w, 20 + pla.width + 20)
                    h += pla.height + 10

                # draw
                cr.set_source_rgba(1, 1, 1, 0.9)
                cr.rectangle(x, y, w, h)
                cr.fill()
                for row in data:
                    pl.set_markup(m % escape(row[1]))
                    Gtk.render_layout(context, cr, x + 20, y + 10, pl)
                    pla = pl.get_pixel_extents()[1]
                    self.clicks.insert(0, ['setp', (d[0][0], row[0]), x, x + w,
                                           y, y + 5 + pla.height + 10])
                    y += pla.height + 10

        # ### smile popup ### #
        if self.smile:
            self.clicks = []
            self.clicks.append(['smilepop', '', 0, width, 0, height])

            d = [('http://www.appgrid.org/#donate', _("Make a donation")),
                 ('mailto:feedback@appgrid.org', _("Provide feedback")),
                 ('http://www.appgrid.org/#showtime', _("Share our website"))]

            # size math
            pl = widget.create_pango_layout('')
            m = '<span color="#dd4814" size="large" weight="light">%s</span>'

            w = 20 + 20
            h = 10
            for row in d:
                pl.set_markup(m % escape(row[1]))
                pla = pl.get_pixel_extents()[1]
                w = max(w, 20 + pla.width + 20)
                h += pla.height + 10

            x, y = width - w, 50

            # draw
            cr.set_source_rgba(1, 1, 1, 0.9)
            cr.rectangle(x, y, w, h)
            cr.fill()
            for row in d:
                pl.set_markup(m % escape(row[1]))
                Gtk.render_layout(context, cr, x + 20, y + 10, pl)
                pla = pl.get_pixel_extents()[1]
                self.clicks.insert(0, ['url', row[0], x, x + w, y,
                                       y + 5 + pla.height + 10])
                y += pla.height + 10

        # ### user popup ### #
        if self.puser:
            self.clicks = []
            self.clicks.append(['popuser', '', 0, width, 0, height])

            d = [('signout', _("Sign out"))]

            # size math
            pl = widget.create_pango_layout('')
            m = '<span color="#dd4814" size="large" weight="light">%s</span>'

            w = 20 + 20
            h = 10
            for row in d:
                pl.set_markup(m % escape(row[1]))
                pla = pl.get_pixel_extents()[1]
                w = max(w, 20 + pla.width + 20)
                h += pla.height + 10

            x, y = width - 50 - w, 50

            # draw
            cr.set_source_rgba(1, 1, 1, 0.9)
            cr.rectangle(x, y, w, h)
            cr.fill()
            for row in d:
                pl.set_markup(m % escape(row[1]))
                Gtk.render_layout(context, cr, x + 20, y + 10, pl)
                pla = pl.get_pixel_extents()[1]
                self.clicks.insert(0, [row[0], '', x, x + w, y,
                                       y + 5 + pla.height + 10])
                y += pla.height + 10

    def do_search(self, more=False):
        from appdata.clients import get_clients
        offset = len(self.data) - 1 if more else self.dpm[self.page]
        if (not self.category and not self.search_term and not self.state and
                not self.sort):
            offset = 0

        c = get_clients(category=self.category, search=self.search_term,
                        state=self.state, sort=self.sort, offset=offset)
        if more:
            self.data = self.data[:-1] + c
        else:
            self.data = c

        self.trigger_draws()

    def trigger_draws(self):
        self.drawcount = 0
        self.queue_draw()

        def trigger_draw():  # catch downloaded images
            self.queue_draw()
            if self.drawcount < 10:
                return True
        GLib.timeout_add(1000, trigger_draw)
