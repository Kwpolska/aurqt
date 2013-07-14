#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.2.2
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.account
    ~~~~~~~~~~~~~~~~
    The Account modification/registration dialog for aurqt.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import tr
from .. import DS, AQError
from PyQt4 import Qt, QtGui, QtCore


class AccountDialog(QtGui.QDialog):
    """The Account modification/registration dialog for aurqt."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(AccountDialog, self).__init__(parent)

        lay = QtGui.QFormLayout()

        self.register = DS.sid is None
        self.uid = None

        # TRANSLATORS: see aurweb.
        labels = [tr('Username'), tr('Mail Address'), tr('Password'),
                  tr('Re-type password'), tr('Real Name'), tr('IRC Nick'),
                  tr('PGP Key Fingerprint')]

        for i, j in enumerate(labels):
            lay.setWidget(i, QtGui.QFormLayout.LabelRole, QtGui.QLabel(j,
                                                                       self))

        self.username = QtGui.QLineEdit(self)
        self.mail = QtGui.QLineEdit(self)
        self.pwd = QtGui.QLineEdit(self)
        self.pwd2 = QtGui.QLineEdit(self)
        self.rname = QtGui.QLineEdit(self)
        self.irc = QtGui.QLineEdit(self)
        self.pgp = QtGui.QLineEdit(self)
        self.pgp.setToolTip(tr('gpg --fingerprint (40 characters long).'))

        lay.setWidget(0, QtGui.QFormLayout.FieldRole, self.username)
        lay.setWidget(1, QtGui.QFormLayout.FieldRole, self.mail)
        lay.setWidget(2, QtGui.QFormLayout.FieldRole, self.pwd)
        lay.setWidget(3, QtGui.QFormLayout.FieldRole, self.pwd2)
        lay.setWidget(4, QtGui.QFormLayout.FieldRole, self.rname)
        lay.setWidget(5, QtGui.QFormLayout.FieldRole, self.irc)
        lay.setWidget(6, QtGui.QFormLayout.FieldRole, self.pgp)

        self.pwd.setEchoMode(QtGui.QLineEdit.Password)
        self.pwd2.setEchoMode(QtGui.QLineEdit.Password)

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Save |
                               QtGui.QDialogButtonBox.Cancel)

        baselay = QtGui.QVBoxLayout(self)
        baselay.addLayout(lay)
        baselay.addWidget(btn)

        QtCore.QObject.connect(btn, QtCore.SIGNAL('accepted()'), self.save)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)

        if self.register:
            self.rtype = 'NewAccount'
            self.setWindowTitle(tr('Register'))
            self.setWindowIcon(QtGui.QIcon.fromTheme('user-group-new'))
        else:
            self.rtype = 'UpdateAccount'
            self.load()
            self.setWindowTitle(tr('Account settings'))
            self.setWindowIcon(QtGui.QIcon.fromTheme('user-group-properties'))

        QtGui.QApplication.restoreOverrideCursor()
        self.show()

    def load(self):
        """Load data from the aurweb."""
        try:
            data = DS.w.get_account_data()
        except:
            QtGui.QMessageBox.critical(self, tr('Account settings') +
                                       ' -- aurqt', tr('Something went wrong.'
                                       '  Cannot make a request to the AUR.'
                                       '  Try again.'), QtGui.QMessageBox.Ok)
            QtGui.QApplication.restoreOverrideCursor()
            self.reject()
        else:
            self.uid = data['id']
            self.username.setText(data['username'])
            self.mail.setText(data['mail'])
            self.rname.setText(data['rname'])
            self.irc.setText(data['irc'])
            self.pgp.setText(data['pgp'])

    def save(self):
        """Save the form."""
        # Sanity checks.
        if not self.uid and self.register:
            QtGui.QMessageBox.critical(self, tr('Account settings') +
                                       ' -- aurqt', tr('Something went '
                                       'wrong.'), QtGui.QMessageBox.Ok)
            self.reject()

        username = self.username.text()
        pwd = self.pwd.text()
        pwd2 = self.pwd2.text()
        mail = self.mail.text()
        rname = self.rname.text()
        irc = self.irc.text()
        pgp = self.pgp.text()
        if pwd != pwd2:
            QtGui.QMessageBox.critical(self, 'aurqt', tr('Passwords differ.'),
                                       QtGui.QMessageBox.Ok)
        elif not username:
            QtGui.QMessageBox.critical(self, 'aurqt', tr('Username is empty.'),
                                       QtGui.QMessageBox.Ok)
        elif not mail:
            QtGui.QMessageBox.critical(self, 'aurqt', tr('Mail address is '
                                       'empty.'), QtGui.QMessageBox.Ok)
        else:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                                 QtCore.Qt.WaitCursor))
            try:
                e = DS.w.account_edit(self.rtype, username, pwd, mail, rname,
                                      irc, pgp)
                QtGui.QMessageBox.information(self, 'aurqt', e.strip(),
                                              QtGui.QMessageBox.Ok)
            except AQError as e:
                QtGui.QMessageBox.critical(self, 'aurqt', e.msg,
                                           QtGui.QMessageBox.Ok)
            else:
                self.accept()
            finally:
                QtGui.QApplication.restoreOverrideCursor()
