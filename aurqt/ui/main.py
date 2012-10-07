#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.main
    ~~~~~~~~~~~~~
    The main window.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import __version__, DS, _
from .about import AboutDialog
from .loginform import LoginForm
from PyQt4 import QtGui, QtCore
import sys
import subprocess


class Main(QtGui.QMainWindow):
    def logagenerate(self):
        """Generate the appropriate login/logout button."""
        if DS.sid:
            # TRANSLATORS: {} = username
            self.loga.setText(_('&Log out [{}]').format(DS.username))
            self.loga.setStatusTip(_('Log out.'))
        else:
            self.loga.setText(_('&Log in'))
            self.loga.setStatusTip(_('Log in.'))

    def __init__(self):
        """Initialize the window."""
        super(Main, self).__init__()

        # Actions.  TODO THOSE CONNECTIONS _MAY_ BE WRONG
        upgrade = QtGui.QAction(
            QtGui.QIcon.fromTheme('system-software-update'),
            _('&Upgrade'), self)
        upgrade.setShortcut('Ctrl+U')
        upgrade.setStatusTip(_('Upgrade installed packages.'))
        upgrade.triggered.connect(self.upgrade)

        upload = QtGui.QAction(QtGui.QIcon.fromTheme('list-add'),
                               _('Upl&oad…'), self)
        upload.setShortcut('Ctrl+Shift+U')
        upload.setStatusTip(_('Upload a package to the AUR.'))
        upload.triggered.connect(self.upload)

        search = QtGui.QAction(QtGui.QIcon.fromTheme('edit-find'),
                               _('&Search…'), self)
        search.setShortcut('Ctrl+S')
        search.setStatusTip(_('Search the AUR.'))
        search.triggered.connect(self.search)

        prefs = QtGui.QAction(QtGui.QIcon.fromTheme('configure'),
                              _('&Preferences'), self)
        prefs.setShortcut('Ctrl+,')
        prefs.setStatusTip(_('Open the preferences window for aurqt.'))
        prefs.triggered.connect(self.prefs)

        quit = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'),
                             _('&Quit'), self)
        quit.setShortcut('Ctrl+Q')
        quit.setStatusTip(_('Quit aurqt.'))
        quit.triggered.connect(QtGui.qApp.quit)

        self.loga = QtGui.QAction(QtGui.QIcon.fromTheme('user-identity'),
                                  '&L', self)
        self.loga.setShortcut('Ctrl+L')
        self.loga.setStatusTip('Log in/out (not to be seen!)')
        self.logagenerate()
        self.loga.triggered.connect(self.log)

        mypkgs = QtGui.QAction(QtGui.QIcon.fromTheme('folder-tar'),
                               _('&My packages'), self)
        mypkgs.setShortcut('Ctrl+M')
        mypkgs.setStatusTip(_('Display my packages.'))
        mypkgs.triggered.connect(self.mine)

        ohelp = QtGui.QAction(QtGui.QIcon.fromTheme('help-contents'),
                              _('Online &Help'), self)
        ohelp.setShortcut('F1')
        ohelp.setStatusTip(_('Show the online help for aurqt.'))
        ohelp.triggered.connect(self.halp)

        about = QtGui.QAction(QtGui.QIcon.fromTheme('help-about'),
                              _('A&bout'), self)
        about.setStatusTip('aurqt v{} — Copyright © 2012, Kwpolska.'.format(
                           __version__))
        about.triggered.connect(self.about)

        # Menu.
        menu = self.menuBar()
        filemenu = menu.addMenu(_('&File'))

        filemenu.addAction(upgrade)
        filemenu.addSeparator()
        filemenu.addAction(upload)
        filemenu.addAction(search)
        filemenu.addSeparator()
        filemenu.addAction(prefs)
        filemenu.addAction(quit)

        accountmenu = menu.addMenu(_('&Account'))
        accountmenu.addAction(self.loga)
        accountmenu.addAction(mypkgs)

        helpmenu = menu.addMenu(_('&Help'))
        helpmenu.addAction(ohelp)
        helpmenu.addAction(about)

        # Toolbar.
        toolbar = self.addToolBar(_('aurqt — main window'))

        toolbar.setIconSize(QtCore.QSize(22, 22))
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        toolbar.addAction(upgrade)
        toolbar.addSeparator()
        toolbar.addAction(upload)
        toolbar.addAction(search)
        toolbar.addSeparator()
        toolbar.addAction(self.loga)
        toolbar.addAction(quit)

        # MDI.
        self.mdiArea = QtGui.QMdiArea()
        self.setCentralWidget(self.mdiArea)

        # Statusbar.
        self.statusBar().showMessage('aurqt v{} — Copyright © 2012, '
                                     'Kwpolska.'.format(__version__))

        # Almost done...
        self.resize(800, 600)
        self.setWindowTitle('aurqt')
        self.setWindowIcon(QtGui.QIcon.fromTheme('go-home'))  # TODO.  When we
                                                              # have one.
        self.show()

    def upload(self, *args):
        print('upload')
        print(args)

    def search(self, *args):
        print('search')
        print(args)

    def prefs(self, *args):
        print('prefs')
        print(args)

    def upgrade(self, *args):
        print('upgrade')
        print(args)

    def log(self, *args):
        """Log in or out."""
        if DS.sid:
            try:
                DS.logout()
                QtGui.QMessageBox.information(self, 'aurqt', _('Logged out.'))
            except AQError as e:
                QtGui.QMessageBox.error(self, 'aurqt', e.msg,
                                        QtGui.QMessageBox.Ok)
            self.logagenerate()
        else:
            l = LoginForm()
            l.exec_()
            self.logagenerate()

    def mine(self, *args):
        print('mine')
        print(args)

    def halp(self):
        """View the help (online).  import webbrowser fails miserably."""
        subprocess.call(['xdg-open', 'http://aurqt.rtfd.org'])

    def about(self, *args):
        """Show the about dialog."""
        a = AboutDialog(self)
        a.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        a.exec_()


def main():
    """The main routine for the UI."""
    app = QtGui.QApplication(sys.argv)
    main = Main()
    return app.exec_()
