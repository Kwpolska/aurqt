#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
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

from .. import DS, _
from PyQt4 import Qt, QtGui, QtCore
from collections import OrderedDict
import pkgbuilder.package

QUEUE = []


class UpThread(QtCore.QThread):
    """The Upload thread."""
    def __init__(self):
        """Initializing the thread."""
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global QUEUE
        item = QUEUE.pop()
        up = DS.w.upload(item[0], item[1])
        if up[0]:
            status = item[0] + '\n|\n' + _('Success')
        else:
            status = item[0] + '\n|\n' + _('Failure: {}').format(up[1])

        self.emit(QtCore.SIGNAL('update(QString)'), status)
        return


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
        browse = QtGui.QPushButton(_('Browse'), self)
        self.category = QtGui.QComboBox(self)
        addbtn = QtGui.QPushButton(_('Upload'), self)
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
        self.setWindowTitle(_('Upload'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('list-add'))
        self.show()

    def browse(self):
        """Browse for files."""
        fname = QtGui.QFileDialog.getOpenFileName(self, _('Browse for source '
                                                  'packages'), '', _('Source '
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
            QtGui.QMessageBox.critical(self, 'aurqt', _('No file selected.'),
                                       QtGui.QMessageBox.Ok)
        else:
            DS.w.upload(fname, cat)
            self.fname.setText('')
            self.category.setCurrentIndex(0)
            QtGui.QApplication.restoreOverrideCursor()
