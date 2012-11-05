#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.999
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.info
    ~~~~~~~~~~~~~
    The package information box for aurqt.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import AQError, DS, _, __version__
from PyQt4 import Qt, QtGui, QtCore
from pkgbuilder.utils import Utils
import pkgbuilder
import pycman

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
        self.setWindowTitle(_('Comment…'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('document-edit'))
        self.show()

    def add(self):
        """Add a comment."""
        self.text = self.textbox.toPlainText()
        self.accept()

class InfoBox(QtGui.QDialog):
    """The package information box for aurqt."""
    def __init__(self, parent=None, pkgname=None, pkgobj=None, r=None):
        """Initialize the box."""
        if not pkgname:
            raise AQError('info', 'pkgnameNotPresent', '`pkgname` not present')
        if not pkgname:
            raise AQError('info', 'rNotPresent', '`r` not present')
        super(InfoBox, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                        QtGui.QSizePolicy.Fixed)
        if pkgobj:
            self.pkg = pkgobj
        else:
            self.pkg = Utils().info([pkgname])[0]

        self.awpkg = DS.w.fetchpkg(self.pkg['ID'])

        infostring = self.pkg['Name'] + ' ' + self.pkg['Version']

        topbar = QtGui.QFrame(self)
        topbar.setFrameShape(QtGui.QFrame.StyledPanel)
        topbar.setFrameShadow(QtGui.QFrame.Raised)
        topbar.setSizePolicy(size_policy)
        topbarlay = QtGui.QHBoxLayout(topbar)

        self.insta = QtGui.QAction(topbar)

        self.instb = QtGui.QToolButton(topbar)
        self.instb.setIcon(QtGui.QIcon.fromTheme('run-build-install'))
        self.instb.setText(_('Install'))
        self.instb.setIconSize(QtCore.QSize(22, 22))
        self.instb.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.instb.setDefaultAction(self.insta)

        QtCore.QObject.connect(self.insta, QtCore.SIGNAL('triggered()'),
                               self.install)

        actionb = QtGui.QToolButton(topbar)
        actionb.setIcon(QtGui.QIcon.fromTheme('system-run'))
        actionb.setIconSize(QtCore.QSize(22, 22))
        actionb.setPopupMode(QtGui.QToolButton.InstantPopup)
        actionb.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        actionb.setText(_('Actions'))
        self.actionm = QtGui.QMenu(self)
        actionb.setMenu(self.actionm)

        QtCore.QObject.connect(self.actionm, QtCore.SIGNAL('aboutToShow()'),
                               self.update_actions)

        topbarlay.addWidget(self.instb)
        topbarlay.addWidget(actionb)

        self.name = QtGui.QLabel(infostring, self)
        font = QtGui.QFont()
        font.setPointSize(20)

        self.name.setFont(font)

        self.name.setSizePolicy(size_policy)
        self.name.setAlignment(QtCore.Qt.AlignCenter)

        desc = QtGui.QLabel(self.pkg['Description'], self)
        desc.setAlignment(QtCore.Qt.AlignCenter)
        desc.setSizePolicy(size_policy)

        data = QtGui.QGroupBox(_('Data'), self)
        datalay = QtGui.QFormLayout(data)
        datalay.setHorizontalSpacing(15)
        datalay.setVerticalSpacing(7)

        datalabels = [_('Out of Date'), _('Category'), _('AUR URL'),
                      _('Project URL'), _('Maintainer'), _('Votes'),
                      _('First submitted'), _('Last updated')]

        aururl = 'https://aur.archlinux.org/packages.php?ID={}'.format(
                 self.pkg['ID'])

        fields = [None, None, '<a href="{0}">{0}</a>'.format(aururl),
                  '<a href="{0}">{0}</a>'.format(self.pkg['URL']),
                  None, None]
        self.oodbox = QtGui.QLabel('…', data)
        self.maintainer = QtGui.QLabel(self.pkg['Maintainer'], data)
        self.numvotes = QtGui.QLabel(str(self.pkg['NumVotes']), data)

        sdate = QtCore.QDateTime()
        sdate = sdate.fromTime_t(self.pkg['FirstSubmitted'])
        fields.append(sdate.toString(QtCore.Qt.SystemLocaleLongDate))

        mdate = QtCore.QDateTime()
        mdate = mdate.fromTime_t(self.pkg['LastModified'])
        fields.append(mdate.toString(QtCore.Qt.SystemLocaleLongDate))

        for i, j in enumerate(datalabels):
            datalay.setWidget(i, QtGui.QFormLayout.LabelRole,
                              QtGui.QLabel(j, data))

        for i, j in enumerate(fields):
            if j:
                datalay.setWidget(i, QtGui.QFormLayout.FieldRole,
                                  QtGui.QLabel(j, data))

        c = self.pkg['CategoryID']
        if DS.username == self.pkg['Maintainer']:
            self.catbox = QtGui.QComboBox(data, frame=False)
            for i in pkgbuilder.DS.categories[1:]:
                self.catbox.addItem(i)

            self.catbox.setCurrentIndex(c - 1)

            datalay.setWidget(1, QtGui.QFormLayout.FieldRole, self.catbox)

            QtCore.QObject.connect(self.catbox,
                                   QtCore.SIGNAL('currentIndexChanged(int)'),
                                   self.changecat)
        else:
            datalay.setWidget(1, QtGui.QFormLayout.FieldRole,
                              QtGui.QLabel(pkgbuilder.DS.categories[c], data))

        datalay.setWidget(0, QtGui.QFormLayout.FieldRole, self.oodbox)
        datalay.setWidget(4, QtGui.QFormLayout.FieldRole, self.maintainer)
        datalay.setWidget(5, QtGui.QFormLayout.FieldRole, self.numvotes)

        self.cgroup = QtGui.QGroupBox(_('Comments'), self)
        clay = QtGui.QVBoxLayout(self.cgroup)
        cadd = QtGui.QPushButton(_('Add a comment…'), self,
                                 icon=QtGui.QIcon.fromTheme('document-edit'))
        QtCore.QObject.connect(cadd, QtCore.SIGNAL('pressed()'), self.comment)
        self.comments = QtGui.QTextBrowser(self.cgroup)

        self.comments.setText("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
.aq {}color: #888; text-align: right;{}
</style>
</head>
<body>
<p>{}</p>
<p class="aq">aurqt v{}</p>
</body>
</html>""".format('{', '}', _('Loading…'), __version__))

        clay.addWidget(cadd)
        clay.addWidget(self.comments)

        lay.addWidget(topbar)
        lay.addWidget(self.name)
        lay.addWidget(desc)
        lay.addWidget(data)
        lay.addWidget(self.cgroup)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.reloadview()
        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowTitle(infostring)
        self.setWindowIcon(QtGui.QIcon.fromTheme('dialog-information'))
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
        self.pkg = Utils().info([self.pkg['Name']])[0]
        QtGui.QApplication.restoreOverrideCursor()

    def vote(self):
        """{Up,Down}vote the package."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        if self.voted:
            self.awpkg = DS.w.pkgaction(self.pkg, '-vote')
        else:
            self.awpkg = DS.w.pkgaction(self.pkg, '+vote')
        self.pkg = Utils().info([self.pkg['Name']])[0]
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
        if self.pkg['OutOfDate'] > 0:
            self.awpkg = DS.w.pkgaction(self.pkg, '-flag')
        else:
            self.awpkg = DS.w.pkgaction(self.pkg, '+flag')
        self.pkg = Utils().info([self.pkg['Name']])[0]
        QtGui.QApplication.restoreOverrideCursor()
        self.reloadview()

    def own(self):
        """Adopt/disown the package."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        if self.pkg['Maintainer'] == DS.username:
            self.awpkg = DS.w.pkgaction(self.pkg, '-own')
        elif self.pkg['Maintainer'] == None:
            self.awpkg = DS.w.pkgaction(self.pkg, '+own')
        else:
            DS.log.error('Tried to own() on a package that isn’t '
                         'yours/nobodys.')
        self.pkg = Utils().info([self.pkg['Name']])[0]
        QtGui.QApplication.restoreOverrideCursor()
        self.reloadview()

    def install(self):
        """{Uni,I}nstall a package."""
        pyc = pycman.config.init_with_config('/etc/pacman.conf')
        localdb = pyc.get_localdb()
        pkg = localdb.get_pkg(self.pkg['Name'])

        if pkg:
            DS.pacman(['-S', self.pkg['Name']])
        else:
            DS.pkginst([self.pkg['Name']])

    def makerequest(self):
        """Make a request."""
        r([self.pkg['Name']])

    def reloaddata(self):
        """Reload the data."""
        self.pkg = Utils().info([self.pkg['Name']])[0]
        self.awpkg = DS.w.fetchpkg(self.pkg['ID'])

    def update_actions(self):
        self.actionm.clear()
        vote = QtGui.QAction(QtGui.QIcon.fromTheme('task-complete'),
                             _('&Vote'), self, toolTip=_('Vote for this '
                             'package'), shortcut='Ctrl+Shift+V',
                             checkable=True, triggered=self.vote)
        notify = QtGui.QAction(QtGui.QIcon.fromTheme('preferences-desktop-'
                               'notification'), _('&Notify'), self,
                               toolTip=_('Enable comment notifications for '
                               'this package'), shortcut='Ctrl+Shift+N',
                               checkable=True, triggered=self.notify)
        flag = QtGui.QAction(QtGui.QIcon.fromTheme('flag-red'),
                             _('&Flag as outdated'), self,
                             toolTip=_('Flag the package as outdated.'),
                             shortcut='Ctrl+Shift+F',
                             checkable=True, triggered=self.flag)
        comment = QtGui.QAction(QtGui.QIcon.fromTheme('document-edit'),
                                _('&Comment…'), self, toolTip=_('Add a '
                                'comment for this package'),
                                shortcut='Ctrl+Shift+C',
                                triggered=self.comment)

        comment = QtGui.QAction(QtGui.QIcon.fromTheme('document-edit'),
                                _('Make a &request…'), self,
                                toolTip=_('Request an action on this'
                                'package (remove, merge, orphan).'),
                                shortcut='Ctrl+Shift+C',
                                triggered=self.comment)
        if self.voted:
            vote.setChecked(2)

        if self.notified:
            notify.setChecked(2)

        if self.pkg['OutOfDate'] > 0:
            flag.setChecked(2)

        if self.pkg['Maintainer']:
            own = QtGui.QAction(QtGui.QIcon.fromTheme('list-remove-user'),
                                _('&Disown'), self, toolTip=_('Disown this '
                                'package'), shortcut='Ctrl+Shift+O',
                                triggered=self.own)
        else:
            own = QtGui.QAction(QtGui.QIcon.fromTheme('list-add-user'),
                                _('&Adopt'), self, toolTip=_('Adopt this '
                                'package'), shortcut='Ctrl+Shift+O',
                                triggered=self.own)

        if self.pkg['Maintainer'] != DS.username and self.pkg['OutOfDate']:
            flag.setEnabled(False)
            flag.setToolTip(_('Only the maintainer can unflag a package.'))

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
        elif self.pkg['Maintainer'] not in (DS.username, None):
            own.setEnabled(False)

    def reloadview(self):
        """Reload the view."""
        if self.pkg['OutOfDate'] > 0:
            self.name.setStyleSheet('color: #f00;')
            self.oodbox.setStyleSheet('color: #f00;')
        else:
            self.name.setStyleSheet('')
            self.oodbox.setStyleSheet('')

        self.voted = 'unvote/">' in self.awpkg.prettify()
        self.notified = 'unnotify/">' in self.awpkg.prettify()

        if self.pkg['OutOfDate'] > 0:
            sdate = QtCore.QDateTime()
            sdate = sdate.fromTime_t(self.pkg['OutOfDate'])
            self.oodbox.setText(_('yes, since {}').format(
                sdate.toString(QtCore.Qt.SystemLocaleLongDate)))
        else:
            self.oodbox.setText(_('no'))

        if self.pkg['Maintainer']:
            self.maintainer.setText(self.pkg['Maintainer'])
        else:
            self.maintainer.setText('none')

        self.numvotes.setText(str(self.pkg['NumVotes']))

        c = DS.w.fetchcomments(self.awpkg)

        if c:
            self.comments.setText(c.prettify())
        else:
            self.comments.setText("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
.aq {}color: #888; text-align: right;{}
</style>
</head>
<body>
<p>{}</p>
<p>{}</p>
<p class="aq">aurqt v{}</p>
</body>
</html>""".format('{', '}', _('There are currently no comments for this '
                  'package.'), _('In order to add one, hit the button '
                  'above.'), __version__))

        pyc = pycman.config.init_with_config('/etc/pacman.conf')
        localdb = pyc.get_localdb()
        pkg = localdb.get_pkg(self.pkg['Name'])

        if pkg:
            self.instb.setIcon(QtGui.QIcon.fromTheme('run-build-purge'))
            self.instb.setText(_('Uninstall'))
        else:
            self.instb.setIcon(QtGui.QIcon.fromTheme('run-build-install'))
            self.instb.setText(_('Install'))
