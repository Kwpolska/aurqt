#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.1
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.request
    ~~~~~~~~~~~~~~~~
    The mail request generator for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import DS, _, __version__
from PyQt4 import Qt, QtGui, QtCore
import pkgbuilder.utils
import threading


class RequestDialog(QtGui.QDialog):
    """The mail request generator for aurqt."""
    def __init__(self, parent=None, pkgnames=()):
        """Initialize the dialog."""
        super(RequestDialog, self).__init__(parent)
        self.queue = []

        lay = QtGui.QGridLayout(self)

        typegroup = QtGui.QGroupBox(_('Request type'), self)
        typelay = QtGui.QVBoxLayout(typegroup)

        self.tdel = QtGui.QRadioButton(_('Remove'), typegroup)
        self.tmerge = QtGui.QRadioButton(_('Merge'), typegroup)
        self.torphan = QtGui.QRadioButton(_('Orphan'), typegroup)

        typelay.addWidget(self.tdel)
        typelay.addWidget(self.tmerge)
        typelay.addWidget(self.torphan)

        pkggroup = QtGui.QGroupBox(_('Packages'), self)
        pkglay = QtGui.QGridLayout(pkggroup)

        self.pkgs = QtGui.QTableWidget(pkggroup)
        self.paddname = QtGui.QLineEdit(pkggroup)
        self.padd = QtGui.QPushButton(_('Add'), pkggroup)
        self.pdel = QtGui.QPushButton(_('Remove selected'), pkggroup)

        self.pkgs.setColumnCount(2)
        self.pkgs.setHorizontalHeaderLabels([_('Package'), _('Reason')])

        pkglay.addWidget(self.pkgs, 0, 0, 1, 2)
        pkglay.addWidget(self.paddname, 1, 0, 1, 1)
        pkglay.addWidget(self.padd, 1, 1, 1, 1)
        pkglay.addWidget(self.pdel, 2, 0, 1, 2)

        requesting101 = QtGui.QLabel(_('Copy this message and send it to '
                                       'aur-general@archlinux.org (no '
                                       'subscription necessary).\nPlease '
                                       'consult the package maintainers '
                                       'before sending.\n(Give them two '
                                       'weeks to answer.)'), self)
        #requesting101.setWordWrap(True)
        self.subject = QtGui.QLineEdit(self)
        self.message = QtGui.QTextEdit(self)
        self.message.setStyleSheet('font-family: monospace;')

        lay.addWidget(typegroup, 0, 0, 1, 1)
        lay.addWidget(pkggroup, 0, 1, 1, 1)
        lay.addWidget(requesting101, 1, 0, 1, 2)
        lay.addWidget(self.subject, 2, 0, 1, 2)
        lay.addWidget(self.message, 3, 0, 1, 2)

        QtCore.QObject.connect(self.padd, QtCore.SIGNAL('pressed()'), self.add)
        QtCore.QObject.connect(self.pdel, QtCore.SIGNAL('pressed()'),
                               self.remove)
        QtCore.QObject.connect(self.tdel, QtCore.SIGNAL('toggled(bool)'),
                self.parse_list)
        QtCore.QObject.connect(self.tmerge, QtCore.SIGNAL('toggled(bool)'),
                self.parse_list)
        QtCore.QObject.connect(self.torphan, QtCore.SIGNAL('toggled(bool)'),
                self.parse_list)
        QtCore.QObject.connect(self.pkgs, QtCore.SIGNAL('cellChanged(int, int)'),
                self.gen)
        QtCore.QMetaObject.connectSlotsByName(self)

        for i in pkgnames:
            # I am lazy.
            self.paddname.setText(i)
            self.add()

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('Mail Request Generator'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('internet-mail'))
        self.show()

    @property
    def rtype(self):
        """Get the type of the request."""
        if self.tdel.isChecked():
            return 'del'
        elif self.tmerge.isChecked():
            return 'merge'
        elif self.torphan.isChecked():
            return 'orphan'
        else:
            return None

    def parse_list(self, *args):
        """Parse the requests list.  (formerly, it was more functional.)"""
        if self.rtype == 'merge':
            self.pkgs.setColumnCount(4)
            self.pkgs.setHorizontalHeaderLabels([_('Package'), _('Reason'),
                                                 _('Merge group'), _('Final '
                                                 'package?')])
        else:
            self.pkgs.setColumnCount(2)
            self.pkgs.setHorizontalHeaderLabels([_('Package'), _('Reason')])

        self.gen()

    def gen(self, *args):
        """Actual message generation."""
        errors = []
        out = ('Hello,\n\nI\'d like to request {} of the following package{}:'
               '\n\n{}\n\n{}\n-- \naurqt v{}')
        subj = '[{} Request] {}'
        if DS.username:
            thanks = 'Thanks in advance,\n{}'.format(DS.username)
        else:
            thanks = 'Thanks in advance!'

        if self.rtype == 'del':
            rtype = 'a removal'
            subj = subj.format('Removal', '{}')
        elif self.rtype == 'merge':
            rtype = 'a merge'
            subj = subj.format('Merge', '{}')
        elif self.rtype == 'orphan':
            rtype = 'disownment'
            subj = subj.format('Disownment', '{}')
        else:
            errors.append(_('No request type chosen.'))
            rtype = None

        requests = []
        for i, j in enumerate(self.queue):
            try:
                reason = self.pkgs.item(i, 1).text()
            except AttributeError:
                reason = '' # Cheating, I hate code repetition.
            if not reason:
                errors.append(_('No reason given for '
                              '{}.').format(j.name))
            if self.rtype == 'merge':
                try:
                    mg = int(self.pkgs.item(i, 2).text())
                except AttributeError:
                    errors.append(_('No merge group set '
                                  'for {}.').format(j.name))
                    mg = False
                except ValueError:
                    errors.append(_('Merge group for {} '
                                  'is not an integer.').format(j.name))
                    mg = False
                try:
                    mf = (self.pkgs.item(i, 3).text().lower() in ('y', 'yes',
                            '1'))
                except:
                    mf = False
            else:
                mg = 0
                mf = False
            if rtype == 'disownment':
                if not j.human:
                    errors.append(_('{} is already an '
                                  'orphan.').format(j.name))
                elif j.human == DS.username:
                    errors.append(_('{} is yours, you can'
                                  ' orphan it yourself (search for it '
                                  'in aurqt or the AUR website.)').format(
                                  j.name))

            requests.append([mg, mf, j, 'Name:   {}\nURL:    https://'
                             'aur.archlinux.org/packages/{}/\n'
                             'Reason: {}'.format(j.name, j.name, reason)])

        if errors:
            out = '<p>' + _('The following errors occured during '
                  'generation:') + '</p><ul><li>{}</li></ul>'.format(
                      '</li>\n<li>'.join(errors))
            self.subject.setText('')
            self.message.setText(out)
            return len(errors)
        else:
            es = 's'
            if len(requests) == 0:
                out = ''
                subj = ''
                es = ''
            elif len(requests) == 1:
                subj = subj.format(requests[0][2].name)
            elif len(requests) > 5:
                subj = subj.format('{} packages'.format(len(requests)))
            else:
                last = requests.pop()
                names = [i[2].name for i in requests]

                subjcont = ', '.join(names)
                subjcont += ' and {}'.format(last[2].name)
                requests.append(last)
                subj = subj.format(subjcont)

            reqgroups = {}
            for i in requests:
                mg = i[0]
                mf = i[1]
                cont = i[3]
                if mg not in reqgroups.keys():
                    reqgroups.update({mg: []})

                reqgroups.update({mg: reqgroups[mg] + [cont]})

            finalreq = ''
            if len(reqgroups) == 1:
                for i in requests:
                    finalreq = finalreq + i[3] + '\n\n'
            elif len(reqgroups) > 1:
                for g, h in reqgroups.items():
                    finalreq = finalreq + '--- GROUP {} ---\n'.format(g)
                    finalreq = finalreq + '\n'.join(h)
                    finalreq = finalreq + '\n'

            out = out.format(rtype, es, finalreq.strip(), thanks, __version__)

        self.subject.setText(subj)
        self.message.setText(out)

    def _pkginfo_helper(self, pkgname):
        """A helper function."""
        i = pkgbuilder.utils.info([pkgname])
        self._pkginfo = i

    def get_pkginfo(self, pkgname):
        """Refresh AUR information."""
        self._tt = threading.Thread(target=self._pkginfo_helper,
                                    args=(pkgname,))
        self._tt.start()

    def add(self):
        """Add the package name specified."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        pkgname = self.paddname.text()
        if not pkgname:
            QtGui.QMessageBox.critical(self, 'aurqt', _('No package '
                                       'specified.'), QtGui.QMessageBox.Ok)
        else:
            try:
                self._pkginfo = None
                pb = Qt.QProgressDialog()
                pb.setLabelText(_('Fetching package information for '
                                  '{0}…').format(pkgname))
                pb.setMaximum(0)
                pb.setValue(-1)
                pb.setWindowModality(QtCore.Qt.WindowModal)
                pb.show()
                self.get_pkginfo(pkgname)
                while self._pkginfo is None:
                    Qt.QCoreApplication.processEvents()
                pkg = self._pkginfo
                self._pkginfo = None
                del self._pkginfo
                pkg = pkgbuilder.utils.info([pkgname])[0]
            except IndexError:
                pb.close()
                QtGui.QMessageBox.critical(self, 'aurqt', _('No such package:'
                                       ' {}').format(pkgname),
                                       QtGui.QMessageBox.Ok)
            else:
                pb.close()
                self.paddname.clear()
                self.queue.append(pkg)
                self.pkgs.setRowCount(len(self.queue))
                slot = len(self.queue) - 1
                item = QtGui.QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemIsSelectable |
                              QtCore.Qt.ItemIsEnabled)
                item.setText(pkg.name)
                self.pkgs.setItem(slot, 0, item)
                self.pkgs.setItem(slot, 1, QtGui.QTableWidgetItem())
            finally:
                self.parse_list()
                self.gen()

        QtGui.QApplication.restoreOverrideCursor()

    def remove(self):
        """Remove the selected package."""
        row = self.pkgs.currentRow()
        self.pkgs.removeRow(row)
        self.queue.pop(row)
