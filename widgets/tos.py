# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GLib, Gtk
from widgets.basics import Button
from appdata import _

escape = GLib.markup_escape_text

disclaimer = ('THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBU'
              'TORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, '
              'BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY A'
              'ND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT'
              ' SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY D'
              'IRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTI'
              'AL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBST'
              'ITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSI'
              'NESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILIT'
              'Y, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NE'
              'GLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THI'
              'S SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.')


class TermsOfService(Gtk.VBox):
    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_border_width(25)
        self.set_spacing(10)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_line_wrap(True)
        markup = _("Welcome to App Grid!")
        smarkup = _("In order to use App Grid, you will need to agree to "
                    "the following:")
        l.set_markup('<big>%s</big>\n%s' % (escape(markup), escape(smarkup)))
        self.pack_start(l, False, False, 0)

        # terms
        sw = Gtk.ScrolledWindow()
        self.pack_start(sw, True, True, 0)

        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_line_wrap(True)
        l.set_markup(escape(disclaimer))
        sw.add(l)

        # full info
        l = Gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_line_wrap(True)
        l.set_markup(escape(_("Please see /usr/share/appgrid/LEGAL for full "
                              "details.")))
        self.pack_start(l, False, False, 0)

        # (dis)agree
        h = Gtk.HBox()
        h.set_spacing(20)
        self.pack_start(h, False, False, 0)

        def on_agree():
            import os.path
            path = os.path.expanduser('~') + '/.config/appgrid/'
            if not os.path.exists(path):
                import os
                os.mkdir(path)
            f = open(path + 'bsd2_accepted', 'w')
            f.close()
            self.hide()
        b = Button()
        b.set_text(_("I Agree"))
        b.set_callback(on_agree)
        h.pack_end(b, False, False, 0)

        def on_disagree(widget, args):
            if args == 'disagree':
                Gtk.main_quit()
            return True
        l = Gtk.Label()
        l.set_markup('<a href="disagree">%s</a>' % escape(_("I disagree")))
        l.connect('activate-link', on_disagree)
        h.pack_end(l, False, False, 0)

        self.show_all()
