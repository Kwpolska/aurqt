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

from .. import _
from PyQt4 import Qt, QtGui, QtCore
from pkgbuilder.utils import Utils

class InfoBox(QtGui.QDialog):
    """The package information box for aurqt."""
    def __init__(self, parent=None, pkgname=None):
        """Initialize the box."""
        if not pkgname:
            raise AQError('info', 'pkgnameNotPresent', '`pkgname` not present')
        super(InfoBox, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        pkg = Utils().info([pkgname])[0]
        infostring = pkg['Name'] + ' ' + pkg['Version']

        topbar = QtGui.QFrame(self)
        topbar.setFrameShape(QtGui.QFrame.StyledPanel)
        topbar.setFrameShadow(QtGui.QFrame.Raised)
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
        actionb.setPopupMode(QtGui.QToolButton.MenuButtonPopup) # TODO menus
        actionb.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        actionb.setText(_('Actions'))

        topbarlay.addWidget(self.insta)
        topbarlay.addWidget(actionb)

        name = QtGui.QLabel(infostring, self)
        font = QtGui.QFont()
        font.setPointSize(20)
        name.setFont(font)
        name.setAlignment(QtCore.Qt.AlignCenter)

        desc = QtGui.QLabel(pkg['Description'], self)
        desc.setAlignment(QtCore.Qt.AlignCenter)

        data = QtGui.QGroupBox(self)
        #datalay = QtGui.QFormLayout(desc)
        #datalay.setHorizontalSpacing(15)
        #datalay.setVerticalSpacing(7)

        #comments = QtGui.QLabel('comments', self) #GOES DOWN TODO

        #datalay.setWidget(0, QtGui.QFormLayout.LabelRole, desc)
        #datalay.setWidget(0, QtGui.QFormLayout.FieldRole, comments)

        comments = QtGui.QLabel('comments', self)

        lay.addWidget(topbar)
        lay.addWidget(name)
        lay.addWidget(desc)
        lay.addWidget(data)
        lay.addWidget(comments)

        #QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowTitle(infostring)
        self.setWindowIcon(QtGui.QIcon.fromTheme('dialog-information'))
        self.show()
