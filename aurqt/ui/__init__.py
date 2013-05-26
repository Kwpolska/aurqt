#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.1
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui
    ~~~~~~~~

    The UI for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import DS, __version__, AQError
DS.log.info('*** Loading...')
DS.log.info(' 1/13 PyQt4')
from PyQt4 import Qt, QtGui, QtCore
DS.log.info(' 2/13 resources and translations')
from .resources import qInitResources
qInitResources()
tr = lambda x: QtCore.QCoreApplication.translate(
    '@default', x, None, QtGui.QApplication.UnicodeUTF8)
DS.log.info(' 3/13 about')
from .about import AboutDialog
DS.log.info(' 4/13 account')
from .account import AccountDialog
DS.log.info(' 5/13 info')
from .info import InfoBox
DS.log.info(' 6/13 login')
from .login import LoginForm
DS.log.info(' 7/13 preferences')
from .preferences import PreferencesDialog
DS.log.info(' 8/13 request')
from .request import RequestDialog
DS.log.info(' 9/13 search')
from .search import SearchDialog
DS.log.info('10/13 upgrade')
from .upgrade import UpgradeDialog
DS.log.info('11/13 upload')
from .upload import UploadDialog
DS.log.info('12/13 external deps')
import sys
import subprocess
import threading
import time
import pickle
import requests
DS.log.info('13/13 pkgbuilder sub-modules')
import pkgbuilder.upgrade
import pkgbuilder.exceptions
DS.log.info('*** Importing done')


class Main(QtGui.QMainWindow):
    """The main window."""
    def logagenerate(self):
        """Generate the appropriate login/logout button."""
        if DS.sid:
            # TRANSLATORS: {} = username
            self.loga.setText(tr('&Log out [{}]').format(DS.username))
            self.loga.setToolTip(tr('Log out.'))
            self.accedita.setText(tr('Account se&ttings'))
            self.accedita.setToolTip(tr('Modify the settings of this '
                                       'account.'))
            self.accedita.setIcon(QtGui.QIcon.fromTheme(
                                  'user-group-properties'))
            self.loga.setEnabled(True)
            self.accedita.setEnabled(True)
            self.mypkgs.setEnabled(True)
            self.uploada.setEnabled(True)
        else:
            self.loga.setText(tr('&Log in'))
            self.loga.setToolTip(('Log in.'))
            self.accedita.setText(tr('Regis&ter'))
            self.accedita.setToolTip(tr('Register a new account.'))
            self.accedita.setIcon(QtGui.QIcon.fromTheme('user-group-new'))
            self.loga.setEnabled(True)
            self.accedita.setEnabled(True)
            self.mypkgs.setEnabled(False)
            self.uploada.setEnabled(False)

    def upgradeagenerate(self):
        """Generate the appropriate upgrade button."""
        DS.log.info('Checking AUR upgrades...')
        ulist = pkgbuilder.upgrade.list_upgradable(
            pkgbuilder.upgrade.gather_foreign_pkgs())[0]

        self.upgradea.setText(str(len(ulist)))
        if ulist:
            self.upgradea.setToolTip(tr('Upgrade installed packages.  '
                                       '({} upgrades available)').format(
                                     len(ulist)))
        else:
            self.upgradea.setToolTip(tr('Upgrade installed packages.').format(
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

    def __init__(self, app):
        """Initialize the window."""
        DS.log.info('Starting main window init...')
        super(Main, self).__init__()

        self.app = app

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
                                      '…', self, shortcut='Ctrl+U',
                                      toolTip=tr('Fetching upgrades list…'),
                                      enabled=False, triggered=self.upgrade)

        upgrefresh = QtGui.QAction(QtGui.QIcon.fromTheme('view-refresh'),
                                   '', self, shortcut='Ctrl+Shift+R',
                                   toolTip=tr('Refresh the upgrade counter.'),
                                   enabled=True,
                                   triggered=self.upgraderefresh)

        self.uploada = QtGui.QAction(QtGui.QIcon.fromTheme('list-add'),
                                     tr('Upl&oad…'), self,
                                     shortcut='Ctrl+Shift+A',
                                     toolTip=tr('Upload a package to the '
                                     'AUR.'), enabled=False,
                                     triggered=self.upload)

        search = QtGui.QAction(QtGui.QIcon.fromTheme('edit-find'),
                               tr('&Search…'), self, shortcut='Ctrl+F',
                               toolTip=tr('Search the AUR.'),
                               triggered=self.search)

        prefs = QtGui.QAction(QtGui.QIcon.fromTheme('configure'),
                              tr('&Preferences'), self, shortcut='Ctrl+,',
                              toolTip=tr('Open the Preferences window.'),
                              triggered=self.prefs)

        quit = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'),
                             tr('&Quit'), self, shortcut='Ctrl+Q',
                             toolTip=tr('Quit aurqt'),
                             triggered=QtGui.qApp.quit)

        try:
            with open(DS.sessionfile, 'rb') as fh:
                loganame = tr('&Log out [{}]').format(pickle.load(fh)[1])
        except IOError:
            loganame = tr('&Log in')

        self.loga = QtGui.QAction(QtGui.QIcon.fromTheme('user-identity'),
                                  loganame, self, shortcut='CTRL+L',
                                  toolTip=tr('Working on authentication…'),
                                  enabled=False, triggered=self.log)

        self.mypkgs = QtGui.QAction(QtGui.QIcon.fromTheme('folder-tar'),
                                    tr('&My packages'), self,
                                    shortcut='Ctrl+M',
                                    toolTip=tr('Display packages maintained'
                                              'by the current user'),
                                    triggered=self.mine)

        self.accedita = QtGui.QAction(QtGui.QIcon.fromTheme(
                                      'user-group-properties'),
                                      tr('Account se&ttings'), self,
                                      shortcut='Ctrl+T',
                                      toolTip=tr('Working on authentication'
                                                '…'), enabled=False,
                                      triggered=self.accedit)

        mkrequest = QtGui.QAction(QtGui.QIcon.fromTheme('internet-mail'),
                                  tr('Request &Generator'), self,
                                  shortcut=('Ctrl+G'), toolTip=tr('Open the '
                                  'Mail Request Generator.'),
                                  triggered=self.request)

        ohelp = QtGui.QAction(QtGui.QIcon.fromTheme('help-contents'),
                              tr('Online &Help'), self, shortcut=('F1'),
                              toolTip=tr('Show the online help for aurqt.'),
                              triggered=self.halp)

        about = QtGui.QAction(QtGui.QIcon.fromTheme('help-about'),
                              tr('A&bout'), self, triggered=self.about)

        self.cls = QtGui.QAction(tr('Cl&ose'), self,
                                 toolTip=tr('Close the active window'),
                                 triggered=self.mdiA.closeActiveSubWindow)

        self.mmin = QtGui.QAction(tr('&Minimize'), self,
                                  toolTip=tr('Minimize the active window'),
                                  shortcut='Ctrl+Shift+M', checkable=True,
                                  triggered=self.mdiminimize)

        self.clsa = QtGui.QAction(tr('Close &All'), self,
                                  toolTip=tr('Close all the windows'),
                                  triggered=self.mdiA.closeAllSubWindows)

        self.tile = QtGui.QAction(tr('&Tile'), self,
                                  toolTip=tr('Tile the windows'),
                                  triggered=self.mdiA.tileSubWindows)

        self.csc = QtGui.QAction(tr('&Cascade'), self,
                                 toolTip=tr('Cascade the windows'),
                                 triggered=self.mdiA.cascadeSubWindows)

        self.nxtw = QtGui.QAction(tr('Ne&xt'), self,
                                  shortcut=QtGui.QKeySequence.NextChild,
                                  toolTip=tr('Move the focus to the next '
                                  'window'),
                                  triggered=self.mdiA.activateNextSubWindow)

        self.pw = QtGui.QAction(tr('Pre&vious'), self,
                                shortcut=QtGui.QKeySequence.PreviousChild,
                                toolTip=tr('Move the focus to the previous '
                                'window'),
                                triggered=self.mdiA.activatePreviousSubWindow)

        # Menu.
        menu = self.menuBar()
        filemenu = menu.addMenu(tr('&File'))

        filemenu.addAction(self.upgradea)
        filemenu.addAction(upgrefresh)
        filemenu.addSeparator()
        filemenu.addAction(self.uploada)
        filemenu.addAction(search)
        filemenu.addAction(mkrequest)
        filemenu.addSeparator()
        filemenu.addAction(prefs)
        filemenu.addAction(quit)

        accountmenu = menu.addMenu(tr('&Account'))
        accountmenu.addAction(self.loga)
        accountmenu.addAction(self.mypkgs)
        accountmenu.addAction(self.accedita)

        self.windowmenu = menu.addMenu(tr('&Window'))
        self.update_window_menu()
        QtCore.QObject.connect(self.windowmenu,
                               QtCore.SIGNAL('aboutToShow()'),
                               self.update_window_menu)

        helpmenu = menu.addMenu(tr('&Help'))
        helpmenu.addAction(ohelp)
        helpmenu.addAction(about)

        # Toolbars.
        self.statustbar = self.addToolBar(tr('Status'))
        self.statustbar.setIconSize(QtCore.QSize(22, 22))
        self.statustbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.statustbar.addAction(self.upgradea)
        self.statustbar.addAction(upgrefresh)

        self.atoolbar = self.addToolBar('Actions')
        self.atoolbar.setIconSize(QtCore.QSize(22, 22))
        self.atoolbar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.atoolbar.addAction(self.uploada)
        self.atoolbar.addAction(search)
        self.atoolbar.addAction(mkrequest)
        self.utoolbar = self.addToolBar(tr('Accounts'))
        self.utoolbar.setIconSize(QtCore.QSize(22, 22))
        self.utoolbar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.utoolbar.addAction(self.loga)
        self.utoolbar.addAction(self.accedita)
        self.utoolbar.addSeparator()
        self.mtoolbar = self.addToolBar(tr('Meta'))
        self.mtoolbar.setIconSize(QtCore.QSize(22, 22))
        self.mtoolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.mtoolbar.addAction(prefs)
        self.mtoolbar.addAction(quit)

        # Almost done...
        self.resize(950, 800)
        self.setWindowTitle('aurqt')
        self.setWindowIcon(QtGui.QIcon.fromTheme('aurqt'))
        threading.Thread(target=self.upgradeagenerate).start()
        threading.Thread(target=DS.continue_session).start()
        threading.Thread(target=self.sessiongenerate).start()

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()
        try:
            requests.get('https://aur.archlinux.org')
        except pkgbuilder.exceptions.NetworkError:
            QtGui.QMessageBox.critical(self, 'aurqt', tr('Can’t connect '
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
        try:
            lang = DS.config['i18n']['language']
        except KeyError:
            lang = 'system'

        p = PreferencesDialog(self)
        p.exec_()

        if lang != DS.config['i18n']['language']:
            p = QtGui.QMessageBox.information(self, tr('aurqt locale changed'),
                                              tr('Restart aurqt in order to '
                                                 'use the new language.'),
                                              QtGui.QMessageBox.Ok)

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
                pb = Qt.QProgressDialog()
                pb.setLabelText(tr('Logging out…'))
                pb.setMaximum(0)
                pb.setValue(-1)
                pb.setWindowModality(QtCore.Qt.WindowModal)
                pb.show()
                _tt = threading.Thread(target=DS.logout)
                _tt.start()
                while _tt.is_alive():
                    Qt.QCoreApplication.processEvents()
                pb.close()
                DS.logout()
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
    if '-h' in sys.argv or '--help' in sys.argv:
        print('aurqt v{0}'.format(__version__))
        print()
        print(tr('This is a GUI application.  There are no command-line '
                 'arguments you can pass.'))
        print(tr('For more information about using aurqt, please visit '
                 '{url}.').format('http://pkgbuilder.rtfd.org'))
        sys.exit(0)
    app = QtGui.QApplication(sys.argv)
    load_locale(app)
    main = Main(app)
    main  # because vim python-mode doesn’t like NOQA
    return app.exec_()


def load_translator(translation):
    """Load a translator."""
    trans = QtCore.QTranslator(None)
    loaded = trans.load(translation, ':/locale/')
    if loaded:
        return trans

    if not translation.startswith('en'):
        DS.log.warning('Could not load translation {0}'.format(translation))

    return None

# The eric5 guys think a translator must not be deleted.  I believe listening
# to them is a good idea.
loaded_translators = {}

def load_locale(app):
    """Load the locale."""
    loc = DS.config['i18n']['language']
    if loc == "system":
        loc = QtCore.QLocale.system().name()

    if loc != "C":
        translator = load_translator(loc)
        loaded_translators[loc] = translator
        if translator is not None:
            app.installTranslator(translator)
        else:
            loc = 'C'
    else:
        loc = None
    DS.log.info('Locale set to {0}'.format(loc))
    return loc
