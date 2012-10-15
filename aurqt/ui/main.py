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

from .. import __version__, DS, _, AQError
DS.log.info('*** Importing in .ui.main…')
DS.log.info('PyQt4')
from PyQt4 import QtGui, QtCore
DS.log.info('about')
from .about import AboutDialog
DS.log.info('account')
from .account import AccountDialog
DS.log.info('info')
from .info import InfoBox
DS.log.info('loginform')
from .loginform import LoginForm
DS.log.info('preferences')
from .preferences import PreferencesDialog
DS.log.info('search')
from .search import SearchDialog
DS.log.info('upgrade')
from .upgrade import UpgradeDialog
DS.log.info('external deps')
import sys
import subprocess
import threading
import time
import pickle
DS.log.info('pkgbuilder.upgrade')
import pkgbuilder.upgrade
DS.log.info('*** Importing done')

class Main(QtGui.QMainWindow):
    """The main window."""

    def logagenerate(self):
        """Generate the appropriate login/logout button."""
        if DS.sid:
            # TRANSLATORS: {} = username
            self.loga.setText(_('&Log out [{}]').format(DS.username))
            self.loga.setToolTip(_('Log out.'))
            self.accedita.setText(_('Account se&ttings'))
            self.accedita.setToolTip(_('Modify the settings of this '
                                       'account.'))
            self.accedita.setIcon(QtGui.QIcon.fromTheme(
                                  'user-group-properties'))
            self.loga.setEnabled(True)
            self.accedita.setEnabled(True)
            self.mypkgs.setEnabled(True)
        else:
            self.loga.setText(_('&Log in'))
            self.loga.setToolTip(_('Log in.'))
            self.accedita.setText(_('Regis&ter'))
            self.accedita.setToolTip(_('Register a new account.'))
            self.accedita.setIcon(QtGui.QIcon.fromTheme('user-group-new'))
            self.loga.setEnabled(True)
            self.accedita.setEnabled(True)
            self.mypkgs.setEnabled(False)

    def upgradeagenerate(self):
        """Generate the appropriate upgrade button."""
        DS.log.info('Checking AUR upgrades...')
        u = pkgbuilder.upgrade.Upgrade()
        ulist = u.list_upgradable(u.gather_foreign_pkgs())[0]

        if ulist:
            self.upgradea.setText(_('&Upgrade ({})').format(len(ulist)))
            self.upgradea.setToolTip(_('Upgrade installed packages.  '
                '  ({} upgrades available)').format(len(ulist)))
        else:
            self.upgradea.setText(_('&Upgrade').format(len(ulist)))
            self.upgradea.setToolTip(_('Upgrade installed packages.'
                ).format(len(ulist)))

        self.upgradea.setEnabled(True)
        DS.log.info('AUR upgrades check done; {} found'.format(len(ulist)))

    def sessiongenerate(self):
        """Handle session re-generation."""
        DS.log.info('Working on session re-generation...')
        while not DS.contstate:
            time.sleep(0.1)

        self.logagenerate()
        DS.log.info('Session re-generation done.')

    def __init__(self):
        """Initialize the window."""
        DS.log.info('Starting main window init...')
        super(Main, self).__init__()
        # Actions.
        self.upgradea = QtGui.QAction(
            QtGui.QIcon.fromTheme('system-software-update'),
            _('&Upgrade (…)'), self)
        self.upgradea.setShortcut('Ctrl+U')
        self.upgradea.setToolTip(_('[Getting upgrade count…]'))
        self.upgradea.setEnabled(False)
        QtCore.QObject.connect(self.upgradea, QtCore.SIGNAL('triggered()'), self.upgrade)

        upload = QtGui.QAction(QtGui.QIcon.fromTheme('list-add'),
                               _('Upl&oad…'), self)
        upload.setShortcut('Ctrl+Shift+U')
        upload.setToolTip(_('Upload a package to the AUR.'))
        QtCore.QObject.connect(upload, QtCore.SIGNAL('triggered()'), self.upload)

        search = QtGui.QAction(QtGui.QIcon.fromTheme('edit-find'),
                               _('&Search…'), self)
        search.setShortcut('Ctrl+S')
        search.setToolTip(_('Search the AUR.'))
        QtCore.QObject.connect(search, QtCore.SIGNAL('triggered()'), self.search)

        prefs = QtGui.QAction(QtGui.QIcon.fromTheme('configure'),
                              _('&Preferences'), self)
        prefs.setShortcut('Ctrl+,')
        prefs.setToolTip(_('Open the preferences window for aurqt.'))
        QtCore.QObject.connect(prefs, QtCore.SIGNAL('triggered()'), self.prefs)

        quit = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'),
                             _('&Quit'), self)
        quit.setShortcut('Ctrl+Q')
        quit.setToolTip(_('Quit aurqt.'))
        QtCore.QObject.connect(quit, QtCore.SIGNAL('triggered()'), QtGui.qApp.quit)

        try:
            loganame = _('&Log out [{}]').format(pickle.load(open(
                DS.sidfile, 'rb'))[1])
        except IOError:
            loganame = _('&Log in')

        self.loga = QtGui.QAction(QtGui.QIcon.fromTheme('user-identity'),
                                  loganame, self)
        self.loga.setShortcut('Ctrl+L')
        self.loga.setToolTip(_('Working on authentication…'))
        QtCore.QObject.connect(self.loga, QtCore.SIGNAL('triggered()'), self.log)
        self.loga.setEnabled(False)

        self.mypkgs = QtGui.QAction(QtGui.QIcon.fromTheme('folder-tar'),
                                    _('&My packages'), self)
        self.mypkgs.setShortcut('Ctrl+M')
        self.mypkgs.setToolTip(_('Display the users’ packages.'))
        QtCore.QObject.connect(self.mypkgs, QtCore.SIGNAL('triggered()'),
                               self.mine)

        self.accedita = QtGui.QAction(QtGui.QIcon.fromTheme(
                                      'user-group-properties'),
                                      _('Account se&ttings'), self)
        self.accedita.setShortcut('Ctrl+T')
        self.accedita.setToolTip(_('Working on authentication…'))
        QtCore.QObject.connect(self.accedita, QtCore.SIGNAL('triggered()'),
                               self.accedit)
        self.accedita.setEnabled(False)

        ohelp = QtGui.QAction(QtGui.QIcon.fromTheme('help-contents'),
                              _('Online &Help'), self)
        ohelp.setShortcut('F1')
        ohelp.setToolTip(_('Show the online help for aurqt.'))
        QtCore.QObject.connect(ohelp, QtCore.SIGNAL('triggered()'), self.halp)

        about = QtGui.QAction(QtGui.QIcon.fromTheme('help-about'),
                              _('A&bout'), self)
        QtCore.QObject.connect(about, QtCore.SIGNAL('triggered()'), self.about)

        # Menu.
        menu = self.menuBar()
        filemenu = menu.addMenu(_('&File'))

        filemenu.addAction(self.upgradea)
        filemenu.addSeparator()
        filemenu.addAction(upload)
        filemenu.addAction(search)
        filemenu.addSeparator()
        filemenu.addAction(prefs)
        filemenu.addAction(quit)

        accountmenu = menu.addMenu(_('&Account'))
        accountmenu.addAction(self.loga)
        accountmenu.addAction(self.mypkgs)
        accountmenu.addAction(self.accedita)

        helpmenu = menu.addMenu(_('&Help'))
        helpmenu.addAction(ohelp)
        helpmenu.addAction(about)

        # Toolbar.
        self.toolbar = self.addToolBar(_('aurqt Toolbar'))

        self.toolbar.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.toolbar.addAction(self.upgradea)
        self.toolbar.addSeparator()
        self.toolbar.addAction(upload)
        self.toolbar.addAction(search)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.loga)
        self.toolbar.addAction(self.accedita)
        self.toolbar.addSeparator()
        self.toolbar.addAction(quit)

        # MDI.
        self.mdiArea = QtGui.QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.windowMapper.mapped[QtGui.QWidget].connect(self.mdiArea.setActiveSubWindow)


        # Statusbar.
        self.statusBar().showMessage('aurqt v{} — Copyright © 2012, '
                                     'Kwpolska.'.format(__version__))

        # Almost done...
        self.resize(800, 600)
        self.setWindowTitle('aurqt')
        self.setWindowIcon(QtGui.QIcon.fromTheme('go-home'))  # TODO.  When we
                                                              # have one.
        threading.Thread(target=self.upgradeagenerate).start()
        threading.Thread(target=DS.continue_session).start()
        threading.Thread(target=self.sessiongenerate).start()
        self.show()
        DS.log.info('Main window ready!')

    def upload(self, *args):
        DS.log.info('upload')
        DS.log.info(args)

    def openpkg(self, pkgname):
        """Show info about a package."""
        p = InfoBox(self, pkgname=pkgname)
        p.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window = self.mdiArea.addSubWindow(p)
        p.show() #this, search and upgrade was exec — TODO

    def search(self):
        """Open search dialog."""
        s = SearchDialog(o=self.openpkg)
        window = self.mdiArea.addSubWindow(s)
        s.show()

    def prefs(self, *args):
        """Show the preferences dialog."""
        p = PreferencesDialog(self)
        p.exec_()

    def upgrade(self):
        """Upgrade installed packages."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        u = UpgradeDialog()
        window = self.mdiArea.addSubWindow(u)
        u.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        u.show()
        threading.Thread(target=self.upgradeagenerate).start()

    def log(self):
        """Log in or out."""
        if DS.sid:
            try:
                DS.logout()
                QtGui.QMessageBox.information(self, 'aurqt', _('Logged out.'))
            except AQError as e:
                QtGui.QMessageBox.critical(self, 'aurqt', e.msg,
                                           QtGui.QMessageBox.Ok)
            self.logagenerate()
        else:
            l = LoginForm()
            l.exec_()
            self.logagenerate()

    def accedit(self):
        """Show the account modification/registration form."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        e = AccountDialog(self)
        e.exec_()

    def mine(self):
        """Open search dialog with the users’ packages."""
        s = SearchDialog(o=self.openpkg, q=DS.username, m=True, a=True)
        s.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window = self.mdiArea.addSubWindow(s)
        s.exec_()

    def halp(self):
        """View the help (online)."""
        # import webbrowser fails miserably.
        subprocess.call(['xdg-open', 'http://aurqt.rtfd.org'])

    def about(self):
        """Show the about dialog."""
        a = AboutDialog(self)
        a.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        a.exec_()



def main():
    """The main routine for the UI."""
    app = QtGui.QApplication(sys.argv)
    main = Main()
    return app.exec_()
