#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.notifications
    ~~~~~~~~~~~~~~~~~~~~~~
    The notifications dialog for aurqt.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import AQError, _
from PyQt4 import Qt, QtGui, QtCore
import aurqt.notifications

class NotificationsDialog(QtGui.QDialog):
    """The notifications dialog for aurqt."""
    def __init__(self, parent=None, o=None):
        """Initialize the dialog."""
        super(NotificationsDialog, self).__init__(parent)

        if o:
            self.o = o
        else:
            raise AQError('search', 'oNotPresent', '“o” not present')

        lay = QtGui.QVBoxLayout(self)

        refreshb = QtGui.QPushButton(_('Refresh'), self,
                                     icon=QtGui.QIcon.fromTheme(
                                          'view-refresh'))
        self.nlist = QtGui.QListWidget(self)

        lay.addWidget(refreshb)
        lay.addWidget(self.nlist)

        QtCore.QObject.connect(refreshb, QtCore.SIGNAL('pressed()'),
                               self.refresh)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowTitle(_('Notifications'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('dialog-information'))

        self.load()

    def load(self):
        self.nlist.addItems(aurqt.notifications.generate())

    def refresh(self):
        """Refresh the notifications."""
        # TODO
        self.load()
