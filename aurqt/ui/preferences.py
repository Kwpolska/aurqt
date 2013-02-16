#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.999
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.Preferences
    ~~~~~~~~~~~~~~~~~~~~
    The preferences dialog for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import DS, _
from PySide import Qt, QtGui, QtCore


class PreferencesDialog(QtGui.QDialog):
    """The preferences dialog for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(PreferencesDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        # Group 1: terminal emulator
        termg = QtGui.QGroupBox(_('Terminal emulator'), self)
        terml = QtGui.QHBoxLayout(termg)

        self.tname = QtGui.QComboBox(termg)
        self.tname.setEditable(True)
        self.tname.setToolTip(_('command'))
        self.tname.addItem('konsole')
        self.tname.addItem('gnome-terminal')
        self.tname.addItem('lxterminal')
        self.tname.addItem('mate-terminal')
        self.tname.addItem('terminal')  # (Xfce)
        self.tname.addItem('urxvt')
        self.tname.addItem('xterm')

        self.targs = QtGui.QLineEdit(termg)
        self.targs.setToolTip(_('arguments used to run a command in the '
                                'terminal emulator of choice (-e in the '
                                'most popular ones)'))
        tlabel = QtGui.QLabel(_('command to execute'), termg)

        terml.addWidget(self.tname)
        terml.addWidget(self.targs)
        terml.addWidget(tlabel)

        # Group 2: favorite helper
        helperg = QtGui.QGroupBox(_('AUR helper'), self)
        helperl = QtGui.QGridLayout(helperg)

        self.hname = QtGui.QComboBox(helperg)
        self.hname.setEditable(True)
        self.hname.setToolTip(_('command'))
        # Sorting demi-alphabetically (to have PB as default and ignore sudo
        # in front of aura), but this is actually my order of AUR helper
        # preference.  Not adding PBWrapper because it would be a waste of time
        # (PBWrapper throws a request to the API with package names to decide
        # which to install with pacman and which go to PB.
        self.hname.addItem('pkgbuilder')
        self.hname.addItem('sudo aura')
        self.hname.addItem('packer')
        self.hname.addItem('yaourt')

        self.hargs = QtGui.QLineEdit(helperg)
        self.hargs.setToolTip(_('arguments used to install AUR packages'))
        hlabel = QtGui.QLabel(_('packages to install'), helperg)
        htext = QtGui.QLabel(_('The helper will run in a terminal window.\n'
                               'Requirements:\ndependency resolution;\n'
                               'actually building and installing packages '
                               '(so no cower)'), helperg)
        htext.setAlignment(QtCore.Qt.AlignJustify)

        helperl.addWidget(self.hname, 0, 0, 1, 1)
        helperl.addWidget(self.hargs, 0, 1, 1, 1)
        helperl.addWidget(hlabel, 0, 2, 1, 1)
        helperl.addWidget(htext, 1, 0, 1, 3)

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Ok |
                               QtGui.QDialogButtonBox.Cancel)

        lay.addWidget(termg)
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

        self.tname.setEditText(DS.config['term']['name'])
        self.targs.setText(DS.config['term']['args'])

    def save(self):
        """Save the values."""
        DS.config['term']['name'] = self.tname.currentText()
        DS.config['term']['args'] = self.targs.text()

        DS.config['helper']['name'] = self.hname.currentText()
        DS.config['helper']['args'] = self.hargs.text()
        with open(DS.conffile, 'w') as cfile:
            DS.config.write(cfile)

        self.accept()
