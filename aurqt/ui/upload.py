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

from .. import DS, _
from PyQt4 import Qt, QtGui, QtCore
from collections import OrderedDict
import pkgbuilder

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

        lay = QtGui.QGridLayout(self)
        self.table = QtGui.QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([_('File'), _('Category'),
                                              _('Status')])

        lay.addWidget(self.table, 0, 0, 1, 5)
        upbtn = QtGui.QPushButton(_('Upload'), self)
        upbtn.setIcon(QtGui.QIcon.fromTheme('go-next'))
        lay.addWidget(upbtn, 3, 0, 1, 5)
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
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.hide()
        lay.addWidget(self.pbar, 4, 0, 1, 5)

        for i in pkgbuilder.DS.categories[1:]:
            self.category.addItem(i)

        self.btn = QtGui.QDialogButtonBox(self)
        self.btn.setStandardButtons(QtGui.QDialogButtonBox.Close)

        lay.addWidget(self.btn, 5, 0, 1, 5)

        QtCore.QObject.connect(self.btn, QtCore.SIGNAL('rejected()'),
                               self.reject)

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
        fname = QtGui.QFileDialog.getOpenFileName(self, _('Browse for source '
                                                  'packages'), '', _('Source '
                                                  'packages') +
                                                  '(*.src.tar.gz)')

        if fname:
            self.fname.setText(fname)

    def add(self):
        """Add a file to queue."""
        global QUEUE  # Sorry.
        self.queue = QUEUE

        if not self.queue:
            self.pbar.hide()
            self.pbar.setValue(0)
            self.table.clear()
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels([_('File'), _('Category'),
                                                  _('Status')])
        cat = self.category.currentIndex() + 1
        fname = self.fname.text()
        if not fname:
            QtGui.QMessageBox.critical(self, 'aurqt', _('No file selected.'),
                                       QtGui.QMessageBox.Ok)
        else:
            slot = len(self.queue)
            self.queue.append([fname, cat, slot])
            self.table.setRowCount(len(self.queue))

            storageitem = [slot]

            item = QtGui.QTableWidgetItem()
            item.setText(fname)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.table.setItem(slot, 0, item)
            storageitem.append(item)

            item = QtGui.QTableWidgetItem()
            item.setText(pkgbuilder.DS.categories[cat])
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.table.setItem(slot, 1, item)
            storageitem.append(item)

            item = QtGui.QTableWidgetItem()
            item.setText(_('Waiting'))
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.table.setItem(slot, 2, item)
            storageitem.append(item)

            self.itemstorage.update({fname: storageitem})

            self.fname.setText('')
            self.category.setCurrentIndex(0)

        QUEUE = self.queue

    def setstatus(self, inp):
        """Set the status."""
        fname, status = inp.split('\n|\n')
        for i in self.oldqueue:
            if i[0] == fname:
                slot = i[2]

        self.table.takeItem(slot, 2)

        item = QtGui.QTableWidgetItem()
        item.setText(status)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.table.setItem(slot, 2, item)
        st = self.itemstorage[fname]
        st[2] = item

        self.itemstorage.update({fname: st})

        self.done.append(fname)
        value = (len(self.done) / len(self.oldqueue)) * 100
        self.pbar.setValue(value)

        if value == 100:
            self.btn.setEnabled(True)

    def upload(self):
        """Run the upload threads."""
        self.pbar.show()
        self.btn.setEnabled(False)
        global QUEUE
        QUEUE = self.queue
        self.thread_pool = []
        self.oldqueue = [i for i in self.queue]  # Cheat.  Sorry.
        for i in self.queue:
            self.thread_pool.append(UpThread())

        for i in self.queue:
            self.connect(self.thread_pool[len(self.thread_pool) - 1],
                         QtCore.SIGNAL("update(QString)"), self.setstatus)
            self.thread_pool[len(self.thread_pool) - 1].start()
            for slot in range(len(self.thread_pool)):
                self.table.takeItem(slot, 2)
                item = QtGui.QTableWidgetItem()
                item.setText(_('Uploading…'))
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
                self.table.setItem(slot, 2, item)
