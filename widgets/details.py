# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import Gdk, GLib, Gtk, Pango, GdkPixbuf
from appdata import _

escape = GLib.markup_escape_text


class Details(Gtk.EventBox):
    def __init__(self, pkgname):
        Gtk.EventBox.__init__(self)

        from appdata.clients import get_client
        self.app = get_client(pkgname)

        self.scroll_time = 0
        self.scrolls = []
        self.connect('button-press-event', self.click)
        self.connect('draw', self.draw)
        self.connect('scroll-event', self.scroll)
        self.show()

        if not self.app:
            return

        self.state = ''
        gr = self
        # magicbutton
        from widgets.magicbutton import MagicButton

        class UltraMagicButton(MagicButton):
            def set_state(self, *args, **kwargs):
                super(UltraMagicButton, self).set_state(*args, **kwargs)
                gr.state = args[0]
                if args[0] == 'installed':
                    import subprocess
                    try:
                        o = subprocess.check_output(["dpkg", "-L",
                                                     self.app.id],
                                                    stderr=subprocess.STDOUT
                                                    ).decode('utf8')
                    except:
                        o = ''
                    o = o.split('\n')
                    o.reverse()
                    c = [l for l in o if (l.endswith('.desktop') and
                         (l.startswith('/opt/') or
                          l.startswith('/usr/share/applications/')) and
                         '\nExec=' in open(l).read())]
                    if c:
                        gr.state += '##'
                gr.queue_draw()
        self.um = UltraMagicButton(self.app)

        # images
        self.screenshots = []
        self.scursor = None
        GLib.timeout_add(100, self.get_screenshots)

        # description overflow
        self.descrip = False

        # reviews
        self.lang = 'local'
        self.reviews = {'local': [], 'any': []}
        self.rpages = {'local': 0, 'any': 0}
        GLib.timeout_add(100, self.get_reviews)
        self.langpop = False

#        from accountmanager import am
#        if am.get_state().startswith('signedin:'):
#            import json
#            self.username = json.loads(am.whoami(async=False))['username']
#        else:
        self.username = ''

        self.rcols = [0]
        self.rindex = 0

    def get_screenshots(self):
        from appdata.helpers import request

        def got_image(w, filename, i):
            self.screenshots[i] = filename
            self.queue_draw()

        def got_json(w, filename):
            scr = []
            if filename:
                import json
                try:
                    parsed = json.loads(open(filename).read())['screenshots']
                except:
                    parsed = []
                urls = [subjson['large_image_url'] for subjson in parsed]
                urls = [u.replace('https://screenshots.ubuntu.com/',
                                  'https://screenshots.debian.net/')
                        for u in urls]
                scr = [request(u, async=True, cache=10) for u in urls]
            self.screenshots = scr

            for i, f in enumerate(self.screenshots):  # FIXME only get visible?
                if f == 'needs-download':
                    f.connect('downloaded', got_image, i)
                    f.download()
            self.queue_draw()

        url = 'https://screenshots.debian.net/json/package/%s'
        r = request(url % self.app.id, async=True, cache=3)
        if r == 'needs-download':
            r.connect('downloaded', got_json)
            r.download()
        else:
            got_json(None, r)

    def get_reviews(self):
        if len(self.reviews[self.lang]) % 10 and self.rpages[self.lang]:
            return
        if (not len(self.reviews[self.lang]) % 10 and
                len(self.reviews[self.lang]) != 10 * self.rpages[self.lang]):
            return
        self.rpages[self.lang] += 1

        url = ('https://reviews.ubuntu.com/reviews/api/1.0/reviews/filter/'
               '%s/any/any/any/%s/page/%d/newest/')
        from appdata.helpers import request
        import json

        def on_page_downloaded(widget, data, lang):
            if not data or data == '[]':
                if self.lang == 'local' and self.rpages[self.lang] == 1:
                    self.lang = 'any'
                    self.get_reviews()
                return
            from appdata.reviews import Review
            try:
                reviews = [Review(r) for r in json.loads(data or '[]')]
            except:
                reviews = []
            self.reviews[lang] += reviews
            self.queue_draw()

        page = self.rpages[self.lang]
        if self.lang == 'local':
            import locale
            try:
                lang = locale.getdefaultlocale()[0].split('_')[0]
            except:
                lang = 'en'
        else:
            lang = 'any'
        r = request(url % (lang, self.app.id, page), async=True, cache=False)
        r.connect('downloaded', on_page_downloaded, self.lang)
        r.download()

    def click(self, widget, event):
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return
        for action, arg, x1, x2, y1, y2 in self.clicks:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if action == 'back':
                    from widgets.sc import sc
                    sc.show_home()
                elif action == 'gallery':
                    self.scursor = arg
                    self.queue_draw()
                elif action == 'reviews':
                    self.rindex = arg
                    self.queue_draw()
                elif action == 'write':
                    def on_write_review():
                        from widgets.write_review import WriteReview
                        from widgets.sc import sc
                        wr = WriteReview(self.app)

                        def on_unmapped(widget):
                            self.lang = 'local'
                            self.reviews = {'local': [], 'any': []}
                            self.rpages = {'local': 0, 'any': 0}
                            self.queue_draw()
                        wr.connect('unmap', on_unmapped)
                        sc.add_small_overlay(wr)
                    from widgets.sc import sc
                    sc.login(on_write_review)
                elif action == 'install':
                    self.um.on_install()
                elif action == 'remove':
                    self.um.on_remove()
                elif action == 'launch':
                    self.um.on_launch()
                elif action == 'pending':
                    from widgets.sc import sc
                    from widgets.pending import Pending
                    sc.add_small_overlay(Pending())
                elif action == 'addons':
                    from widgets.sc import sc
                    from widgets.addons import Addons
                    sc.add_small_overlay(Addons(self.app.addons))
                elif action == 'url':
                    import subprocess
                    subprocess.Popen(['xdg-open', arg])
                elif action == 'descrip':
                    self.descrip = arg
                    self.queue_draw()
                elif action == 'delete':
                    def delete_review(arg):
                        from appdata.helpers import request
                        from accountmanager import am
                        request('https://reviews.ubuntu.com/reviews/api/1.0/re'
                                'views/delete/%d/' % arg, oauth=am.get_oauth(),
                                data={})
                        self.lang = 'local'
                        self.reviews = {'local': [], 'any': []}
                        self.rpages = {'local': 0, 'any': 0}
                        self.queue_draw()
                    from widgets.sc import sc
                    sc.login(lambda: delete_review(arg))
                elif action == 'moderate':
                    def moderate_review(arg):
                        from widgets.flag_review import FlagReview
                        from widgets.sc import sc
                        fr = FlagReview(arg)

                        def on_unmapped(widget):
                            self.lang = 'local'
                            self.reviews = {'local': [], 'any': []}
                            self.rpages = {'local': 0, 'any': 0}
                            self.queue_draw()
                        fr.connect('unmap', on_unmapped)
                        sc.add_small_overlay(fr)
                    from widgets.sc import sc
                    sc.login(lambda: moderate_review(arg))
                elif action == 'langpop':
                    self.langpop = arg
                    self.queue_draw()
                elif action == 'setlang':
                    self.lang = arg
                    self.langpop = False
                    self.rindex = 0
                    self.queue_draw()
                    self.get_reviews()
                return

    def scroll(self, widget, event):
        import time
        if time.time() - self.scroll_time <= 0.5:
            return
        self.scroll_time = time.time()

        a = widget.get_allocation()
        if (a.width - 440 <= event.x <= a.width and
                50 <= event.y <= a.height and 'prevrev' in self.scrolls and
                event.direction == Gdk.ScrollDirection.UP):
            self.rindex -= 1
            self.queue_draw()
        elif (a.width - 440 <= event.x <= a.width and
                50 <= event.y <= a.height and 'nextrev' in self.scrolls and
                event.direction == Gdk.ScrollDirection.DOWN):
            self.rindex += 1
            self.queue_draw()

    def draw(self, widget, cr):
        a = widget.get_allocation()
        width, height = a.width, a.height

        self.clicks = []
        self.scrolls = []

        context = widget.get_style_context()
        from math import pi

        # background
        cr.set_source_rgb(242 / 255, 241 / 255, 240 / 255)
        cr.rectangle(0, 0, a.width, a.height)
        cr.fill()
        cr.set_source_rgba(221 / 255, 72 / 255, 20 / 255)
        cr.rectangle(0, 0, width, 50)
        cr.fill()
        # strokes
        cr.set_line_width(1)
        for i in [50, width - 440]:
            cr.set_source_rgba(1, 1, 1, 0.1)
            cr.move_to(i + 0.5, 0.5)
            cr.line_to(i + 0.5, 49.5)
            cr.stroke()
        for i in [width - 440]:
            cr.set_source_rgba(221 / 255, 72 / 255, 20 / 255, 0.1)
            cr.move_to(i + 0.5, 65.5)
            cr.line_to(i + 0.5, a.height - 15.5)
            cr.stroke()
        # back
        cr.set_source_rgb(1, 1, 1)
        cr.set_line_width(2)
        cr.move_to(30, 25 - 15)
        cr.line_to(20, 25)
        cr.line_to(30, 25 + 15)
        cr.stroke()
        cr.set_line_width(1)
        self.clicks.append(['back', '', 0, 50, 0, 50])
        # title
        pl = widget.create_pango_layout('')
        m = '<span color="#ffffff" size="x-large" weight="light">%s</span>'
        if not self.app:
            pl.set_markup(m % escape(_("Not found")))
        else:
            pl.set_markup(m % escape(self.app.name))
        pla = pl.get_pixel_extents()[1]
        Gtk.render_layout(context, cr, 70, 25 - pla.height // 2, pl)
        if not self.app:
            return

        # ultramagicbutton  # FIXME: query for already pending installs
        state = self.state
        actions = []
        m = '<span color="#ffffff" size="large" weight="light">%s</span>'
        if state == 'available':
            actions = [(_("Install"), 'install')]
        elif state.startswith('installed'):
            actions = [(_("Remove"), 'remove')]
            if state.endswith('##'):
                actions.append((_("Launch"), 'launch'))
        elif state == 'installing':
            actions = [(_("Installing…"), 'pending')]
        elif state == 'launching':
            actions = [(_("Launching…"), '')]
        elif state == 'removing':
            actions = [(_("Removing…"), 'pending')]

        x = width - 440 - 20
        for text, task in actions:
            pl.set_markup(m % escape(text))
            pla = pl.get_pixel_extents()[1]
            if task:
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
            x -= pla.width + 20 + 20
        cr.set_dash([1, 0])

        # ### images ### #
        im_height = height // 2 - 50
        h = im_height
        tim_width = width - 440 - 40

        cr.set_line_width(1)

        x, y = 20, 65
        tx = x

        cr.new_path()
        cr.arc(x + tim_width - 5 + 0.5, y + 5 + 0.5, 5, - pi / 2, 0)
        cr.arc(x + tim_width - 5 + 0.5, y + h - 5 + 0.5, 5, 0, pi / 2)
        cr.arc(x + 5 + 0.5, y + h - 5 + 0.5, 5, pi / 2, pi)
        cr.arc(x + 5 + 0.5, y + 5 + 0.5, 5, pi, 3 * pi / 2)
        cr.close_path()
        cr.save()
        cr.clip()
        i = 0
        while (tx < x + tim_width and i < len(self.screenshots) and
               self.screenshots[i] and
               self.screenshots[i] != 'needs-download'):
            if tx == x:
                self.clicks.append(['gallery', 0, x, x + tim_width, y, y + h])
            f = self.screenshots[i]
            # image
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_size(f, -1, h)
            except:
                pb = None
            i += 1
            if pb:
                Gdk.cairo_set_source_pixbuf(cr, pb, tx, y)
                cr.paint_with_alpha(0.9)
                tx += pb.get_width()
                if i == len(self.screenshots):
                    i = 0
        cr.restore()
        cr.set_source_rgba(0, 0, 0, 0.1)
        cr.new_path()
        cr.arc(x + tim_width - 5 + 0.5, y + 5 + 0.5, 5, - pi / 2, 0)
        cr.arc(x + tim_width - 5 + 0.5, y + h - 5 + 0.5, 5, 0, pi / 2)
        cr.arc(x + 5 + 0.5, y + h - 5 + 0.5, 5, pi / 2, pi)
        cr.arc(x + 5 + 0.5, y + 5 + 0.5, 5, pi, 3 * pi / 2)
        cr.close_path()
        cr.stroke()

        # ### body ### #
        # summary
        bwidth = width - 440 - 40 - 40
        x, y = 40, y + im_height + 30
        pl = widget.create_pango_layout('')
        pl.set_width(bwidth * Pango.SCALE)
        m = '<span font="16" weight="light" color="#444">%s</span>'
        pl.set_markup(m % escape(self.app.summary))
        Gtk.render_layout(context, cr, x, y, pl)
        y += pl.get_pixel_extents()[1].height + 10

        # keys
        ad = self.app.addons
        if len(ad) <= 2:
            nice_addons = ', '.join(ad)
        else:
            nice_addons = ad[0] + " (+%d)" % (len(ad) - 1)

        def dispurl(url):
            if '://' in url:
                url = url.split('://')[1]
            if url.endswith('/'):
                url = url[:-1]
            if url.startswith('www.'):
                url = url[4:]
            if url.startswith('mailto:'):
                url = url[7:]
            return url

        metadata = [
            [_("Identifier"), self.app.id],
            [_("Addons"), nice_addons],
            [_("Version"), self.app.version[1] or self.app.version[0]],
            [_("Origin"), self.app.origin],
            [_("License"), self.app.license],
            [_("Website"), dispurl(self.app.website)],
        ]
        pl = widget.create_pango_layout('')
        pl.set_width(150 * Pango.SCALE)
        kwidths, twidths = [], []
        for key, value in metadata:
            pl.set_markup('<span weight="light">%s</span>' % escape(key))
            plw = pl.get_pixel_extents()[1].width
            kwidths.append(plw)
            pl.set_markup('<span weight="light">%s</span>' % escape(value))
            twidths.append(plw + 10 + pl.get_pixel_extents()[1].width)
        kwidth = max(kwidths)
        x = 40 + bwidth - max(twidths)
        ty = y
        for key, value in metadata:
            if not value:
                continue
            pl.set_markup('<span color="#888" weight="light">%s</span>' %
                          escape(key))
            pla = pl.get_pixel_extents()[1]
            Gtk.render_layout(context, cr, x + kwidth - pla.width, ty, pl)
            if key in [_("Addons"), _("Website")]:
                pl.set_markup('<span weight="light"><u>%s</u></span>' %
                              escape(value))
            else:
                pl.set_markup('<span weight="light">%s</span>' % escape(value))
            pla = pl.get_pixel_extents()[1]
            if key == _("Addons"):
                self.clicks.append(['addons', '', x + kwidth + 10,
                                    x + kwidth + 10 + pla.width, ty,
                                    ty + pla.height])
            elif key == _("Website"):
                self.clicks.append(['url', self.app.website, x + kwidth + 10,
                                    x + kwidth + 10 + pla.width, ty,
                                    ty + pla.height])
            Gtk.render_layout(context, cr, x + kwidth + 10, ty, pl)
            ty += pla.height + 3
        cr.set_line_width(1)
        cr.set_source_rgba(221 / 255, 72 / 255, 20 / 255, 0.1)
        cr.move_to(x - 19.5, y + 0.5)
        cr.line_to(x - 19.5, ty - 3 + 0.5)
        cr.stroke()

        # description
        pl = widget.create_pango_layout('')
        pl.set_width((x - 40 - 40) * Pango.SCALE)
        m = '<span font="12.5" weight="light" color="#444">%s</span>'
        pl.set_markup(m % escape(self.app.description))
        Gtk.render_layout(context, cr, 40, y, pl)

        # overflow
        h = pl.get_pixel_extents()[1].height
        if y + h > height:
            self.clicks.append(['descrip', True, 40, x - 40, y, height])
            x = x // 2
            y = height
            cr.set_source_rgb(221 / 255, 72 / 255, 20 / 255)  # orange
            cr.new_path()
            cr.move_to(x - 30 + 0.5, y + 0.5)
            cr.arc(x - 25 + 0.5, y - 25 + 0.5, 5, pi, 3 * pi / 2)
            cr.arc(x + 25 + 0.5, y - 25 + 0.5, 5, 3 * pi / 2, 2 * pi)
            cr.line_to(x + 30 + 0.5, y + 0.5)
            cr.close_path()
            cr.fill()
            cr.set_source_rgb(1, 1, 1)
            cr.set_line_width(3)
            cr.move_to(x - 15, y - 20)
            cr.line_to(x, y - 10)
            cr.line_to(x + 15, y - 20)
            cr.stroke()

        # ### reviews ### #
        x, y = width - 420, 65

        # title
        pl = widget.create_pango_layout('')
        m = '<span color="#ffffff" size="x-large" weight="light">%s</span>'
        pl.set_markup(m % escape(_("Reviews")))
        pla = pl.get_pixel_extents()[1]
        Gtk.render_layout(context, cr, x, 25 - pla.height // 2, pl)

        # lang
        m = '<span color="#fff" font="22" weight="light">%s</span>'
        pl.set_markup(m % escape("⚙"))
        pla = pl.get_pixel_extents()[1]
        Gtk.render_layout(context, cr, width - 25 - pla.width // 2,
                          25 - pla.height // 2, pl)
        cr.set_line_width(1)
        cr.set_source_rgba(1, 1, 1, 0.1)
        cr.move_to(width - 50 + 0.5, 0.5)
        cr.line_to(width - 50 + 0.5, 49.5)
        cr.stroke()
        self.clicks.append(['langpop', True, width - 50, width, 0, 50])

        # write
        if self.app.state == 'installed':
            o = self.app.origin_id
            if o.startswith('U/') or o.startswith('S/') or o == 'P':
                m = '<span color="#fff" size="large" weight="light">%s</span>'
                pl.set_markup(m % escape(_("Write a Review")))
                pla = pl.get_pixel_extents()[1]
                cr.set_source_rgba(1, 1, 1, 0.95)
                cr.set_line_width(1)
                cr.set_dash([2, 2])
                cr.move_to(width - 50 - 20 - 10 - pla.width - 10 + 0.5,
                           25 + pla.height // 2 + 4.5)
                cr.line_to(width - 50 - 20 + 0.5, 25 + pla.height // 2 + 4.5)
                cr.stroke()
                Gtk.render_layout(context, cr, width - 50 - 20 - pla.width -
                                  10, 25 - pla.height // 2, pl)
                self.clicks.append(['write', '', width - 90 - pla.width,
                                    width - 50 - 20, 10, 40])

        pl1 = widget.create_pango_layout('')
        pl1.set_width((400 - 50 - 10) * Pango.SCALE)
        cr.set_dash([2, 2])

        i = self.rcols[self.rindex]
        while y <= height and i < len(self.reviews[self.lang]):
            review = self.reviews[self.lang][i]
            # calculate heights
            if self.username and review.reviewer_id == self.username:
                action = 'delete'
                text = _("delete review")
            else:
                action = 'moderate'
                text = _("flag review")
            m = ('<span font="12.5" weight="light" color="#444">%s</span>'
                 '\n<span font="1">\n</span>'
                 '<span font="10" weight="light" color="#444">%s</span>'
                 '\n<span font="1">\n</span>'
                 '<span font="9" weight="light" color="#777">%s  /  %s  /  '
                 '<u>%s</u></span>')
            m = m % (escape(review.summary),
                     escape(review.review.strip().replace('\n', ' ')),
                     escape(review.reviewer),
                     escape(review.date.split()[0]),
                     escape(text),)
            pl1.set_markup(m, -1)
            pl1h = pl1.get_pixel_extents()[1].height

            # color
            r = review.rating
            if r == 1:
                cr.set_source_rgb(0.8, 0, 0)
            elif r == 2:
                cr.set_source_rgb(0.8, 0.4, 0.2)
            elif r == 3:
                cr.set_source_rgb(0, 0.8, 0)
            cr.new_path()
            cr.arc(x + 50 - 5 + 0.5, y + 5 + 0.5, 5, - pi / 2, 0)
            cr.arc(x + 50 - 5 + 0.5, y + 50 - 5 + 0.5, 5, 0, pi / 2)
            cr.arc(x + 5 + 0.5, y + 50 - 5 + 0.5, 5, pi / 2, pi)
            cr.arc(x + 5 + 0.5, y + 5 + 0.5, 5, pi, 3 * pi / 2)
            cr.close_path()
            cr.fill()

            cr.set_line_width(1)
            cr.set_source_rgba(0, 0, 0, 0.1)
            cr.new_path()
            cr.arc(x + 50 - 5 + 0.5, y + 5 + 0.5, 5, - pi / 2, 0)
            cr.arc(x + 50 - 5 + 0.5, y + 50 - 5 + 0.5, 5, 0, pi / 2)
            cr.arc(x + 5 + 0.5, y + 50 - 5 + 0.5, 5, pi / 2, pi)
            cr.arc(x + 5 + 0.5, y + 5 + 0.5, 5, pi, 3 * pi / 2)
            cr.close_path()
            cr.stroke()

            # schmile :)
            cr.set_line_width(3)
            cr.set_source_rgb(1, 1, 1)
            cr.move_to(x + 20, y + 15)
            cr.line_to(x + 20, y + 25)
            cr.move_to(x + 30, y + 15)
            cr.line_to(x + 30, y + 25)
            if r == 1:
                cr.move_to(x + 10, y + 40)
                cr.curve_to(x + 20, y + 35, x + 30, y + 35, x + 40, y + 40)
            elif r == 2:
                cr.move_to(x + 10, y + 35)
                cr.curve_to(x + 20, y + 37, x + 30, y + 37, x + 40, y + 35)
            elif r == 3:
                cr.move_to(x + 10, y + 35)
                cr.curve_to(x + 20, y + 40, x + 30, y + 40, x + 40, y + 35)
            cr.stroke()

            # render text
            Gtk.render_layout(context, cr, x + 60, y, pl1)
            ind = pl1.xy_to_index(400 * Pango.SCALE, 1000 * Pango.SCALE)[1] + 1
            x2 = x + 60 + pl1.index_to_pos(ind).x // Pango.SCALE
            fy = y + pl1.index_to_pos(ind).y // Pango.SCALE
            ind -= len(text)
            x1 = x + 60 + pl1.index_to_pos(ind).x // Pango.SCALE
            self.clicks.append([action, review.id, x1, x2, fy,
                                y + max(50, pl1h)])

            y += 15 + max(50, pl1h)
            i += 1

        cr.set_dash([1, 0])
        if y <= height:
            self.get_reviews()
        else:
            self.rcols = self.rcols[:self.rindex + 1] + [i - 1]

        # back/forward
        if self.rindex or self.rindex < len(self.rcols) - 1:
            x = width - 220
            y = height
            cr.set_source_rgb(221 / 255, 72 / 255, 20 / 255)  # orange
            cr.new_path()
            cr.move_to(x - 60 + 0.5, y + 0.5)
            cr.arc(x - 55 + 0.5, y - 25 + 0.5, 5, pi, 3 * pi / 2)
            cr.arc(x + 55 + 0.5, y - 25 + 0.5, 5, 3 * pi / 2, 2 * pi)
            cr.line_to(x + 60 + 0.5, y + 0.5)
            cr.close_path()
            cr.fill()
            cr.set_line_width(1)
            cr.set_source_rgba(1, 1, 1, 0.2)
            cr.move_to(x + 0.5, y + 0.5)
            cr.line_to(x + 0.5, y - 30 + 0.5)
            cr.stroke()
            cr.set_source_rgb(1, 1, 1)
            cr.set_line_width(3)
            self.clicks.insert(0, ['', '', x - 60, x + 60, y - 30, y])
            if self.rindex:
                cr.move_to(x - 30 - 15, y - 10)
                cr.line_to(x - 30, y - 20)
                cr.line_to(x - 30 + 15, y - 10)
                self.clicks.insert(0, ['reviews', self.rindex - 1, x - 60, x,
                                       y - 30, y])
                self.scrolls.append('prevrev')
            if self.rindex < len(self.rcols) - 1:
                cr.move_to(x + 30 - 15, y - 20)
                cr.line_to(x + 30, y - 10)
                cr.line_to(x + 30 + 15, y - 20)
                self.clicks.insert(0, ['reviews', self.rindex + 1, x, x + 60,
                                       y - 30, y])
                self.scrolls.append('nextrev')
            cr.stroke()

        # ### language popup ### #
        if self.langpop:
            self.clicks = []
            self.scrolls = []
            self.clicks.append(['langpop', False, 0, width, 0, height])

            # data
            import locale
            try:
                lang = locale.getdefaultlocale()[0].split('_')[0]
            except:
                lang = 'en'
            from appdata.reviews import get_language_from_id
            data = [('local', get_language_from_id(lang).split(';')[0]),
                    ('any', _("All languages"))]

            # size math
            pl = widget.create_pango_layout('')
            m = '<span color="#dd4814" size="large" weight="light">%s</span>'
            pl.set_markup(m % escape(data[0][1]))
            pla = pl.get_pixel_extents()[1]
            locw, loch = pla.width, pla.height
            pl.set_markup(m % escape(data[1][1]))
            pla = pl.get_pixel_extents()[1]
            anyw, anyh = pla.width, pla.height

            w = 20 + max(locw, anyw) + 20
            h = 10 + loch + 10 + anyh + 10
            x, y = width - w, 50

            # draw
            cr.set_source_rgba(1, 1, 1, 0.9)
            cr.rectangle(x, y, w, h)
            cr.fill()
            pl.set_markup(m % escape(data[0][1]))
            Gtk.render_layout(context, cr, x + 20, y + 10, pl)
            self.clicks.insert(0, ['setlang', 'local', x, x + w, y,
                                   y + 10 + loch + 5])
            pl.set_markup(m % escape(data[1][1]))
            Gtk.render_layout(context, cr, x + 20, y + 10 + loch + 10, pl)
            self.clicks.insert(0, ['setlang', 'any', x, x + w,
                                   y + 10 + loch + 5, y + h])

        # ### zoom gallery ### #
        if self.scursor is not None:
            self.clicks = []
            self.scrolls = []

            # background
            cr.set_source_rgba(0, 0, 0, 0.6)
            cr.rectangle(0, 0, width, height)
            cr.fill()
            self.clicks.append(['gallery', None, 0, width, 0, height])

            # screenshot
            path = self.screenshots[self.scursor]
            if path == 'needs-download':
                path.connect('downloaded', lambda w, f: self.queue_draw())
                return
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_size(path, width - 80,
                                                            height - 60)
            except:
                if (path.startswith('/home/') and
                        path.split('/')[4] == 'appgrid' and
                        len(path.split('/')) == 6):
                    import os
                    os.remove(path)  # corrupted file
                if self.scursor < len(self.screenshots) - 1:
                    self.scursor += 1
                self.queue_draw()
                return
            w, h = pb.get_width(), pb.get_height()
            x, y = (width - w) // 2, (height - h) // 2
            Gdk.cairo_set_source_pixbuf(cr, pb, x, y)
            cr.paint()
            if self.scursor == len(self.screenshots) - 1:
                res = None
            else:
                res = self.scursor + 1
            self.clicks.insert(0, ['gallery', res, x, x + w, y, y + h])

            # next / prev
            x, y = width, height // 2
            if self.scursor > 0 or self.scursor < len(self.screenshots) - 1:
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
                if self.scursor > 0:
                    cr.move_to(x - 10, y - 30 - 15)
                    cr.line_to(x - 20, y - 30)
                    cr.line_to(x - 10, y - 30 + 15)
                    self.clicks.insert(0, ['gallery', self.scursor - 1, x - 30,
                                           x, y - 60, y])
                if self.scursor < len(self.screenshots) - 1:
                    cr.move_to(x - 20, y + 30 - 15)
                    cr.line_to(x - 10, y + 30)
                    cr.line_to(x - 20, y + 30 + 15)
                    self.clicks.insert(0, ['gallery', self.scursor + 1, x - 30,
                                           x, y, y + 60])
                cr.stroke()

        # ### zoom descrip ### #
        if self.descrip:  # FIXME: do better than this..
            self.clicks = []
            self.scrolls = []

            # background
            cr.set_source_rgba(0, 0, 0, 0.6)
            cr.rectangle(0, 0, width, height)
            cr.fill()
            self.clicks.append(['descrip', False, 0, width, 0, height])

            # math
            pl = widget.create_pango_layout('')
            pl.set_width((width // 2) * Pango.SCALE)
            m = '<span font="12.5" weight="light" color="#444">%s</span>'
            pl.set_markup(m % escape(self.app.description))
            pla = pl.get_pixel_extents()[1]

            # draw
            x = width // 2 - pla.width // 2 - 40
            y = height // 2 - pla.height // 2 - 40
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(x, y, pla.width + 80, pla.height + 80)
            cr.fill()
            Gtk.render_layout(context, cr, x + 20, y + 20, pl)
