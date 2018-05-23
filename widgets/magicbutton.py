# -*- coding: utf-8 -*-
# This code is copyrighted and all rights are reserved
# for full legalities see the LEGAL file
from gi.repository import GLib, Gtk
from defer import inline_callbacks
from appdata import _

escape = GLib.markup_escape_text


class MagicButton(Gtk.Alignment):
    def __init__(self, app):
        Gtk.Alignment.__init__(self)

        self.set(0.5, 0.5, 0, 0)

        vbox = Gtk.VBox()
        vbox.set_spacing(5)
        self.add(vbox)

        self.app = app
        self.callbacks = ()
        self.progress = 0

        self.button = Gtk.EventBox()
        self.button.set_size_request(150, 30)

        def on_button_press(widget, e):
            if not self.callbacks:
                return
            rtl = self.get_direction() == Gtk.TextDirection.RTL
            if len(self.callbacks) == 1:
                self.callbacks[0]()
            elif e.x >= widget.get_allocation().width - 30 and not rtl:
                self.callbacks[1]()
            elif e.x <= 30 and rtl:
                self.callbacks[1]()
            else:
                self.callbacks[0]()
        self.button.connect('button-press-event', on_button_press)

        def draw_button(widget, cr):
            a = widget.get_allocation()
            from math import pi
            r = 5
            rtl = self.get_direction() == Gtk.TextDirection.RTL
            if len(self.callbacks) == 2 and rtl:
                cr.set_source_rgba(174 / 255, 167 / 255, 159 / 255, 0.8)  # wgr
                cr.arc(r, r, r, pi, 1.5 * pi)
                cr.arc(30, 0, 0, 1.5 * pi, 2 * pi)
                cr.arc(30, a.height, 0, 0, 0.5 * pi)
                cr.arc(r, a.height - r, r, 0.5 * pi, pi)
                cr.fill()
                cr.set_source_rgba(221 / 255, 72 / 255, 20 / 255, 0.8)  # orang
                cr.arc(30, 0, 0, pi, 1.5 * pi)
                cr.arc(a.width - r, r, r, 1.5 * pi, 2 * pi)
                cr.arc(a.width - r, a.height - r, r, 0, 0.5 * pi)
                cr.arc(30, a.height, 0, 0.5 * pi, pi)
                cr.fill()
            elif len(self.callbacks) == 2:
                cr.set_source_rgba(221 / 255, 72 / 255, 20 / 255, 0.8)  # orang
                cr.arc(r, r, r, pi, 1.5 * pi)
                cr.arc(a.width - 30, 0, 0, 1.5 * pi, 2 * pi)
                cr.arc(a.width - 30, a.height, 0, 0, 0.5 * pi)
                cr.arc(r, a.height - r, r, 0.5 * pi, pi)
                cr.fill()
                cr.set_source_rgba(174 / 255, 167 / 255, 159 / 255, 0.8)  # wgr
                cr.arc(a.width - 30, 0, 0, pi, 1.5 * pi)
                cr.arc(a.width - r, r, r, 1.5 * pi, 2 * pi)
                cr.arc(a.width - r, a.height - r, r, 0, 0.5 * pi)
                cr.arc(a.width - 30, a.height, 0, 0.5 * pi, pi)
                cr.fill()
            else:
                if not self.callbacks or self.callbacks[0] == self.on_remove:
                    cr.set_source_rgba(174 / 255, 167 / 255, 159 / 255, 0.8)
                else:  # warm grey ^; vv orange
                    cr.set_source_rgba(221 / 255, 72 / 255, 20 / 255, 0.8)
                cr.arc(r, r, r, pi, 1.5 * pi)
                cr.arc(a.width - r, r, r, 1.5 * pi, 2 * pi)
                cr.arc(a.width - r, a.height - r, r, 0, 0.5 * pi)
                cr.arc(r, a.height - r, r, 0.5 * pi, pi)
                cr.fill()
                cr.set_source_rgba(1, 1, 1, 0.3)
                cr.rectangle(0, 0, self.progress / 100 * a.width, a.height)
                cr.fill()
        self.button.connect('draw', draw_button)
        vbox.pack_start(self.button, False, False, 0)

        self.subscript = Gtk.Label()
        vbox.pack_start(self.subscript, False, False, 0)

        self.set_state(self.get_state(), initial=True)

    def get_state(self):
        import subprocess
        o = subprocess.check_output(["dpkg", "--get-selections", self.app.id],
                                    stderr=subprocess.STDOUT).decode('utf8')
        line = o.split('\n')[0]
        if (line.split('\t')[0].split(':')[0] == self.app.id.split(':')[0] and
                line.endswith('\tinstall')):
            return 'installed'
        return 'available'

    def set_state(self, state, initial=False):
        for child in self.button.get_children():
            self.button.remove(child)
        self.callbacks = ()
        self.show_all()
        self.subscript.hide()
        self.subscript.set_markup("<small></small>")
        self.progress = 0

        def set_button_label(text):
            l = Gtk.Label()
            l.set_markup("<span color='white'><big>%s</big></span>" %
                         escape(text))
            l.show()
            self.button.add(l)
            self.button.show_all()
        if state == 'available':
            self.callbacks = (self.on_install, )
            set_button_label(_("Install"))
        elif state == 'installed':
            import subprocess
            try:
                o = subprocess.check_output(["dpkg", "-L", self.app.id],
                                            stderr=subprocess.STDOUT
                                            ).decode('utf8')
            except:
                o = ''
            candidates = []
            o = o.split('\n')
            o.reverse()
            import codecs
            for line in o:
                if ((line.startswith('/usr/share/applications/') or
                        line.startswith('/opt/')) and
                        line.endswith('.desktop')):
                    if '\nExec=' in codecs.open(line, 'r', 'utf8').read():
                        candidates.append(line)
            if candidates:
                self.callbacks = (self.on_launch, self.on_remove)
                hbox = Gtk.HBox()
                self.button.add(hbox)
                l = Gtk.Label()
                l.set_markup("<span color='white'><big>%s</big></span>" %
                             escape(_("Launch")))
                hbox.pack_start(l, True, True, 0)
                b = Gtk.HBox()
                b.set_size_request(30, 30)
                hbox.pack_start(b, False, False, 0)
                i = Gtk.Image.new_from_icon_name('user-trash-symbolic',
                                                 Gtk.IconSize.MENU)
                i.get_style_context().add_class('whitecolor')
                b.add(i)
                self.button.show_all()
            else:
                self.callbacks = (self.on_remove, )
                self.style = 'secondary'
                set_button_label(_("Remove"))
        elif state == 'installing':
            set_button_label(_("Installing…"))
        elif state == 'launching':
            set_button_label(_("Launching…"))
            GLib.timeout_add(10000, self.set_state, self.get_state())
        elif state == 'removing':
            set_button_label(_("Removing…"))
        if not initial:
            while Gtk.events_pending():
                Gtk.main_iteration()

    def on_install(self):
        self.set_state('installing')
        if hasattr(self.app, '_filename'):
            self.do_commit(install=[self.app._filename])
        else:
            self.do_commit(install=[self.app.id])

    def on_launch(self):
        self.set_state('launching')

        import subprocess
        try:
            o = subprocess.check_output(["dpkg", "-L", self.app.id],
                                        stderr=subprocess.STDOUT
                                        ).decode('utf8')
        except:
            o = ''
        candidates = []
        o = o.split('\n')
        o.reverse()
        for line in o:
            if ((line.startswith('/usr/share/applications/') or
                 line.startswith('/opt/')) and
                    line.endswith('.desktop')):
                with open(line) as f:
                    if '\nExec=' in f.read():
                        candidates.append(line)
        if candidates:
            candidates.sort(key=len)
            from gi.repository import Gio
            ai = Gio.DesktopAppInfo.new_from_filename(candidates[0])
            ai.launch([], None)  # must be [] for 12.04

    def on_remove(self):
        self.set_state('removing')
        self.do_commit(remove=[self.app.id])

    @inline_callbacks
    def do_commit(self, install=[], remove=[]):
        from aptdaemon.client import AptClient
        ac = AptClient()
        if install and install[0].endswith('.deb'):
            trans = yield ac.install_file(install[0], force=True,
                                          defer=True)
        else:
            trans = yield ac.commit_packages(install=install,
                                             reinstall=[],
                                             remove=remove,
                                             purge=[],
                                             upgrade=[],
                                             downgrade=[],
                                             defer=True)

        def on_finished(transaction, exit_state):
            if exit_state == 'exit-failed':
                if (transaction.error and
                        not trans.error.code == 'error-not-authorized'):
                    from widgets.sc import sc
                    from widgets.transaction_failed import TransactionFailed
                    sc.add_small_overlay(TransactionFailed(trans))
                self.set_state(self.get_state())
                return

            def update_state_button():
                self.set_state(self.get_state())
            GLib.timeout_add(1500, update_state_button)
        trans.connect('finished', on_finished)

        @inline_callbacks
        def on_config_file_conflict(transaction, old, new):
            from aptdaemon.gtk3widgets import AptConfigFileConflictDialog
            acfcd = AptConfigFileConflictDialog(old, new)
            response = acfcd.run()
            acfcd.hide()
            acfcd.destroy()
            if response == Gtk.ResponseType.YES:
                yield transaction.resolve_config_file_conflict(old, 'replace',
                                                               defer=True)
            else:
                yield transaction.resolve_config_file_conflict(old, 'keep',
                                                               defer=True)
        trans.connect('config-file-conflict', on_config_file_conflict)

        @inline_callbacks
        def on_medium_required(transaction, medium, drive):
            from aptdaemon.gtk3widgets import AptMediumRequiredDialog
            amrd = AptMediumRequiredDialog(medium, drive)
            response = amrd.run()
            amrd.hide()
            amrd.destroy()
            if response == Gtk.ResponseType.YES:
                yield transaction.provide_medium(medium, defer=True)
            else:
                yield transaction.cancel(defer=True)
        trans.connect('medium-required', on_medium_required)

        def on_progress_changed(transaction, progress):
            self.progress = progress
            self.button.queue_draw()
        trans.connect('progress-changed', on_progress_changed)
        trans.set_debconf_frontend('gnome', defer=True)
        trans.set_remove_obsoleted_depends(True, defer=True)

        try:
            yield trans.simulate(defer=True)
        except:
            return

        @inline_callbacks
        def on_removal_warning(widget):
            if widget.approved:
                try:
                    yield trans.run(defer=True)
                except:
                    pass
            else:
                yield trans.cancel(defer=True)
                self.set_state(self.get_state())

        removals = [str(r).split('=')[0] for r in trans.dependencies[2]]
        if removals:
            from widgets.sc import sc
            from widgets.removal_warnings import RemovalWarnings
            rw = RemovalWarnings(removals)
            rw.connect('unmap', on_removal_warning)
            sc.add_small_overlay(rw)
        else:
            try:
                yield trans.run(defer=True)
            except:
                pass
