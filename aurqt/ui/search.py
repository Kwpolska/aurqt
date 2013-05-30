#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.2.0
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.search
    ~~~~~~~~~~~~~~~
    The Search dialog for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import tr
from .. import AQError
from PyQt4 import Qt, QtGui, QtCore
import pkgbuilder
import pkgbuilder.utils


class SearchDialog(QtGui.QDialog):
    """The Search dialog for aurqt."""
    def __init__(self, parent=None, o=None, q=None, m=False, a=False):
        """Initialize the dialog."""
        super(SearchDialog, self).__init__(parent)
        self.setWindowTitle(tr('Search')) # changed by .search() later

        if o:
            self.o = o
        else:
            raise AQError('search', 'oNotPresent', 'o not present')

        lay = QtGui.QVBoxLayout(self)
        frame = QtGui.QFrame(self)
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setFrameShadow(QtGui.QFrame.Raised)
        top = QtGui.QHBoxLayout(frame)

        # Top frame contents.
        self.query = QtGui.QLineEdit(frame)
        self.qtype = QtGui.QComboBox(frame)
        self.qtype.insertItem(0, tr('Name/Description'))
        self.qtype.insertItem(1, tr('Maintainer'))
        btn = QtGui.QPushButton(tr('Search'), frame)
        btn.setDefault(True)
        btn.setIcon(QtGui.QIcon.fromTheme('edit-find'))

        self.table = QtGui.QTableWidget(self, sortingEnabled=True)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([tr('Category'), tr('Name'),
                                              tr('Version'), tr('Votes'),
                                              tr('Description'),
                                              tr('Maintainer')])
        QtCore.QObject.connect(self.table,
                               QtCore.SIGNAL('itemDoubleClicked('
                                             'QTableWidgetItem *)'),
                               self.openpkg)

        top.addWidget(self.query)
        top.addWidget(self.qtype)
        top.addWidget(btn)

        lay.addWidget(frame)
        lay.addWidget(self.table)

        if q:
            self.query.setText(q)
            if m:
                self.qtype.setCurrentIndex(1)
            if a:
                self.search()

        QtCore.QObject.connect(btn, QtCore.SIGNAL('clicked()'), self.search)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.WindowModal)
        self.setWindowIcon(QtGui.QIcon.fromTheme('edit-find'))

    def openpkg(self, item):
        pkgname = None
        itemcount = None
        for i in self.itemstorage.keys():
            if item in self.itemstorage[i]:
                pkgname = i
                break

        if pkgname:
            for i, j in enumerate(self.results):
                if pkgname == j.name:
                    itemcount = i
                    break
        else:
            QtGui.QMessageBox.critical(self, 'aurqt', tr('Internal error.')
                                       + '\nsearch/openpkg noname',
                                       QtGui.QMessageBox.Ok)

        if pkgname and itemcount is not None:
            self.o(pkgname, self.results[itemcount])
        else:
            QtGui.QMessageBox.critical(self, 'aurqt', tr('Internal error.')
                                       + '\nsearch/openpkg nocount',
                                       QtGui.QMessageBox.Ok)

    def search(self):
        """Perform the search."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
            QtCore.Qt.WaitCursor))
        if self.qtype.currentIndex() == 0:
            qtype = 'search'
        else:
            qtype = 'msearch'

        query = self.query.text()
        self.table.setSortingEnabled(False)
        self.itemstorage = {}
        self.table.clear()
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels([tr('Category'), tr('Name'),
                                              tr('Version'), tr('Votes'),
                                              tr('Description'),
                                              tr('Maintainer')])

        if len(query) == 0:
            pass  # Ignore, because I have nothing to do.
        elif len(query) == 1:
                QtGui.QApplication.restoreOverrideCursor()
                QtGui.QMessageBox.critical(self, 'aurqt', tr('Your query is too'
                                           ' short.'), QtGui.QMessageBox.Ok)
        else:
            if qtype == 'search':
                self.results = pkgbuilder.utils.search(query)
            elif qtype == 'msearch':
                self.results = pkgbuilder.utils.msearch(query)

            self.table.setRowCount(len(self.results))
            j = 0
            for i in self.results:
                storageitem = []
                item = QtGui.QTableWidgetItem()
                item.setText(i.repo)
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
                self.table.setItem(j, 0, item)
                storageitem.append(item)

                item = QtGui.QTableWidgetItem()
                item.setText(i.name)
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
                self.table.setItem(j, 1, item)
                storageitem.append(item)

                item = QtGui.QTableWidgetItem()
                item.setText(i.version)
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)

                if i.is_outdated:
                    brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item.setForeground(brush)

                self.table.setItem(j, 2, item)
                storageitem.append(item)

                item = QtGui.QTableWidgetItem()
                item.setText(str(i.votes))
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
                self.table.setItem(j, 3, item)
                storageitem.append(item)

                item = QtGui.QTableWidgetItem()
                item.setText(i.description)
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
                self.table.setItem(j, 4, item)
                storageitem.append(item)

                item = QtGui.QTableWidgetItem()
                item.setText(i.human)
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
                self.table.setItem(j, 5, item)
                storageitem.append(item)

                self.itemstorage.update({i.name: storageitem})

                j += 1

        self.table.setSortingEnabled(True)
        if qtype == 'msearch':
            searchprefix = ' -- [{0}] '.format(tr('M|aintainer (TRANSLATORS: '
                                                 'put | after the first '
                                                 'character of the word for '
                                                 'Maintainer)').split('|')[0])
        else:
            searchprefix = ' -- '
        self.setWindowTitle(tr('Search') + searchprefix + query)
        QtGui.QApplication.restoreOverrideCursor()
