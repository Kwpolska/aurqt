#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.about
    ~~~~~~~~~~~~~~
    The About window for aurqt.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import __version__, __pbversion__, _
from PyQt4 import Qt, QtGui, QtCore


class AboutDialog(QtGui.QDialog):
    """The About window for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(AboutDialog, self).__init__(parent)

        lay = QtGui.QVBoxLayout(self)

        aurqt = QtGui.QLabel('aurqt v{}'.format(__version__), self)
        tagline = QtGui.QLabel(_('INSERT TAGLINE HERE.'), self)
        copy = QtGui.QLabel('Copyright © 2012, Kwpolska.', self)
        localetxt = _('LANG locale by AUTHOR <MAIL@IF.YOU.WANT')
        if localetxt == 'LANG locale by AUTHOR <MAIL@IF.YOU.WANT':
            localetxt = 'No locale in use.'
        locale = QtGui.QLabel(localetxt, self)
        pbinf = QtGui.QLabel(_('Using PKGBUILDer v{}.').format(__pbversion__),
                             self)
        okay = QtGui.QDialogButtonBox(self)
        okay.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        font = QtGui.QFont()
        font.setPointSize(20)

        aurqt.setFont(font)
        aurqt.setAlignment(QtCore.Qt.AlignCenter)
        tagline.setAlignment(QtCore.Qt.AlignCenter)
        copy.setAlignment(QtCore.Qt.AlignCenter)
        locale.setAlignment(QtCore.Qt.AlignCenter)
        pbinf.setAlignment(QtCore.Qt.AlignCenter)

        lay.addWidget(aurqt)
        lay.addWidget(tagline)
        lay.addWidget(copy)
        lay.addWidget(locale)
        lay.addWidget(pbinf)
        lay.addWidget(okay)

        QtCore.QObject.connect(okay, QtCore.SIGNAL('accepted()'), self.accept)
        QtCore.QObject.connect(okay, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('About aurqt'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('help-about'))
        self.show()