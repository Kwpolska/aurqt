#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.999
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.upgrade
    ~~~~~~~~~~~~~~~~
    The upgrade window for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import DS, _
from PySide import Qt, QtGui, QtCore
import pkgbuilder.upgrade


class UpgradeDialog(QtGui.QDialog):
    """The upgrade window for aurqt."""
    def refresh(self):
        """Refresh the upgrades list."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        self.table.clear()
        self.table.setSortingEnabled(False)
        dwn = self.dwnmode.checkState() == 2
        vcsup = self.vcsmode.checkState() == 2
        u = pkgbuilder.upgrade.Upgrade()
        self.ulist = u.list_upgradable(u.gather_foreign_pkgs(), vcsup)

        if dwn:
            self.ulist = self.ulist[0] + self.ulist[1]
        else:
            self.ulist = self.ulist[0]

        if self.ulist:
            self.greet.setText(_('Found the following upgrades:'))
            self.epilog.show()
            self.table.setColumnCount(3)
            self.table.setRowCount(len(self.ulist))
            self.table.setHorizontalHeaderLabels([_('Name'), _('Current'),
                                                  _('New')])
            for i, j in enumerate(self.ulist):
                item = QtGui.QTableWidgetItem()
                item.setText(j[0])
                item.setCheckState(QtCore.Qt.Checked)
                self.table.setItem(i, 0, item)

                item = QtGui.QTableWidgetItem()
                item.setText(j[1])
                self.table.setItem(i, 1, item)

                item = QtGui.QTableWidgetItem()
                item.setText(j[2])
                self.table.setItem(i, 2, item)
        else:
            self.greet.setText(_('No upgrades found.'))

        self.table.setSortingEnabled(True)
        QtGui.QApplication.restoreOverrideCursor()

    @property
    def items(self):
        """All the items we have."""
        return [self.table.item(i, 0) for i in range(len(self.ulist))]

    def install(self):
        """Install the selected upgrades."""
        upgrades = []
        for i in self.items:
            if i.checkState() == 2:
                upgrades.append(i.text())

        DS.pkginst(upgrades)

        self.accept()

    def check_all(self):
        """Check _ALL_ the things."""
        for c, item in enumerate(self.items):
            item.setCheckState(2)
            self.table.takeItem(c, 0)
            self.table.setItem(c, 0, item)

    def check_none(self):
        """Uncheck _ALL_ the things."""
        for c, item in enumerate(self.items):
            item.setCheckState(0)
            self.table.takeItem(c, 0)
            self.table.setItem(c, 0, item)

    def check_revert(self):
        """Check HALF-ALL-OR-SOMETHING-LIKE-THAT the things."""
        for c, item in enumerate(self.items):
            if item.checkState() == 2:
                item.setCheckState(0)
            else:
                item.setCheckState(2)

            self.table.takeItem(c, 0)
            self.table.setItem(c, 0, item)

    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(UpgradeDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        refresh = QtGui.QPushButton(_('Refresh'), self)
        refresh.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        self.greet = QtGui.QLabel(_('Searching for upgrades…'), self)
        self.epilog = QtGui.QLabel(_('Choose the packages you want to '
                                     'upgrade and press OK.'), self)
        self.greet.setWordWrap(True)
        self.epilog.setWordWrap(True)
        self.epilog.hide()
        modeg = QtGui.QGroupBox(_('Show:'), self)
        modelay = QtGui.QVBoxLayout(modeg)
        self.dwnmode = QtGui.QCheckBox(_('Downgrades'), modeg)
        self.vcsmode = QtGui.QCheckBox(_('VCS packages'), modeg)
        modelay.addWidget(self.dwnmode)
        modelay.addWidget(self.vcsmode)

        checkg = QtGui.QGroupBox(_('Check:'), self)
        checklay = QtGui.QHBoxLayout(checkg)
        call = QtGui.QPushButton(_('All'), checkg)
        cnone = QtGui.QPushButton(_('None'), checkg)
        crev = QtGui.QPushButton(_('Reverse'), checkg,
                                 toolTip=_('Revert the selection.'))

        checklay.addWidget(call)
        checklay.addWidget(cnone)
        checklay.addWidget(crev)

        self.table = QtGui.QTableWidget(self, sortingEnabled=True)
        self.btn = QtGui.QDialogButtonBox(self)
        self.btn.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        lay.addWidget(refresh)
        lay.addWidget(modeg)
        lay.addWidget(checkg)
        lay.addWidget(self.greet)
        lay.addWidget(self.table)
        lay.addWidget(self.epilog)
        lay.addWidget(self.btn)

        QtCore.QObject.connect(self.btn, QtCore.SIGNAL('accepted()'),
                               self.install)
        QtCore.QObject.connect(self.btn, QtCore.SIGNAL('rejected()'),
                               self.reject)
        QtCore.QObject.connect(refresh, QtCore.SIGNAL('clicked()'),
                               self.refresh)
        QtCore.QObject.connect(call, QtCore.SIGNAL('clicked()'),
                               self.check_all)
        QtCore.QObject.connect(cnone, QtCore.SIGNAL('clicked()'),
                               self.check_none)
        QtCore.QObject.connect(crev, QtCore.SIGNAL('clicked()'),
                               self.check_revert)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowTitle(_('Upgrade'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('system-software-update'))
        self.resize(450, 500)
        self.refresh()
        QtGui.QApplication.restoreOverrideCursor()
        self.show()
