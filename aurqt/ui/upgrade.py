#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.upgrade
    ~~~~~~~~~~~~~~~~
    The upgrade window for aurqt.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import _
from ..upgrade import Upgrade
from PyQt4 import Qt, QtGui, QtCore
import threading
import time

class UpgradeDialog(QtGui.QDialog):
    """The upgrade window for aurqt."""
    def genulist(self):
        """Generate the upgrades list."""
        upgrade = Upgrade()
        self.ulist = upgrade.list()
        self.rnotdone = False

    def refresh(self):
        """Refresh the upgrades list."""
        self.greet.setText(_('Searching for upgrades…'))
        self.table.clear()
        upgrade = Upgrade()
        ulist = upgrade.list()[0]

        if ulist:
            self.greet.setText(_('Found the following upgrades:'))
            self.epilog.show()
            self.table.setColumnCount(3)
            self.table.setRowCount(len(ulist))
            self.table.setHorizontalHeaderLabels([_('Name'), _('Current'),
                                                  _('New')])
            j = 0
            for i in ulist:
                item = QtGui.QTableWidgetItem()
                item.setText(i[0])
                item.setCheckState(QtCore.Qt.Checked)
                self.table.setItem(j, 0, item)

                item = QtGui.QTableWidgetItem()
                item.setText(i[1])
                self.table.setItem(j, 1, item)

                item = QtGui.QTableWidgetItem()
                item.setText(i[2])
                self.table.setItem(j, 2, item)

                j += 1
        else:
            self.greet.setText(_('No upgrades found.'))


    def install(self):
        """Install the selected upgrades."""
        #TODO: run users’ AUR helper with stuff.  Also, checkboxes.
        self.accept()

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
        self.table = QtGui.QTableWidget(self)
        self.btn = QtGui.QDialogButtonBox(self)
        self.btn.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        lay.addWidget(refresh)
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
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowTitle(_('Upgrade'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('system-software-update'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.refresh()
        self.resize(300, 400)
        self.show()
        QtGui.QApplication.restoreOverrideCursor()
