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

class UpgradeListThread(QtCore.QThread):
    def __init__(self):
        """Init the thread."""
        QtCore.QThread.__init__(self)

    def run(self):
        """Run the thread."""
        upgrade = Upgrade()
        ulist = upgrade.list()
        ustr = '\n'.join('\\\\'.join(map(str,l)) for l in ulist)
        self.emit(QtCore.SIGNAL('update(QString)'), ustr)

    def __del__(self):
        """Wait for it…"""
        self.wait()


class UpgradeDialog(QtGui.QDialog):
    """The upgrade window for aurqt."""
    def parseupgrades(self, ustr):
        """Parse the upgrades list.  ustr is a cheat."""
        self.ulist = [i.split('\\\\') for i in ustr.split('\n')] #cheating…
        self.ulist = [s for s in self.ulist[0] if s != '']

        if not self.ulist:
            self.greet.setText(_('No upgrades found.'))
            self.btn.setStandardButtons(QtGui.QDialogButtonBox.Close)
            self.btn.setEnabled(True)
        else:
            self.epilog.show()
            self.greet.setText(_('Found the following upgrades:'))
            #TODO
            self.btn.setEnabled(True)

    def install(self):
        """Install the selected upgrades."""
        #TODO: run users’ AUR helper with stuff.  Also, checkboxes.
        print(self.ulist)

    def runthread(self):
        """Run the upgrade list thread."""
        t = UpgradeListThread()
        self.connect(t, QtCore.SIGNAL('update(QString)'),
                     self.parseupgrades)
        t.start()

    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(UpgradeDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        self.greet = QtGui.QLabel(_('Searching for upgrades…'),
                                  self)
        self.epilog = QtGui.QLabel(_('Choose the packages you want to '
                                     'upgrade and press OK.'), self)
        self.epilog.hide()
        self.table = QtGui.QTableWidget(self) # TODO?
        self.table.setEnabled(False)
        self.btn = QtGui.QDialogButtonBox(self)
        self.btn.setStandardButtons(QtGui.QDialogButtonBox.Ok |
                                    QtGui.QDialogButtonBox.Cancel)
        self.btn.setEnabled(False)

        lay.addWidget(self.greet)
        lay.addWidget(self.table)
        lay.addWidget(self.epilog)
        lay.addWidget(self.btn)

        QtCore.QObject.connect(self.btn, QtCore.SIGNAL('accepted()'), self.accept)
        QtCore.QObject.connect(self.btn, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('Upgrade'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('system-software-update'))
        self.show()
