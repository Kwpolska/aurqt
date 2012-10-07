#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.AQDS
    ~~~~~~~~~~
    aurqt Data Storage.

    :Copyright: © 2011-2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import AQError, _, __version__
import os
import logging
import configparser
import requests


### AQDS           AQ global data storage  ###
class AQDS():
    """aurqt Data Storage."""
    ### STUFF NOT TO BE CHANGED BY HUMAN BEINGS.  EVER.
    debug = False
    console = None
    sid = None
    username = None
    cookies = None  # TODO []?

    aurweburl = 'https://aur.archlinux.org/'  # TODO?

    # Creating the configuration/log stuff...
    confhome = os.getenv('XDG_CONFIG_HOME')
    if confhome is None:
        confhome = os.path.expanduser('~/.config/')

    kwdir = os.path.join(confhome, 'kwpolska')
    confdir = os.path.join(kwdir, 'aurqt')

    if not os.path.exists(confhome):
        os.mkdir(confhome)

    if not os.path.exists(kwdir):
        os.mkdir(kwdir)

    if not os.path.exists(confdir):
        os.mkdir(confdir)

    if not os.path.exists(confdir):
        print(' '.join(_('ERROR:'), _('Cannot create the configuration '
                                      'directory.')))
        print(' '.join(_('WARNING:'), _('Logs will not be created.')))

    logging.basicConfig(format='%(asctime)-15s [%(levelname)-7s] '
                        ':%(name)-10s: %(message)s',
                        filename=os.path.join(confdir, 'aurqt.log'),
                        level=logging.DEBUG)
    log = logging.getLogger('aurqt')
    log.info('*** aurqt v' + __version__)

    # TODO config

    def __init__(self):
        """Additional initialization."""
        # TODO load cookies here, if any.

    def debugmode(self, nochange=False):
        """Print all the logged messages to stderr."""
        if not self.debug:
            self.console = logging.StreamHandler()
            self.console.setLevel(logging.DEBUG)
            self.console.setFormatter(logging.Formatter('[%(levelname)-7s] '
                                      ':%(name)-10s: %(message)s'))
            logging.getLogger('').addHandler(self.console)
            self.debug = True
        elif self.debug and nochange:
            pass
        else:
            logging.getLogger('').removeHandler(self.console)
            self.debug = False

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
                r = requests.post(self.aurweburl, data={'user': username,
                                                        'passwd': password,
                                                        'remember': remember})
                c = r.cookies.get_dict()
                self.sid = c['AURSID']
                self.username = username
            except:
                raise AQError('login', 'error', _('Cannot log in (wrong '
                                                  'credentials?)'))

    def logout(self):
        """Log out of the AUR."""
        try:
            r = requests.get(self.aurweburl + 'logout.php')
            self.sid = None
            self.username = None
        except:
            raise AQError('logout', 'error', _('Cannot log out.'))
