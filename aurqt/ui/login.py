#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.999
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.ui.loginform
    ~~~~~~~~~~~~~~~~~~
    The aurqt login form.

    :Copyright: © 2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from .. import DS, AQError, _
from .account import AccountDialog
from PyQt4 import Qt, QtGui, QtCore
import requests


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

    def login(self):
        """Log into the AUR."""
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(
                                             QtCore.Qt.WaitCursor))
        try:
            DS.login(self.uname.text(), self.pwd.text(),
                     self.remember.checkState())
            self.accept()
        except AQError as e:
            QtGui.QMessageBox.critical(self, _('Cannot log in (wrong '
                                               'credentials?)'),
                                       e.msg, QtGui.QMessageBox.Ok)
        except Exception as e:
            DS.log.exception(e)
            QtGui.QMessageBox.critical(self, 'aurqt',
                                       _('Something went wrong.\nError '
                                         'message: {}').format(e),
                                       QtGui.QMessageBox.Ok)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def forgot(self):
        """Show the forgot password form."""
        email, ok = QtGui.QInputDialog.getText(self, _('Forgot password'),
                                               _('E-mail address:'))
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
                    r = requests.post(DS.aurweburl + 'passreset.php',
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
