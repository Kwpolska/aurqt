#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.aurweb
    ~~~~~~~~~~~~
    Access the aurweb.

    :Copyright: © 2011-2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

#from . import DS
#AQError, _, __version__
import requests
import re # Sorry!

### aurweb         Access the aurweb       ###
class aurweb():
    """Access the aurweb."""
    url = 'https://aur.archlinux.org/' #TODO

    def login(self, username, password, remember):
        """Log into the AUR."""
        r = requests.post(self.url, data={'user': username,
                                          'passwd': password,
                                          'remember': remember})
        c = r.cookies.get_dict()
        return [c['AURSID'], username]

    def logout(self):
        """Log out of the AUR."""
        requests.get(self.url + 'logout.php')

    def loggedin(self, sid):
        """Is anyone logged in?"""
        cookies = {'AURSID': sid}

        r = requests.get(self.url, cookies=cookies)
        if re.search('logout', r.text):  # Need to do that, sorry!
            return True
        else:
            return False
