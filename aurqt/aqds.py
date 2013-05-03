#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.AQDS
    ~~~~~~~~~~
    aurqt Data Storage.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import AQError, _, __version__
from .aurweb import AurWeb
from pkgbuilder import DS as PBDS
import os
import logging
import configparser
import pickle
import subprocess


### AQDS           AQ global data storage  ###
class AQDS():
    """aurqt Data Storage."""
    ### STUFF NOT TO BE CHANGED BY HUMAN BEINGS.  EVER.
    sid = None
    username = None
    w = AurWeb()

    # Creating the configuration/log stuff...
    confhome = os.getenv('XDG_CONFIG_HOME')
    if confhome is None:
        confhome = os.path.expanduser('~/.config/')

    kwdir = os.path.join(confhome, 'kwpolska')
    confdir = os.path.join(kwdir, 'aurqt')
    conffile = os.path.join(confdir, 'aurqt.cfg')
    archdir = os.path.join(confdir, 'archives')

    if not os.path.exists(confhome):
        os.mkdir(confhome)

    if not os.path.exists(kwdir):
        os.mkdir(kwdir)

    if not os.path.exists(confdir):
        os.mkdir(confdir)

    if not os.path.exists(archdir):
        os.mkdir(archdir)

    if not os.path.exists(confdir):
        print(' '.join(_('ERROR:'), _('Cannot create the configuration '
                                      'directory.')))
        exit(1)

    logging.basicConfig(format='%(asctime)-15s [%(levelname)-7s] '
                        ':%(name)-10s: %(message)s',
                        filename=os.path.join(confdir, 'aurqt.log'),
                        level=logging.DEBUG)
    log = logging.getLogger('aurqt')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)  # Don’t want the requests spam.
    console.setFormatter(logging.Formatter('[%(levelname)-7s] '
                         ':%(name)-10s: %(message)s'))
    logging.getLogger('').addHandler(console)
    log.info('*** aurqt v' + __version__)

    # Configuration.
    config = configparser.ConfigParser()
    if not config.read(conffile):
        config['aurqt'] = {}
        config['aurqt']['remember'] = 'yes'
        config['aurqt']['mail-generation'] = 'yes'

        config['helper'] = {}
        config['helper']['name'] = 'pkgbuilder'
        config['helper']['args'] = '-S'
        with open(conffile, 'w') as cfile:
            config.write(cfile)

    # Remember mode.
    sidfile = os.path.join(confdir, 'sid.pickle')
    contstate = False

    def pkginst(self, pkgs):
        """Install specified AUR packages."""
        subprocess.call('xterm -e \'{0} {1} {2}; printf '
                        '"\e[1;1m\e[1;32m==>\e[1;0m\e[1;1m Exited with $?.  '
                        'Press Enter to close."; read l\' &'.format(
                            self.config['helper']['name'],
                            self.config['helper']['args'], ' '.join(pkgs)),
                        shell=True)

    def pacman(self, args):
        """Run pacman."""
        if PBDS.hassudo:
            subprocess.call('xterm -e \'sudo {0} {1}; printf '
                            '"\e[1;1m\e[1;32m==>\e[1;0m\e[1;1m Exited with $?.'
                            '  Press Enter to close."; read l\' &'.format(
                                PBDS.paccommand, ' '.join(args)),
                            shell=True)
        else:
            subprocess.call('xterm -e \'su -c "{0} {1}"; printf '
                            '"\e[1;1m\e[1;32m==>\e[1;0m\e[1;1m Exited with $?.'
                            '  Press Enter to close."; read l\' &'.format(
                                PBDS.paccommand, ' '.join(args)),
                            shell=True)

    def continue_session(self):
        """Continue pre-existing session."""
        try:
            with open(self.sidfile, 'rb') as fh:
                login_data = pickle.load(fh)
            self.w.cookies = login_data[0]
            if self.w.loggedin:
                self.log.info('Using pre-existing login data: {}'.format(
                              [login_data[0]['AURSID'], login_data[1]]))
                self.w.sid = login_data[0]['AURSID']
                self.w.username = login_data[1]
                self.remember = True
                self.sid = login_data[0]['AURSID']
                self.username = login_data[1]
            else:
                self.log.info('Session of {} expired.'.format(login_data[1]))
                os.remove(self.sidfile)
                self.remember = False
                self.w.cookies = None
                self.w.sid = None
                self.w.username = None
                self.sid = None
                self.w.sid = None
                self.username = None
        except IOError:
            self.remember = False

        self.contstate = True

    def login(self, username, password, remember):
        """Log into the AUR."""
        if remember == 0:  # pyqt4 value conversion.
            remember = False
        elif remember == 2:
            remember = True
        if not username or not password:
            raise AQError('login', 'nodata', _('You didn’t provide the '
                                               'username or the password!'))
        else:
            try:
                self.w.login(username, password, remember)
                self.sid = self.w.sid
                self.username = self.w.username
                self.remember = remember
                with open(self.sidfile, 'wb') as fh:
                    pickle.dump([self.w.cookies, self.w.username], fh)
            except NotImplementedError: # WTF?! TODO
                raise AQError('login', 'error', _('Cannot log in (wrong '
                                                  'credentials?)'))

    def logout(self):
        """Log out of the AUR."""
        try:
            self.w.logout()
            self.sid = None
            self.username = None
            if self.remember:
                self.remember = False
                os.remove(self.sidfile)
        except:
            raise AQError('logout', 'error', _('Cannot log out.'))
