#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.preferences
    ~~~~~~~~~~~~~~~~~~~~
    The preferences dialog for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import DS, _
from PyQt4 import Qt, QtGui, QtCore


class PreferencesDialog(QtGui.QDialog):
    """The preferences dialog for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(PreferencesDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        # Group 1: favorite helper
        helperg = QtGui.QGroupBox(_('AUR helper'), self)
        helperl = QtGui.QGridLayout(helperg)

        self.hname = QtGui.QComboBox(helperg)
        self.hname.setEditable(True)
        self.hname.setToolTip(_('command'))
        # Sorting demi-alphabetically (to have PB as default and ignore sudo
        # in front of aura), but this is actually my order of AUR helper
        # preference.  Not adding PBWrapper because it would be a waste of time
        # (PBWrapper throws a request to the API with package names to decide
        # which to install with pacman and which go to PB).
        self.hname.addItem('pkgbuilder')
        self.hname.addItem('sudo aura')
        self.hname.addItem('pacaur')
        self.hname.addItem('packer')
        self.hname.addItem('yaourt')

        self.hargs = QtGui.QLineEdit(helperg)
        self.hargs.setToolTip(_('arguments used to install AUR packages'))
        hlabel = QtGui.QLabel(_('packages to install'), helperg)
        htext = QtGui.QLabel(_('The helper will run in a terminal window.\n'
                               'Requirements:\n1. dependency resolution\n'
                               '2. actually building and installing packages '
                               '(so no cower)'), helperg)
        htext.setAlignment(QtCore.Qt.AlignJustify)

        helperl.addWidget(self.hname, 0, 0, 1, 1)
        helperl.addWidget(self.hargs, 0, 1, 1, 1)
        helperl.addWidget(hlabel, 0, 2, 1, 1)
        helperl.addWidget(htext, 1, 0, 1, 3)

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Ok |
                               QtGui.QDialogButtonBox.Cancel)

        lay.addWidget(QtGui.QLabel(_('aurqt doesn’t have too many prefe'
                                     'rences, unlike most of FOSS.'), self))
        lay.addWidget(helperg)
        lay.addWidget(btn)

        QtCore.QObject.connect(btn, QtCore.SIGNAL('accepted()'), self.save)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('Preferences'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('preferences'))
        self.load()
        self.show()

    def load(self):
        """Load the values."""
        self.hname.setEditText(DS.config['helper']['name'])
        self.hargs.setText(DS.config['helper']['args'])

    def save(self):
        """Save the values."""
        DS.config['helper']['name'] = self.hname.currentText()
        DS.config['helper']['args'] = self.hargs.text()
        with open(DS.conffile, 'w') as cfile:
            DS.config.write(cfile)

        self.accept()
