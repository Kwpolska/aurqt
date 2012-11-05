#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.999
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.TEMPLATE
    ~~~~~~~~~~~~~~~~~
    The TEMPLATE for aurqt.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import _
from PyQt4 import Qt, QtGui, QtCore


class TEMPLATEDialog(QtGui.QDialog):
    """The TEMPLATE for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(TEMPLATEDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        lay.addWidget(btn)

        QtCore.QObject.connect(btn, QtCore.SIGNAL('accepted()'), self.accept)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('TEMPLATE'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('template'))
        self.show()
