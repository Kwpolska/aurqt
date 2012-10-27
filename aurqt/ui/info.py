#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
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


class CThread(QtCore.QThread):
    """The Comment retrieval thread.."""
    def __init__(self):
        """Initializing the thread."""
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        pkg = self.fetchpkg()
        self.emit(QtCore.SIGNAL('update(QString)'), pkg)
        return


class CommentDialog(QtGui.QDialog):
    """The comment dialog for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(CommentDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        self.box = QtGui.QTextEdit(self)

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Save |
                               QtGui.QDialogButtonBox.Cancel)

        lay.addWidget(self.box)
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
        print('cannot.')
        self.accept()


class InfoBox(QtGui.QDialog):
    """The package information box for aurqt."""
    def __init__(self, parent=None, pkgname=None, pkgobj=None):
        """Initialize the box."""
        if not pkgname:
            raise AQError('info', 'pkgnameNotPresent', '`pkgname` not present')
        super(InfoBox, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                        QtGui.QSizePolicy.Fixed)
        if pkgobj:
            self.pkg = pkgobj
        else:
            self.pkg = Utils().info([pkgname])[0]
        self.fetchpkg(self.pkg['ID'])
        infostring = self.pkg['Name'] + ' ' + self.pkg['Version']

        topbar = QtGui.QFrame(self)
        topbar.setFrameShape(QtGui.QFrame.StyledPanel)
        topbar.setFrameShadow(QtGui.QFrame.Raised)
        topbar.setSizePolicy(size_policy)
        topbarlay = QtGui.QHBoxLayout(topbar)

        self.insta = QtGui.QToolButton(topbar)
        self.insta.setIcon(QtGui.QIcon.fromTheme('run-build-install'))
        self.insta.setIconSize(QtCore.QSize(22, 22))
        self.insta.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.insta.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.insta.setText(_('Install'))

        actionb = QtGui.QToolButton(topbar)
        actionb.setIcon(QtGui.QIcon.fromTheme('system-run'))
        actionb.setIconSize(QtCore.QSize(22, 22))
        actionb.setPopupMode(QtGui.QToolButton.MenuButtonPopup)  # TODO menus
        actionb.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        actionb.setText(_('Actions'))

        topbarlay.addWidget(self.insta)
        topbarlay.addWidget(actionb)

        name = QtGui.QLabel(infostring, self)
        font = QtGui.QFont()
        font.setPointSize(20)

        name.setFont(font)
        if self.pkg['OutOfDate'] == '1':
            name.setStyleSheet('color: #f00;')

        name.setSizePolicy(size_policy)
        name.setAlignment(QtCore.Qt.AlignCenter)

        desc = QtGui.QLabel(self.pkg['Description'], self)
        desc.setAlignment(QtCore.Qt.AlignCenter)
        desc.setSizePolicy(size_policy)

        data = QtGui.QGroupBox(_('Data'), self)
        datalay = QtGui.QFormLayout(data)
        datalay.setHorizontalSpacing(15)
        datalay.setVerticalSpacing(7)

        datalabels = [_('Category'), _('AUR URL'), _('Project URL'),
                      _('Maintainer'), _('Votes'),
                      _('First submitted'), _('Last updated')]

        aururl = 'https://aur.archlinux.org/packages.php?ID={}'.format(
                 self.pkg['ID'])

        fields = [None, '<a href="{0}">{0}</a>'.format(aururl),
                  '<a href="{0}">{0}</a>'.format(self.pkg['URL']),
                  self.pkg['Maintainer'], self.pkg['NumVotes']]

        sdate = QtCore.QDateTime()
        sdate = sdate.fromTime_t(int(self.pkg['FirstSubmitted']))
        fields.append(sdate.toString(QtCore.Qt.SystemLocaleLongDate))

        mdate = QtCore.QDateTime()
        mdate = mdate.fromTime_t(int(self.pkg['LastModified']))
        fields.append(mdate.toString(QtCore.Qt.SystemLocaleLongDate))

        for i, j in enumerate(datalabels):
            datalay.setWidget(i, QtGui.QFormLayout.LabelRole,
                              QtGui.QLabel(j, data))

        for i, j in enumerate(fields):
            if j:
                datalay.setWidget(i, QtGui.QFormLayout.FieldRole,
                                  QtGui.QLabel(j, data))

        c = int(self.pkg['CategoryID'])
        if DS.username == self.pkg['Maintainer']:
            self.catbox = QtGui.QComboBox(data, frame=False)
            for i in pkgbuilder.DS.categories[1:]:
                self.catbox.addItem(i)

            self.catbox.setCurrentIndex(c - 1)

            datalay.setWidget(0, QtGui.QFormLayout.FieldRole, self.catbox)

            QtCore.QObject.connect(self.catbox,
                                   QtCore.SIGNAL('currentIndexChanged(int)'),
                                   self.changecat)
        else:
            datalay.setWidget(0, QtGui.QFormLayout.FieldRole,
                              QtGui.QLabel(pkgbuilder.DS.categories[c], data))

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
        lay.addWidget(name)
        lay.addWidget(desc)
        lay.addWidget(data)
        lay.addWidget(self.cgroup)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.getcomments()
        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowTitle(infostring)
        self.setWindowIcon(QtGui.QIcon.fromTheme('dialog-information'))
        QtGui.QApplication.restoreOverrideCursor()

    def comment(self):
        """Make a comment."""
        c = CommentDialog()
        c.exec_()
        self.getcomments()

    def changecat(self, cat):
        """Change the category."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        cat += 1
        print(cat)  # TODO
        QtGui.QApplication.restoreOverrideCursor()

    def fetchpkg(self, pkgid):
        """Fetch the package data."""
        self.awpkg = DS.w.fetchpkg(pkgid)

    def getcomments(self):
        """Get the comments."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        self.fetchpkg(self.pkg['ID'])
        self.fetchcomments()
        QtGui.QApplication.restoreOverrideCursor()

    def fetchcomments(self):
        """Load the comments."""
        c = DS.w.fetchcomments(self.awpkg)

        if c:
            self.cgroup.setEnabled(True)
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
