#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.999
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

from .. import DS, _, AQError
DS.log.info('*** Loading...')
DS.log.info(' 1/12 PyQt4')
from PyQt4 import QtGui, QtCore
DS.log.info(' 2/12 about')
from .about import AboutDialog
DS.log.info(' 3/12 account')
from .account import AccountDialog
DS.log.info(' 4/12 info')
from .info import InfoBox
DS.log.info(' 5/12 login')
from .login import LoginForm
DS.log.info(' 6/12 preferences')
from .preferences import PreferencesDialog
DS.log.info(' 7/12 request')
from .request import RequestDialog
DS.log.info(' 8/12 search')
from .search import SearchDialog
DS.log.info(' 9/12 upgrade')
from .upgrade import UpgradeDialog
DS.log.info('10/12 upload')
from .upload import UploadDialog
DS.log.info('11/12 external deps')
import sys
import subprocess
import threading
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle
import requests
DS.log.info('12/12 pkgbuilder.upgrade')
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
            self.uploada.setEnabled(True)
        else:
            self.loga.setText(_('&Log in'))
            self.loga.setToolTip(('Log in.'))
            self.accedita.setText(_('Regis&ter'))
            self.accedita.setToolTip(_('Register a new account.'))
            self.accedita.setIcon(QtGui.QIcon.fromTheme('user-group-new'))
            self.loga.setEnabled(True)
            self.accedita.setEnabled(True)
            self.mypkgs.setEnabled(False)
            self.uploada.setEnabled(False)

    def upgradeagenerate(self):
        """Generate the appropriate upgrade button."""
        DS.log.info('Checking AUR upgrades...')
        u = pkgbuilder.upgrade.Upgrade()
        ulist = u.list_upgradable(u.gather_foreign_pkgs())[0]

        if ulist:
            self.upgradea.setText(_('&Upgrade ({})').format(len(ulist)))
            self.upgradea.setToolTip(_('Upgrade installed packages.  '
                                       '({} upgrades available)').format(
                                     len(ulist)))
        else:
            self.upgradea.setText(_('&Upgrade').format(len(ulist)))
            self.upgradea.setToolTip(_('Upgrade installed packages.').format(
                                     len(ulist)))

        self.upgradea.setEnabled(True)
        DS.log.info('AUR upgrades check done; {} found'.format(len(ulist)))

    def upgraderefresh(self):
        """self.upgradeagenerate(), human-friendly mode."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        self.upgradeagenerate()
        QtGui.QApplication.restoreOverrideCursor()

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

        # MDI.
        self.mdiA = QtGui.QMdiArea(self)
        self.mdiA.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiA.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiA)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.windowMapper.mapped[QtGui.QWidget].connect(
            self.mdiA.setActiveSubWindow)

        # Actions.
        self.upgradea = QtGui.QAction(QtGui.QIcon.fromTheme(
                                      'system-software-update'),
                                      _('&Upgrade (…)'), self,
                                      shortcut='Ctrl+U',
                                      toolTip=_('Fetching upgrades list…'),
                                      enabled=False, triggered=self.upgrade)

        upgrefresh = QtGui.QAction(QtGui.QIcon.fromTheme('view-refresh'),
                                   _('&Refresh upgrades'),
                                   self, shortcut='Ctrl+Shift+R',
                                   toolTip=_('Refresh the upgrade counter.'),
                                   enabled=True,
                                   triggered=self.upgraderefresh)

        self.uploada = QtGui.QAction(QtGui.QIcon.fromTheme('list-add'),
                                     _('Upl&oad…'), self,
                                     shortcut='Ctrl+Shift+A',
                                     toolTip=_('Upload a package to the '
                                     'AUR.'), enabled=False,
                                     triggered=self.upload)

        search = QtGui.QAction(QtGui.QIcon.fromTheme('edit-find'),
                               _('&Search…'), self, shortcut='Ctrl+F',
                               toolTip=_('Search the AUR.'),
                               triggered=self.search)

        prefs = QtGui.QAction(QtGui.QIcon.fromTheme('configure'),
                              _('&Preferences'), self, shortcut='Ctrl+,',
                              toolTip=_('Open the Preferences window.'),
                              triggered=self.prefs)

        quit = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'),
                             _('&Quit'), self, shortcut='Ctrl+Q',
                             toolTip=_('Quit aurqt'),
                             triggered=QtGui.qApp.quit)

        try:
            with open(DS.sidfile, 'rb') as fh:
                loganame = _('&Log out [{}]').format(pickle.load(fh)[1])
        except IOError:
            loganame = _('&Log in')

        self.loga = QtGui.QAction(QtGui.QIcon.fromTheme('user-identity'),
                                  loganame, self, shortcut='CTRL+L',
                                  toolTip=_('Working on authentication…'),
                                  enabled=False, triggered=self.log)

        self.mypkgs = QtGui.QAction(QtGui.QIcon.fromTheme('folder-tar'),
                                    _('&My packages'), self,
                                    shortcut='Ctrl+M',
                                    toolTip=_('Display packages maintained'
                                              'by the current user'),
                                    triggered=self.mine)

        self.accedita = QtGui.QAction(QtGui.QIcon.fromTheme(
                                      'user-group-properties'),
                                      _('Account se&ttings'), self,
                                      shortcut='Ctrl+T',
                                      toolTip=_('Working on authentication'
                                                '…'), enabled=False,
                                      triggered=self.accedit)

        mkrequest = QtGui.QAction(QtGui.QIcon.fromTheme('internet-mail'),
                                  _('Request &Generator'), self,
                                  shortcut=('Ctrl+G'), toolTip=_('Open the '
                                  'Mail Request Generator.'),
                                  triggered=self.request)

        ohelp = QtGui.QAction(QtGui.QIcon.fromTheme('help-contents'),
                              _('Online &Help'), self, shortcut=('F1'),
                              toolTip=_('Show the online help for aurqt.'),
                              triggered=self.halp)

        about = QtGui.QAction(QtGui.QIcon.fromTheme('help-about'),
                              _('A&bout'), self, triggered=self.about)

        self.cls = QtGui.QAction(_('Cl&ose'), self,
                                 toolTip=_('Close the active window'),
                                 triggered=self.mdiA.closeActiveSubWindow)

        self.mmin = QtGui.QAction(_('&Minimize'), self,
                                  toolTip=_('Minimize the active window'),
                                  shortcut='Ctrl+Shift+M', checkable=True,
                                  triggered=self.mdiminimize)

        self.clsa = QtGui.QAction(_('Close &All'), self,
                                  toolTip=_('Close all the windows'),
                                  triggered=self.mdiA.closeAllSubWindows)

        self.tile = QtGui.QAction(_('&Tile'), self,
                                  toolTip=_('Tile the windows'),
                                  triggered=self.mdiA.tileSubWindows)

        self.csc = QtGui.QAction(_('&Cascade'), self,
                                 toolTip=_('Cascade the windows'),
                                 triggered=self.mdiA.cascadeSubWindows)

        self.nxtw = QtGui.QAction(_('Ne&xt'), self,
                                  shortcut=QtGui.QKeySequence.NextChild,
                                  toolTip=_('Move the focus to the next'
                                  'window'),
                                  triggered=self.mdiA.activateNextSubWindow)

        self.pw = QtGui.QAction(_('Pre&vious'), self,
                                shortcut=QtGui.QKeySequence.PreviousChild,
                                toolTip=_('Move the focus to the previous '
                                'window'),
                                triggered=self.mdiA.activatePreviousSubWindow)

        # Menu.
        menu = self.menuBar()
        filemenu = menu.addMenu(_('&File'))

        filemenu.addAction(self.upgradea)
        filemenu.addAction(upgrefresh)
        filemenu.addSeparator()
        filemenu.addAction(self.uploada)
        filemenu.addAction(search)
        filemenu.addAction(mkrequest)
        filemenu.addSeparator()
        filemenu.addAction(prefs)
        filemenu.addAction(quit)

        accountmenu = menu.addMenu(_('&Account'))
        accountmenu.addAction(self.loga)
        accountmenu.addAction(self.mypkgs)
        accountmenu.addAction(self.accedita)

        self.windowmenu = menu.addMenu(_('&Window'))
        self.update_window_menu()
        QtCore.QObject.connect(self.windowmenu,
                               QtCore.SIGNAL('aboutToShow()'),
                               self.update_window_menu)

        helpmenu = menu.addMenu(_('&Help'))
        helpmenu.addAction(ohelp)
        helpmenu.addAction(about)

        # Toolbars.
        self.statustbar = self.addToolBar(_('Status'))
        self.statustbar.setIconSize(QtCore.QSize(22, 22))
        self.statustbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.statustbar.addAction(self.upgradea)
        self.statustbar.addAction(upgrefresh)

        self.toolbar = self.addToolBar('aurqt')
        self.toolbar.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.toolbar.addAction(self.uploada)
        self.toolbar.addAction(search)
        self.toolbar.addAction(mkrequest)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.loga)
        self.toolbar.addAction(self.accedita)
        self.toolbar.addSeparator()
        self.toolbar.addAction(quit)

        # Almost done...
        self.resize(950, 800)
        self.setWindowTitle('aurqt')
        self.setWindowIcon(QtGui.QIcon.fromTheme('aurqt'))
        threading.Thread(target=self.upgradeagenerate).start()
        threading.Thread(target=DS.continue_session).start()
        threading.Thread(target=self.sessiongenerate).start()

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()
        if not requests.get('https://aur.archlinux.org').ok:
            QtGui.QMessageBox.critical(self, _('aurqt'), _('Can’t connect '
                'to the AUR.  aurqt will now quit.'), QtGui.QMessageBox.Ok)
            QtGui.QApplication.quit()
            exit(1)
        DS.log.info('Main window ready!')

    @property
    def active_child(self):
        """Return the active MDI child."""
        child = self.mdiA.activeSubWindow()
        return child.widget() if child else None

    def mdiminimize(self):
       """Minimize the active MDI child."""
       c = self.active_child
       if c:
           if c.isMinimized():
               c.showNormal()
           else:
                c.showMinimized()


    def update_window_menu(self):
        """Update the Window menu."""
        self.windowmenu.clear()
        self.windowmenu.addAction(self.mmin)
        self.windowmenu.addAction(self.cls)
        self.windowmenu.addAction(self.clsa)
        self.windowmenu.addSeparator()
        self.windowmenu.addAction(self.tile)
        self.windowmenu.addAction(self.csc)
        self.windowmenu.addSeparator()
        self.windowmenu.addAction(self.nxtw)
        self.windowmenu.addAction(self.pw)
        self.windowmenu.addSeparator()

        windows = self.mdiA.subWindowList()
        if len(windows) != 0:
            self.windowmenu.addSeparator()

        for i, window in enumerate(windows):
            child = window

            text = "%d %s" % (i + 1, child.windowTitle())
            if i < 9:
                text = '&' + text

            action = self.windowmenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child.widget() is self.active_child)
            action.triggered.connect(self.windowMapper.map)
            self.mmin.setChecked(self.active_child.isMinimized())
            self.windowMapper.setMapping(action, window)

    def upload(self):
        """Show the upload dialog."""
        u = UploadDialog(self)
        u.exec_()
        del u

    def openpkg(self, pkgname, pkgobj=None):
        """Show info about a package."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        p = InfoBox(self, pkgname=pkgname, pkgobj=pkgobj,
                    r=self.request)
        p.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.mdiA.addSubWindow(p)
        p.show()

    def prefs(self):
        """Show the preferences dialog."""
        p = PreferencesDialog(self)
        p.exec_()

    def request(self, wtfisthis, pkgnames=[]):
        """Open the request generator."""
        r = RequestDialog(self, pkgnames=pkgnames)
        r.exec_()

    def search(self):
        """Open search dialog."""
        s = SearchDialog(o=self.openpkg)
        self.mdiA.addSubWindow(s)
        s.show()

    def upgrade(self):
        """Upgrade installed packages."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        u = UpgradeDialog()
        u.exec_()
        threading.Thread(target=self.upgradeagenerate).start()

    def log(self):
        """Log in or out."""
        if DS.sid:
            try:
                DS.logout()
                QtGui.QMessageBox.information(self, 'aurqt',
                                              _('Logged out.'),
                                              QtGui.QMessageBox.Ok)
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
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        e = AccountDialog(self)
        e.exec_()

    def mine(self):
        """Open search dialog with the users’ packages."""
        s = SearchDialog(o=self.openpkg, q=DS.username, m=True, a=True)
        s.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.mdiA.addSubWindow(s)
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
