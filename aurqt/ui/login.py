#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.2.2
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

from . import tr
from .. import DS, AQError
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
        unamelabel = QtGui.QLabel(tr('Username'), self)
        pwdlabel = QtGui.QLabel(tr('Password'), self)

        self.uname = QtGui.QLineEdit(self)
        self.pwd = QtGui.QLineEdit(self)
        self.pwd.setEchoMode(QtGui.QLineEdit.Password)
        self.remember = QtGui.QCheckBox(tr('Remember me'), self)
        self.remember.setCheckState(2)

        forgot = QtGui.QPushButton(tr('Forgot password'), self)
        register = QtGui.QPushButton(tr('Register'), self)

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
        self.setWindowTitle(tr('Log in'))
        self.setWindowIcon(QtGui.QIcon.fromTheme('user-identity'))
        self.show()

    def _login(self, *args):
        """Logging in in the background."""
        try:
            DS.login(*args)
        except AQError as e:
            DS.log.exception(e)
            self._loginstatus = ('AQError', e.msg)
        except Exception as e:
            DS.log.exception(e)
            self._loginstatus = ('Exception', e)
        else:
            self._loginstatus = (True,)

    def login(self):
        """Log into the AUR."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        try:
            pb = Qt.QProgressDialog()
            pb.setLabelText(tr('Logging in...'))
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
            if self._loginstatus[0] == 'AQError':
                Qt.QCoreApplication.processEvents()
                QtGui.QMessageBox.critical(self, tr('Login failed.'),
                                           self._loginstatus[1],
                                           QtGui.QMessageBox.Ok)
            elif self._loginstatus[0] == 'Exception':
                Qt.QCoreApplication.processEvents()
                QtGui.QMessageBox.critical(self, 'aurqt',
                                           tr('Something went wrong.\nError '
                                              'message: {}').format(
                                                   self._loginstatus[1]),
                                           QtGui.QMessageBox.Ok)

            del self._loginstatus

            self.accept()
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def forgot(self):
        """Show the forgot password form."""
        email, ok = QtGui.QInputDialog.getText(self, tr('Forgot password'),
                                               tr('Mail Address'))
        if ok:
            if not email:
                r = QtGui.QMessageBox.critical(self, tr('Forgot password'),
                                               tr('Please enter an address.'),
                                               QtGui.QMessageBox.Ok,
                                               QtGui.QMessageBox.Cancel)
                if r == QtGui.QMessageBox.Ok:
                    self.forgot()
            else:
                try:
                    r = requests.post(DS.aurweburl + 'passreset/',
                                      data={'email': email})
                    r.raise_for_status()
                    QtGui.QMessageBox.information(self, tr('Forgot password'),
                                                  tr('Check your mailbox.'),
                                                  QtGui.QMessageBox.Ok)
                except:
                    QtGui.QMessageBox.critical(self, tr('Forgot password'),
                                               tr('Request failed.  Check '
                                                 'your Internet connection.'),
                                               QtGui.QMessageBox.Ok)

    def register(self):
        """Show the registration form."""
        r = AccountDialog(self)
        r.exec_()
