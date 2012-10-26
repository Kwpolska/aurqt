#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.search
    ~~~~~~~~~~~~~~~
    The Search dialog for aurqt.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import AQError, _
from PyQt4 import Qt, QtGui, QtCore
import pkgbuilder
import pkgbuilder.aur


class SearchDialog(QtGui.QDialog):
    """The Search dialog for aurqt."""
    def __init__(self, parent=None, o=None, q=None, m=False, a=False):
        """Initialize the dialog."""
        super(SearchDialog, self).__init__(parent)
        if o:
            self.o = o
        else:
            raise AQError('search', 'oNotPresent', '“o” not present')
        self.a = pkgbuilder.aur.AUR()

        lay = QtGui.QVBoxLayout(self)
        frame = QtGui.QFrame(self)
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        frame.setFrameShadow(QtGui.QFrame.Raised)
        top = QtGui.QHBoxLayout(frame)

        # Top frame contents.
        self.query = QtGui.QLineEdit(frame)
        self.qtype = QtGui.QComboBox(frame)
        self.qtype.insertItem(0, _('Name/Description'))
        self.qtype.insertItem(1, _('Maintainer'))
        btn = QtGui.QPushButton(_('Search'), frame)
        btn.setDefault(True)
        btn.setIcon(QtGui.QIcon.fromTheme('edit-find'))

        self.table = QtGui.QTableWidget(self, sortingEnabled=True)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([_('Category'), _('Name'),
                                              _('Version'), _('Votes'),
                                              _('Description'),
                                              _('Maintainer')])
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
        self.setWindowTitle(_('Search'))
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
                if pkgname == j['Name']:
                    itemcount = i
                    break
        else:
            QtGui.QMessageBox.critical(self, 'aurqt', _('Internal error.')
                                       + '\nsearch/openpkg noname',
                                       QtGui.QMessageBox.Ok)

        if pkgname and itemcount is not None:
            self.o(pkgname, self.results[itemcount])
        else:
            QtGui.QMessageBox.critical(self, 'aurqt', _('Internal error.')
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
        self.table.setHorizontalHeaderLabels([_('Category'), _('Name'),
                                              _('Version'), _('Votes'),
                                              _('Description'),
                                              _('Maintainer')])

        if len(query) == 0:
            pass  # Ignore, because I have nothing to do.
        elif len(query) == 1:
                QtGui.QApplication.restoreOverrideCursor()
                QtGui.QMessageBox.critical(self, 'aurqt', _('Your query is too'
                                           ' short.'), QtGui.QMessageBox.Ok)
        else:
            self.results = self.a.request(qtype, query)
            if self.results['type'] != 'error':
                self.results = self.results['results']
                self.table.setRowCount(len(self.results))
                j = 0
                for i in self.results:
                    storageitem = []
                    item = QtGui.QTableWidgetItem()
                    item.setText(pkgbuilder.DS.categories[int(
                                 i['CategoryID'])])
                    item.setFlags(QtCore.Qt.ItemIsSelectable |
                                  QtCore.Qt.ItemIsEnabled)
                    self.table.setItem(j, 0, item)
                    storageitem.append(item)

                    item = QtGui.QTableWidgetItem()
                    item.setText(i['Name'])
                    item.setFlags(QtCore.Qt.ItemIsSelectable |
                                  QtCore.Qt.ItemIsEnabled)
                    self.table.setItem(j, 1, item)
                    storageitem.append(item)

                    item = QtGui.QTableWidgetItem()
                    item.setText(i['Version'])
                    item.setFlags(QtCore.Qt.ItemIsSelectable |
                                  QtCore.Qt.ItemIsEnabled)

                    if i['OutOfDate'] == '1':
                        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
                        brush.setStyle(QtCore.Qt.NoBrush)
                        item.setForeground(brush)

                    self.table.setItem(j, 2, item)
                    storageitem.append(item)

                    item = QtGui.QTableWidgetItem()
                    item.setText(i['NumVotes'])
                    item.setFlags(QtCore.Qt.ItemIsSelectable |
                                  QtCore.Qt.ItemIsEnabled)
                    self.table.setItem(j, 3, item)
                    storageitem.append(item)

                    item = QtGui.QTableWidgetItem()
                    item.setText(i['Description'])
                    item.setFlags(QtCore.Qt.ItemIsSelectable |
                                  QtCore.Qt.ItemIsEnabled)
                    self.table.setItem(j, 4, item)
                    storageitem.append(item)

                    item = QtGui.QTableWidgetItem()
                    item.setText(i['Maintainer'])
                    item.setFlags(QtCore.Qt.ItemIsSelectable |
                                  QtCore.Qt.ItemIsEnabled)
                    self.table.setItem(j, 5, item)
                    storageitem.append(item)

                    self.itemstorage.update({i['Name']: storageitem})

                    j += 1

        self.table.setSortingEnabled(True)
        QtGui.QApplication.restoreOverrideCursor()
