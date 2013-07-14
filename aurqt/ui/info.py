#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.2.2
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.info
    ~~~~~~~~~~~~~
    The package information box for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import tr
from .. import AQError, DS, __version__
from PyQt4 import Qt, QtGui, QtCore
from pkgbuilder import DS as PBDS
import pkgbuilder.utils
from pkgbuilder.package import CATEGORIES

class CommentDialog(QtGui.QDialog):
    """The comment dialog for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(CommentDialog, self).__init__(parent)
        lay = QtGui.QVBoxLayout(self)

        self.textbox = QtGui.QTextEdit(self)
        self.text = ''

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Save |
                               QtGui.QDialogButtonBox.Cancel)

        lay.addWidget(self.textbox)
        lay.addWidget(btn)

        QtCore.QObject.connect(btn, QtCore.SIGNAL('accepted()'), self.add)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(tr('Comment...'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('document-edit'))
        self.show()

    def add(self):
        """Add a comment."""
        self.text = self.textbox.toPlainText()
        self.accept()

class InfoBox(QtGui.QDialog):
    """The package information box for aurqt."""
    def __init__(self, parent=None, pkgname=None, pkgobj=None, r = None):
        """Initialize the box."""
        if not pkgname:
            raise AQError('info', 'pkgnameNotPresent', 'pkgname not present')
        if r:
            self.r = r
        else:
            raise AQError('info', 'rNotPresent', 'r not present')

        super(InfoBox, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                        QtGui.QSizePolicy.Fixed)
        if pkgobj:
            self.pkg = pkgobj
        else:
            self.pkg = pkgbuilder.utils.info([pkgname])[0]

        infostring = ' '.join((self.pkg.name, self.pkg.version))

        topbar = QtGui.QFrame(self)
        topbar.setFrameShape(QtGui.QFrame.StyledPanel)
        topbar.setFrameShadow(QtGui.QFrame.Raised)
        topbar.setSizePolicy(size_policy)
        topbarlay = QtGui.QHBoxLayout(topbar)

        self.insta = QtGui.QAction(topbar)
        self.upga = QtGui.QAction(topbar)

        self.instb = QtGui.QToolButton(topbar)
        self.instb.setIcon(QtGui.QIcon.fromTheme('run-build-install'))
        self.instb.setText(tr('Install'))
        self.instb.setIconSize(QtCore.QSize(22, 22))
        self.instb.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.instb.setDefaultAction(self.insta)

        self.upgb = QtGui.QToolButton(topbar)
        self.upgb.setIcon(QtGui.QIcon.fromTheme('system-software-update'))
        self.upgb.setText(tr('Update'))
        self.upgb.setIconSize(QtCore.QSize(22, 22))
        self.upgb.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.upgb.setDefaultAction(self.upga)

        QtCore.QObject.connect(self.insta, QtCore.SIGNAL('triggered()'),
                               self.install)
        QtCore.QObject.connect(self.upga, QtCore.SIGNAL('triggered()'),
                               self.upgrade)

        actionb = QtGui.QToolButton(topbar)
        actionb.setIcon(QtGui.QIcon.fromTheme('system-run'))
        actionb.setIconSize(QtCore.QSize(22, 22))
        actionb.setPopupMode(QtGui.QToolButton.InstantPopup)
        actionb.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        actionb.setText(tr('Actions'))
        self.actionm = QtGui.QMenu(self)
        actionb.setMenu(self.actionm)

        QtCore.QObject.connect(self.actionm, QtCore.SIGNAL('aboutToShow()'),
                               self.update_actions)

        topbarlay.addWidget(self.upgb)
        topbarlay.addWidget(self.instb)
        topbarlay.addWidget(actionb)

        self.name = QtGui.QLabel(infostring, self)
        font = QtGui.QFont()
        font.setPointSize(20)

        self.name.setFont(font)

        self.name.setSizePolicy(size_policy)
        self.name.setAlignment(QtCore.Qt.AlignCenter)

        desc = QtGui.QLabel(self.pkg.description, self)
        desc.setAlignment(QtCore.Qt.AlignCenter)
        desc.setSizePolicy(size_policy)

        data = QtGui.QGroupBox(tr('Data'), self)
        datalay = QtGui.QFormLayout(data)
        datalay.setHorizontalSpacing(15)
        datalay.setVerticalSpacing(7)

        datalabels = [tr('Out of Date'), tr('Category'), tr('AUR URL'),
                      tr('Project URL'), tr('Maintainer'), tr('Votes'),
                      tr('First submitted'), tr('Last updated')]

        aururl = 'https://aur.archlinux.org/packages/{0}/'.format(
                 self.pkg.name)

        fields = [None, None, '<a href="{0}">{0}</a>'.format(aururl),
                  '<a href="{0}">{0}</a>'.format(self.pkg.url),
                  None, None]
        self.oodbox = QtGui.QLabel('...', data)
        self.maintainer = QtGui.QLabel(self.pkg.human, data)
        self.numvotes = QtGui.QLabel(str(self.pkg.votes), data)

        sdate = QtCore.QDateTime()
        sdate = sdate.fromTime_t(int(self.pkg.added.timestamp()))
        fields.append(sdate.toString(QtCore.Qt.SystemLocaleLongDate))

        mdate = QtCore.QDateTime()
        mdate = sdate.fromTime_t(int(self.pkg.modified.timestamp()))
        fields.append(mdate.toString(QtCore.Qt.SystemLocaleLongDate))

        for i, j in enumerate(datalabels):
            datalay.setWidget(i, QtGui.QFormLayout.LabelRole,
                              QtGui.QLabel(j, data))

        for i, j in enumerate(fields):
            if j:
                datalay.setWidget(i, QtGui.QFormLayout.FieldRole,
                                  QtGui.QLabel(j, data))

        c = self.pkg._categoryid
        if DS.username == self.pkg.human:
            self.catbox = QtGui.QComboBox(data, frame=False)
            for i in CATEGORIES[1:]:
                self.catbox.addItem(i)

            self.catbox.setCurrentIndex(c - 1)

            datalay.setWidget(1, QtGui.QFormLayout.FieldRole, self.catbox)

            QtCore.QObject.connect(self.catbox,
                                   QtCore.SIGNAL('currentIndexChanged(int)'),
                                   self.changecat)
        else:
            datalay.setWidget(1, QtGui.QFormLayout.FieldRole,
                              QtGui.QLabel(CATEGORIES[c], data))

        datalay.setWidget(0, QtGui.QFormLayout.FieldRole, self.oodbox)
        datalay.setWidget(4, QtGui.QFormLayout.FieldRole, self.maintainer)
        datalay.setWidget(5, QtGui.QFormLayout.FieldRole, self.numvotes)

        self.cgroup = QtGui.QGroupBox(tr('Comments'), self)
        clay = QtGui.QVBoxLayout(self.cgroup)
        cadd = QtGui.QPushButton(tr('Add a comment...'), self,
                                 icon=QtGui.QIcon.fromTheme('document-edit'))
        QtCore.QObject.connect(cadd, QtCore.SIGNAL('pressed()'), self.comment)
        self.comments = QtGui.QTextBrowser(self.cgroup)

        self.comments.setText('<!DOCTYPE html>\n<html><head>'
                              '<meta charset="UTF-8"><style>'
                              '.aq {}color: #888; text-align: right;{}'
                              '</style></head><body><p>{}</p>'
                              '<p class="aq">aurqt v{}</p></body>'
                              '</html>'.format('{', '}', tr('Loading...'),
                                               __version__))

        clay.addWidget(cadd)
        clay.addWidget(self.comments)

        lay.addWidget(topbar)
        lay.addWidget(self.name)
        lay.addWidget(desc)
        lay.addWidget(data)
        lay.addWidget(self.cgroup)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowTitle(infostring)
        self.setWindowIcon(QtGui.QIcon.fromTheme('dialog-information'))
        Qt.QCoreApplication.processEvents()
        self.awpkg = DS.w.fetchpkg(self.pkg)
        self.reloadview()
        QtGui.QApplication.restoreOverrideCursor()

    def comment(self):
        """Make a comment."""
        c = CommentDialog()
        c.exec_()
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        if c.text:
            self.awpkg = DS.w.pkgaction(self.pkg, 'comment', c.text)
        QtGui.QApplication.restoreOverrideCursor()
        self.reloadview()

    def changecat(self, cat):
        """Change the category."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        cat += 1
        self.awpkg = DS.w.pkgaction(self.pkg, 'category', cat)
        self.pkg = pkgbuilder.utils.info([self.pkg.name])[0]
        QtGui.QApplication.restoreOverrideCursor()

    def vote(self):
        """{Up,Down}vote the package."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        if self.voted:
            self.awpkg = DS.w.pkgaction(self.pkg, '-vote')
        else:
            self.awpkg = DS.w.pkgaction(self.pkg, '+vote')
        self.pkg = pkgbuilder.utils.info([self.pkg.name])[0]
        QtGui.QApplication.restoreOverrideCursor()
        self.reloadview()

    def notify(self):
        """{Un,}Notify me for the package."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        if self.notified:
            self.awpkg = DS.w.pkgaction(self.pkg, '-notify')
        else:
            self.awpkg = DS.w.pkgaction(self.pkg, '+notify')
        QtGui.QApplication.restoreOverrideCursor()
        self.reloadview()

    def flag(self):
        """{Un,}flag the package."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        if self.pkg.is_outdated > 0:
            self.awpkg = DS.w.pkgaction(self.pkg, '-flag')
        else:
            self.awpkg = DS.w.pkgaction(self.pkg, '+flag')
        self.pkg = pkgbuilder.utils.info([self.pkg.name])[0]
        QtGui.QApplication.restoreOverrideCursor()
        self.reloadview()

    def own(self):
        """Adopt/disown the package."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        if self.pkg.human == DS.username:
            self.awpkg = DS.w.pkgaction(self.pkg, '-own')
        elif not self.pkg.human:
            self.awpkg = DS.w.pkgaction(self.pkg, '+own')
        else:
            DS.log.error('Tried to own() on a package that isn\'t '
                         'yours/nobodys.')
        self.pkg = pkgbuilder.utils.info([self.pkg.name])[0]
        QtGui.QApplication.restoreOverrideCursor()
        self.reloadview()

    def install(self):
        """{Uni,I}nstall a package."""
        PBDS._pycreload()
        localdb = PBDS.pyc.get_localdb()
        pkg = localdb.get_pkg(self.pkg.name)

        if pkg:
            DS.pacman(['-R', self.pkg.name])
        else:
            DS.pkginst([self.pkg.name])

    def upgrade(self):
        """Upgrade a package."""
        DS.pkginst([self.pkg.name])


    def req(self):
        """Make a request."""
        self.r(wtfisthis=None, pkgnames=[self.pkg.name])

    def reloaddata(self):
        """Reload the data."""
        self.pkg = pkgbuilder.utils.info([self.pkg.name])[0]
        self.awpkg = DS.w.fetchpkg(self.pkg)

    def update_actions(self):
        self.actionm.clear()
        vote = QtGui.QAction(QtGui.QIcon.fromTheme('task-complete'),
                             tr('&Vote'), self, toolTip=tr('Vote for this '
                             'package'), shortcut='Ctrl+Shift+V',
                             checkable=True, triggered=self.vote)
        notify = QtGui.QAction(QtGui.QIcon.fromTheme('preferences-desktop-'
                               'notification'), tr('&Notify'), self,
                               toolTip=tr('Enable comment notifications for '
                               'this package'), shortcut='Ctrl+Shift+N',
                               checkable=True, triggered=self.notify)
        flag = QtGui.QAction(QtGui.QIcon.fromTheme('flag-red'),
                             tr('&Flag as outdated'), self,
                             toolTip=tr('Flag the package as outdated.'),
                             shortcut='Ctrl+Shift+F',
                             checkable=True, triggered=self.flag)
        comment = QtGui.QAction(QtGui.QIcon.fromTheme('document-edit'),
                                tr('&Comment...'), self, toolTip=tr('Add a '
                                'comment for this package'),
                                shortcut='Ctrl+Shift+C',
                                triggered=self.comment)

        req = QtGui.QAction(QtGui.QIcon.fromTheme('internet-mail'),
                            tr('Make a &request...'), self,
                            toolTip=tr('Request an action on this '
                            'package (remove, merge, orphan).'),
                            shortcut='Ctrl+Shift+C',
                            triggered=self.req)
        if self.voted:
            vote.setChecked(2)

        if self.notified:
            notify.setChecked(2)

        if self.pkg.is_outdated:
            flag.setChecked(2)

        if self.pkg.human:
            own = QtGui.QAction(QtGui.QIcon.fromTheme('list-remove-user'),
                                tr('&Disown'), self, toolTip=tr('Disown this '
                                'package'), shortcut='Ctrl+Shift+O',
                                triggered=self.own)
        else:
            own = QtGui.QAction(QtGui.QIcon.fromTheme('list-add-user'),
                                tr('A&dopt'), self, toolTip=tr('Adopt this '
                                'package'), shortcut='Ctrl+Shift+O',
                                triggered=self.own)

        if self.pkg.human != DS.username and self.pkg.is_outdated:
            flag.setEnabled(False)
            flag.setToolTip(tr('Only the maintainer can unflag a package.'))

        self.actionm.addAction(vote)
        self.actionm.addAction(notify)
        self.actionm.addAction(flag)
        self.actionm.addAction(comment)
        self.actionm.addAction(req)
        self.actionm.addSeparator()
        self.actionm.addAction(own)
        if not DS.username:
            vote.setEnabled(False)
            notify.setEnabled(False)
            flag.setEnabled(False)
            comment.setEnabled(False)
            own.setEnabled(False)
        elif self.pkg.human not in (DS.username, None):
            own.setEnabled(False)

    def reloadview(self):
        """Reload the view."""
        if self.pkg.is_outdated:
            self.name.setStyleSheet('color: #f00;')
            self.oodbox.setStyleSheet('color: #f00;')
        else:
            self.name.setStyleSheet('')
            self.oodbox.setStyleSheet('')

        self.voted = 'unvote/">' in self.awpkg.prettify()
        self.notified = 'unnotify/">' in self.awpkg.prettify()

        if self.pkg.is_outdated:
            sdate = QtCore.QDateTime()
            sdate = sdate.fromTime_t(self.pkg.outdated_since.timestamp())
            self.oodbox.setText(tr('yes, since {}').format(
                sdate.toString(QtCore.Qt.SystemLocaleLongDate)))
        else:
            self.oodbox.setText(tr('no'))

        if self.pkg.human:
            self.maintainer.setText(self.pkg.human)
        else:
            self.maintainer.setText('none')

        self.numvotes.setText(str(self.pkg.votes))

        c = DS.w.fetchcomments(self.awpkg)

        if c:
            self.comments.setText(c.prettify())
        else:
            self.comments.setText('<!DOCTYPE html>\n<html><head>'
                                  '<meta charset="UTF-8"><style>'
                                  '.aq {}color: #888; text-align: right;{}'
                                  '</style></head><body><p>{}</p><p>{}</p>'
                                  '<p class="aq">aurqt v{}</p></body>'
                                  '</html>'.format(
                                      '{', '}',
                                      tr('There are currently no comments for '
                                         'this package.'),
                                      tr('In order to add one, hit the button '
                                         'above.'), __version__))

        PBDS._pycreload()
        localdb = PBDS.pyc.get_localdb()
        pkg = localdb.get_pkg(self.pkg.name)

        if pkg:
            self.instb.setIcon(QtGui.QIcon.fromTheme('run-build-prune'))
            self.instb.setText(tr('Uninstall'))
            if pkg.version == self.pkg.version:
                self.upgb.setIcon(QtGui.QIcon.fromTheme('run-build-install'))
                self.upgb.setText(tr('Reinstall'))
            else:
                self.upgb.setIcon(QtGui.QIcon.fromTheme('system-software-update'))
                self.upgb.setText(tr('Upgrade'))
            self.upgb.setEnabled(True)
        else:
            self.instb.setIcon(QtGui.QIcon.fromTheme('run-build-install'))
            self.instb.setText(tr('Install'))
            self.upgb.setIcon(QtGui.QIcon.fromTheme('system-software-update'))
            self.upgb.setText(tr('Upgrade'))
            self.upgb.setEnabled(False)
