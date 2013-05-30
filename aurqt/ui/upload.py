#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.2.1
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.upload
    ~~~~~~~~~~~~~~~
    The upload dialog for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import tr
from .. import DS
from PyQt4 import Qt, QtGui, QtCore
from collections import OrderedDict
import pkgbuilder.package

QUEUE = []


class UploadDialog(QtGui.QDialog):
    """The upload dialog for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(UploadDialog, self).__init__(parent)
        self.queue = []
        self.itemstorage = OrderedDict()
        self.oldqueue = []
        self.done = []

        lay = QtGui.QHBoxLayout(self)
        self.fname = QtGui.QLineEdit(self)
        browse = QtGui.QPushButton(tr('Browse'), self)
        self.category = QtGui.QComboBox(self)
        addbtn = QtGui.QPushButton(tr('Upload'), self)
        addbtn.setIcon(QtGui.QIcon.fromTheme('list-add'))

        for i in pkgbuilder.package.CATEGORIES[1:]:
            self.category.addItem(i)

        self.btn = QtGui.QDialogButtonBox(self)
        self.btn.setStandardButtons(QtGui.QDialogButtonBox.Close)

        lay.addWidget(self.fname)
        lay.addWidget(browse)
        lay.addWidget(self.category)
        lay.addWidget(addbtn)
        lay.addWidget(self.btn)

        QtCore.QObject.connect(self.btn, QtCore.SIGNAL('rejected()'),
                               self.reject)

        QtCore.QObject.connect(addbtn, QtCore.SIGNAL('pressed()'), self.add)
        QtCore.QObject.connect(browse, QtCore.SIGNAL('pressed()'), self.browse)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(tr('Upload'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('list-add'))
        self.show()

    def browse(self):
        """Browse for files."""
        fname = QtGui.QFileDialog.getOpenFileName(self, tr('Browse for source '
                                                  'packages'), '', tr('Source '
                                                  'packages') +
                                                  '(*.src.tar.gz)')

        if fname:
            self.fname.setText(fname)

    def add(self):
        """Add a file to queue."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        cat = self.category.currentIndex() + 1
        fname = self.fname.text()
        if not fname:
            QtGui.QApplication.restoreOverrideCursor()
            QtGui.QMessageBox.critical(self, 'aurqt', tr('No file selected.'),
                                       QtGui.QMessageBox.Ok)
        else:
            DS.w.upload(fname, cat)
            self.fname.setText('')
            self.category.setCurrentIndex(0)
            QtGui.QApplication.restoreOverrideCursor()
