#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.2.1
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

from . import tr
from .. import DS
from PyQt4 import Qt, QtGui, QtCore
from pkgbuilder import DS as PBDS
import pkgbuilder.upgrade as pu
import pkgbuilder.utils
import threading


class UpgradeDialog(QtGui.QDialog):
    """The upgrade window for aurqt."""
    def _aurinfo(self):
        """A helper function."""
        self.aurinfo = pkgbuilder.utils.info(pu.gather_foreign_pkgs())

    def _ulist(self, vcsup):
        """Yet another helper function."""
        self.ulist = pu.list_upgradable(pu.gather_foreign_pkgs(), vcsup,
                                        aurcache=self.aurinfo)

    def refresh(self, *args, **kwargs):
        """Refresh the upgrades list."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        self.table.clear()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)
        dwn = self.dwnmode.checkState() == 2
        vcsup = self.vcsmode.checkState() == 2
        pb = Qt.QProgressDialog()
        pb.setLabelText(tr('Refreshing package information...'))
        pb.setMaximum(0)
        pb.setValue(-1)
        pb.setWindowModality(QtCore.Qt.WindowModal)
        pb.show()
        Qt.QCoreApplication.processEvents()
        if 'info' in kwargs:
            self.aurinfo = kwargs['info']
            _pt = threading.Thread(target=PBDS._pycreload)
            _pt.start()
            while _pt.is_alive():
                Qt.QCoreApplication.processEvents()
        else:
            _at = threading.Thread(target=self._aurinfo)
            _at.start()

            while _at.is_alive():
                Qt.QCoreApplication.processEvents()

            _pt = threading.Thread(target=PBDS._pycreload)
            _pt.start()

            while _pt.is_alive():
                Qt.QCoreApplication.processEvents()

        _lt = threading.Thread(target=self._ulist, args=(vcsup,))
        _lt.start()
        while _lt.is_alive():
            Qt.QCoreApplication.processEvents()

        if dwn:
            self.ulist = self.ulist[0] + self.ulist[1]
        else:
            self.ulist = self.ulist[0]

        pb.close()

        if self.ulist:
            self.greet.setText(tr('Found the following upgrades:'))
            self.epilog.show()
            self.table.setColumnCount(3)
            self.table.setRowCount(len(self.ulist))
            self.table.setHorizontalHeaderLabels([tr('Name'), tr('Current'),
                                                  tr('New')])
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
            self.greet.setText(tr('No upgrades found.'))
            self.epilog.hide()

        self.table.setSortingEnabled(True)
        QtGui.QApplication.restoreOverrideCursor()

    @property
    def items(self):
        """All the items we have."""
        return [self.table.item(i, 0) for i in range(len(self.ulist))]

    def dvchange(self, *args):
        self.refresh(info=self.aurinfo)

    def install(self):
        """Install the selected upgrades."""
        upgrades = []
        for i in self.items:
            if i.checkState() == 2:
                upgrades.append(i.text())

        if upgrades:
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

        refresh = QtGui.QPushButton(tr('Refresh'), self)
        refresh.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        self.greet = QtGui.QLabel(tr('Searching for upgrades...'), self)
        self.epilog = QtGui.QLabel(tr('Choose the packages you want to '
                                     'upgrade and press OK.'), self)
        self.greet.setWordWrap(True)
        self.epilog.setWordWrap(True)
        self.epilog.hide()
        modeg = QtGui.QGroupBox(tr('Show:'), self)
        modelay = QtGui.QVBoxLayout(modeg)
        self.dwnmode = QtGui.QCheckBox(tr('Downgrades'), modeg)
        self.vcsmode = QtGui.QCheckBox(tr('VCS packages'), modeg)
        modelay.addWidget(self.dwnmode)
        modelay.addWidget(self.vcsmode)

        checkg = QtGui.QGroupBox(tr('Check:'), self)
        checklay = QtGui.QHBoxLayout(checkg)
        call = QtGui.QPushButton(tr('All'), checkg)
        cnone = QtGui.QPushButton(tr('None'), checkg)
        crev = QtGui.QPushButton(tr('Reverse'), checkg,
                                 toolTip=tr('Revert the selection.'))

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
        QtCore.QObject.connect(self.dwnmode, QtCore.SIGNAL('stateChanged(int)'),
                               self.dvchange)
        QtCore.QObject.connect(self.vcsmode, QtCore.SIGNAL('stateChanged(int)'),
                               self.dvchange)
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
        self.setWindowTitle(tr('Upgrade'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('system-software-update'))
        self.resize(450, 500)
        self.refresh()
        QtGui.QApplication.restoreOverrideCursor()
        self.show()
