#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.upload
    ~~~~~~~~~~~~~~~
    The upload dialog for aurqt.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import _
from PyQt4 import Qt, QtGui, QtCore
import pkgbuilder


class UploadDialog(QtGui.QDialog):
    """The upload dialog for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(UploadDialog, self).__init__(parent)
        self.queue = []
        self.itemstorage = {}

        lay = QtGui.QGridLayout(self)
        self.table = QtGui.QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([_('File'), _('Category'),
                                              _('Status')])

        lay.addWidget(self.table, 0, 0, 1, 5)
        delbtn = QtGui.QPushButton(_('Remove selected'), self)
        delbtn.setIcon(QtGui.QIcon.fromTheme('list-remove'))
        lay.addWidget(delbtn, 1, 0, 1, 5)
        self.fname = QtGui.QLineEdit(self)
        lay.addWidget(self.fname, 2, 0, 1, 1)
        browse = QtGui.QPushButton(_('Browse'), self)
        lay.addWidget(browse, 2, 1, 1, 2)
        self.category = QtGui.QComboBox(self)
        lay.addWidget(self.category, 2, 3, 1, 1)
        addbtn = QtGui.QPushButton(_('Add'), self)
        addbtn.setIcon(QtGui.QIcon.fromTheme('list-add'))
        lay.addWidget(addbtn, 2, 4, 1, 1)
        upbtn = QtGui.QPushButton(_('Upload'), self)
        upbtn.setIcon(QtGui.QIcon.fromTheme('go-next'))
        lay.addWidget(upbtn, 3, 0, 1, 5)
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.hide()
        #self.pbar.setProperty('value', 24) #TODO
        lay.addWidget(self.pbar, 4, 0, 1, 5)

        for i in pkgbuilder.DS.categories[1:]:
            self.category.addItem(i)

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Close)

        lay.addWidget(btn, 5, 0, 1, 5)

        #QtCore.QObject.connect(btn, QtCore.SIGNAL('accepted()'), self.accept)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('rejected()'), self.reject)

        QtCore.QObject.connect(addbtn, QtCore.SIGNAL('pressed()'), self.add)
        QtCore.QObject.connect(browse, QtCore.SIGNAL('pressed()'), self.browse)
        QtCore.QObject.connect(upbtn, QtCore.SIGNAL('pressed()'), self.upload)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('Upload'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('list-add'))
        self.show()

    def browse(self):
        """Browse for files."""

        fname = QtGui.QFileDialog.getOpenFileName(self,
               _('Browse for source packages'), '',
               _('Source packages') + '(*.src.tar.gz)')

        if fname:
            self.fname.setText(fname)

    def add(self):
        """Add a file to queue."""
        cat = self.category.currentIndex() + 1
        fname = self.fname.text()
        if not fname:
            QtGui.QMessageBox.critical(self, 'aurqt', _('No file selected.'),
                                       QtGui.QMessageBox.Ok)
        else:
            slot = len(self.queue)
            self.queue.append([fname, cat])
            self.table.setRowCount(len(self.queue))

            storageitem = []

            item = QtGui.QTableWidgetItem()
            item.setText(fname)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.table.setItem(slot, 0, item)
            storageitem.append(item)

            item = QtGui.QTableWidgetItem()
            item.setText(pkgbuilder.DS.categories[cat])
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.table.setItem(slot, 1, item)
            storageitem.append(item)

            item = QtGui.QTableWidgetItem()
            item.setText(_('Waiting'))
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.table.setItem(slot, 2, item)
            storageitem.append(item)

            self.itemstorage.update({fname: storageitem})

            self.fname.setText('')
            self.category.setCurrentIndex(0)

    def run_upload(self):
        """Do the actual upload magic."""
        self.pbar.show()
        for i in self.queue:
            print(i[0], i[1]) #TODO

    def upload(self):
        """Run the upload thread."""
        self.run_upload() #TODO
