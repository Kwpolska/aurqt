#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.99
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.Preferences
    ~~~~~~~~~~~~~~~~~~~~
    The preferences dialog for aurqt.

    :Copyright: © 2012, Kwpolska.
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

        # Group 1: aurqt
        aurqtg = QtGui.QGroupBox('aurqt', self)
        aurqtl = QtGui.QVBoxLayout(aurqtg)

        self.noremember = QtGui.QCheckBox(_('Allow session remembering'),
                                          aurqtg)
        self.noremember.setToolTip(_('The “Remember me” button in the '
                                     'login window will be enabled.'))

        self.generation = QtGui.QCheckBox(_('Show the mail generation '
                                            'options'), aurqtg)
        self.generation.setToolTip(_('Allow generating and sending mails '
                                     'to the aur-general list with requests '
                                     'for deletion, merges and disowning.'))

        aurqtl.addWidget(self.noremember)
        aurqtl.addWidget(self.generation)

        # Group 2: terminal emulator
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
                                'most popular ones'))
        tlabel = QtGui.QLabel(_('command to execute'), termg)

        terml.addWidget(self.tname)
        terml.addWidget(self.targs)
        terml.addWidget(tlabel)

        # Group 3: favorite helper
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

        lay.addWidget(aurqtg)
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

    def parse(self, value, save=False, reverse=False):
        """Parse value loading and saving."""
        if save:
            values = {2: 'yes', 0: 'no'}
        else:
            values = {'yes': 2, 'no': 0}

        return values[value]

    def load(self):
        self.noremember.setCheckState(self.parse(
                                      DS.config['aurqt']['remember']))
        self.generation.setCheckState(self.parse(
                                      DS.config['aurqt']['mail-generation']))

        self.hname.setEditText(DS.config['helper']['name'])
        self.hargs.setText(DS.config['helper']['args'])

        self.tname.setEditText(DS.config['term']['name'])
        self.targs.setText(DS.config['term']['args'])

    def save(self):
        DS.config['aurqt']['remember'] = self.parse(
            self.noremember.checkState(), save=True)
        DS.config['aurqt']['mail-generation'] = self.parse(
            self.generation.checkState(), save=True)

        DS.config['term']['name'] = self.tname.currentText()
        DS.config['term']['args'] = self.targs.text()

        DS.config['helper']['name'] = self.hname.currentText()
        DS.config['helper']['args'] = self.hargs.text()
        with open(DS.conffile, 'w') as cfile:
            DS.config.write(cfile)

        self.accept()
