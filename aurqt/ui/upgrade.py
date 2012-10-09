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


class UpgradeDialog(QtGui.QDialog):
    """The upgrade window for aurqt."""
    def refresh(self):
        """Refresh the upgrades list."""
        self.greet.setText(_('Searching for upgrades…'))
        self.btn.setEnabled(False)
        self.table.setEnabled(False)
        upgrade = Upgrade()
        self.ulist = upgrade.list()[0]

        if not self.ulist:
            self.greet.setText(_('No upgrades found.'))
            self.btn.setStandardButtons(QtGui.QDialogButtonBox.Close)
        else:
            self.epilog.show()
            self.btn.setStandardButtons(QtGui.QDialogButtonBox.Ok |
                                        QtGui.QDialogButtonBox.Cancel)
            self.greet.setText(_('Found the following upgrades:'))
            #TODO

        self.btn.setEnabled(True)

    def install(self):
        """Install the selected upgrades."""
        #TODO: run users’ AUR helper with stuff.  Also, checkboxes.
        print(self.ulist)
        self.accept()

    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(UpgradeDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        refresh = QtGui.QPushButton(_('Refresh'), self)
        refresh.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        self.greet = QtGui.QLabel(_('Please hit Refresh to search for '
                                    'upgrades.'), self)
        self.epilog = QtGui.QLabel(_('Choose the packages you want to '
                                     'upgrade and press OK.'), self)
        self.greet.setWordWrap(True)
        self.epilog.setWordWrap(True)
        self.epilog.hide()
        self.table = QtGui.QTableWidget(self) # TODO?
        self.table.setEnabled(False)
        self.btn = QtGui.QDialogButtonBox(self)
        self.btn.setStandardButtons(QtGui.QDialogButtonBox.Close)

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

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('Upgrade'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('system-software-update'))
        self.resize(300, 400)
        self.show()
