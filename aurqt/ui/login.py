#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.1
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.loginform
    ~~~~~~~~~~~~~~~~~~
    The aurqt login form.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import DS, AQError, _
from .account import AccountDialog
from PyQt4 import Qt, QtGui, QtCore
import requests
import threading


class LoginForm(QtGui.QDialog):
    """The aurqt login form."""
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super(LoginForm, self).__init__(parent)

        lay = QtGui.QGridLayout(self)
        unamelabel = QtGui.QLabel(_('Username'), self)
        pwdlabel = QtGui.QLabel(_('Password'), self)

        self.uname = QtGui.QLineEdit(self)
        self.pwd = QtGui.QLineEdit(self)
        self.pwd.setEchoMode(QtGui.QLineEdit.Password)
        self.remember = QtGui.QCheckBox(_('Remember me'), self)
        self.remember.setCheckState(2)

        if DS.config['aurqt']['remember'] == 'no':
            self.remember.setEnabled(False)

        forgot = QtGui.QPushButton(_('Forgot password'), self)
        register = QtGui.QPushButton(_('Register'), self)

        btn = QtGui.QDialogButtonBox(self)
        btn.setStandardButtons(QtGui.QDialogButtonBox.Ok |
                               QtGui.QDialogButtonBox.Cancel)

        lay.addWidget(unamelabel, 0, 0, 1, 1)
        lay.addWidget(pwdlabel, 1, 0, 1, 1)
        lay.addWidget(self.uname, 0, 1, 1, 1)
        lay.addWidget(self.pwd, 1, 1, 1, 1)
        lay.addWidget(self.remember, 2, 0, 1, 2)
        lay.addWidget(forgot, 3, 0, 1, 1)
        lay.addWidget(register, 3, 1, 1, 1)
        lay.addWidget(btn, 4, 0, 1, 2)

        QtCore.QObject.connect(forgot, QtCore.SIGNAL('clicked()'),
                               self.forgot)
        QtCore.QObject.connect(register, QtCore.SIGNAL('clicked()'),
                               self.register)

        QtCore.QObject.connect(btn, QtCore.SIGNAL('accepted()'), self.login)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('rejected()'), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowModality(Qt.Qt.ApplicationModal)
        self.setWindowTitle(_('Log in'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('user-identity'))
        self.show()

    def _login(self, *args):
        """Logging in in the background."""
        try:
            DS.login(*args)
        except AQError as e:
            Qt.QCoreApplication.processEvents()
            QtGui.QMessageBox.critical(self, _('Cannot log in (wrong '
                                               'credentials?)'),
                                       e.msg, QtGui.QMessageBox.Ok)
        except Exception as e:
            Qt.QCoreApplication.processEvents()
            DS.log.exception(e)
            QtGui.QMessageBox.critical(self, 'aurqt',
                                       _('Something went wrong.\nError '
                                         'message: {}').format(e),
                                       QtGui.QMessageBox.Ok)

    def login(self):
        """Log into the AUR."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        try:
            pb = Qt.QProgressDialog()
            pb.setLabelText(_('Logging in…'))
            pb.setMaximum(0)
            pb.setValue(-1)
            pb.setWindowModality(QtCore.Qt.WindowModal)
            pb.show()
            _tt = threading.Thread(target=self._login,
                                   args=(self.uname.text(), self.pwd.text(),
                                         self.remember.checkState()))
            _tt.start()
            while _tt.is_alive():
                Qt.QCoreApplication.processEvents()

            pb.close()
            self.accept()
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def forgot(self):
        """Show the forgot password form."""
        email, ok = QtGui.QInputDialog.getText(self, _('Forgot password'),
                                               _('Mail address:'))
        if ok:
            if not email:
                r = QtGui.QMessageBox.critical(self, _('Forgot password'),
                                               _('Please enter an address.'),
                                               QtGui.QMessageBox.Ok,
                                               QtGui.QMessageBox.Cancel)
                if r == QtGui.QMessageBox.Ok:
                    self.forgot()
            else:
                try:
                    r = requests.post(DS.aurweburl + 'passreset/',
                                      data={'email': email})
                    r.raise_for_status()
                    QtGui.QMessageBox.information(self, _('Forgot password'),
                                                  _('Check your mailbox.'),
                                                  QtGui.QMessageBox.Ok)
                except:
                    QtGui.QMessageBox.critical(self, _('Forgot password'),
                                               _('Request failed.  Check '
                                                 'your Internet connection.'),
                                               QtGui.QMessageBox.Ok)

    def register(self):
        """Show the registration form."""
        r = AccountDialog(self)
        r.exec_()
