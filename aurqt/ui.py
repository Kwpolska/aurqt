#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

# Names convention: pkg = a package object, pkgname = a package name.

"""
    pkgbuilder.AUR
    ~~~~~~~~~~~~~~
    A class for calling the AUR API.

    :Copyright: © 2011-2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""


"""The User Interface for aurqt."""

from . import __version__, __pbversion__, _, AQError
from PyQt4 import QtGui, QtCore
import sys

class About(QtGui.QDialog):
    def __init__(self):
        """Initialize the dialog."""
        super(About, self).__init__()

        self.setWindowTitle(_('About aurqt'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('help-about'))

        lay = QtGui.QVBoxLayout(self)

        aurqt = QtGui.QLabel('aurqt v{}'.format(__version__), self)
        tagline = QtGui.QLabel(_('INSERT TAGLINE HERE.'), self)
        copyright = QtGui.QLabel(_('Copyright © 2012, Kwpolska.'), self)
        pb = QtGui.QLabel(_('Using PKGBUILDer v{}.').format(__pbversion__),
                          self)
        okay = QtGui.QDialogButtonBox(self)
        okay.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        font = QtGui.QFont()
        font.setPointSize(20)

        aurqt.setFont(font)
        aurqt.setAlignment(QtCore.Qt.AlignCenter)
        tagline.setAlignment(QtCore.Qt.AlignCenter)

        lay.addWidget(aurqt)
        lay.addWidget(tagline)
        lay.addWidget(copyright)
        lay.addWidget(pb)
        lay.addWidget(okay)

        QtCore.QObject.connect(okay, QtCore.SIGNAL('accepted()'), self.accept)
        QtCore.QObject.connect(okay, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)


        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)
        self.show()

class Main(QtGui.QMainWindow):
    def __init__(self):
        """Initialize the window."""
        super(Main, self).__init__()

        # Actions.
        upgrade = QtGui.QAction(QtGui.QIcon.fromTheme('system-software-update'), '&Upgrade',
                                self)
        upgrade.setShortcut('Ctrl+U')
        upgrade.setStatusTip('Upgrade installed packages.')
        upgrade.triggered.connect(self.upgrade)

        upload = QtGui.QAction(QtGui.QIcon.fromTheme('list-add'), 'Up&load…', self)
        upload.setShortcut('Ctrl+Shift+U')
        upload.setStatusTip('Upload a package to the AUR.')
        upload.triggered.connect(self.upload)

        search = QtGui.QAction(QtGui.QIcon.fromTheme('edit-find'), '&Search…', self)
        search.setShortcut('Ctrl+S')
        search.setStatusTip('Search the AUR.')
        search.triggered.connect(self.search)

        prefs = QtGui.QAction(QtGui.QIcon.fromTheme('configure'), '&Preferences', self)
        prefs.setShortcut('Ctrl+,')
        prefs.setStatusTip('Open the preferences window for aurqt.')
        prefs.triggered.connect(self.prefs)

        quit = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'), '&Quit', self)
        quit.setShortcut('Ctrl+Q')
        quit.setStatusTip('Quit aurqt.')
        quit.triggered.connect(QtGui.qApp.quit)

        log = QtGui.QAction(QtGui.QIcon.fromTheme('system-log-out'), '&Log in/out', self)
        log.setShortcut('Ctrl+L')
        log.setStatusTip('Log in our out.')
        log.triggered.connect(self.log)

        mypkgs = QtGui.QAction(QtGui.QIcon.fromTheme('user-identity'), '&My packages', self)
        mypkgs.setShortcut('Ctrl+M')
        mypkgs.setStatusTip('Display my packages.')
        mypkgs.triggered.connect(self.mine)

        ohelp = QtGui.QAction(QtGui.QIcon.fromTheme('help-contents'), 'Online &Help', self)
        ohelp.setShortcut('F1')
        ohelp.setStatusTip('Show the online help for aurqt.')
        ohelp.triggered.connect(self.halp)

        about = QtGui.QAction(QtGui.QIcon.fromTheme('help-about'), 'A&bout', self)
        about.setStatusTip('aurqt v{} — Copyright © 2012, Kwpolska.'.format(
                           __version__))
        about.triggered.connect(self.about)

        # Menu.
        menu = self.menuBar()
        filemenu = menu.addMenu('&File')

        filemenu.addAction(upgrade)
        filemenu.addSeparator()
        filemenu.addAction(upload)
        filemenu.addAction(search)
        filemenu.addSeparator()
        filemenu.addAction(prefs)
        filemenu.addAction(quit)

        accountmenu = menu.addMenu('&Account')
        accountmenu.addAction(log)
        accountmenu.addAction(mypkgs)

        helpmenu = menu.addMenu('&Help')
        helpmenu.addAction(ohelp)
        helpmenu.addAction(about)

        # Toolbar.
        toolbar = self.addToolBar('aurqt — main window')

        toolbar.setIconSize(QtCore.QSize(22, 22))
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        toolbar.addAction(upgrade)
        toolbar.addSeparator()
        toolbar.addAction(upload)
        toolbar.addAction(search)
        toolbar.addSeparator()
        toolbar.addAction(log)
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
        self.setWindowIcon(QtGui.QIcon.fromTheme('go-home'))  #TODO.  When we
                                                              # have one.
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)
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
        print('log')
        print(args)

    def mine(self, *args):
        print('mine')
        print(args)

    def halp(self, *args):
        print('halp')
        print(args)

    def about(self, *args):
        """Show the about dialog."""
        a = About()
        a.exec_()

def main():
    """The main routine."""
    app = QtGui.QApplication(sys.argv)
    mainapp = Main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
