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

from . import AQError
import requests
import re # Sorry!
import lxml.html

### AurWeb         Access the aurweb       ###
class AurWeb():
    """Access the aurweb."""
    url = 'https://aur.archlinux.org/'
    sid = None

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

    @property
    def loggedin(self):
        """Is anyone logged in?"""
        if not sid:
            return False

        cookies = {'AURSID': self.sid}

        r = requests.get(self.url, cookies=cookies)
        if re.search('logout', r.text):  # Need to do that, sorry!
            return True
        else:
            return False

    def get_account_data(self):
        cookies = {'AURSID': self.sid}
        r = requests.get(self.url + 'account.php', cookies=cookies)
        if re.search('logout', r.text):
            root = lxml.html.document_fromstring(r.text)
            form = root.find_class('pgboxbody')[0].forms[0]
            v = form.form_values()
            return {'id': v['ID'], 'username': v['U'], 'mail': v['M'],
                    'rname': v['R'], 'irc': v['I']}
        else:
            return {'id': '', 'username': '', 'mail': '', 'rname': '',
                    'irc': ''}

        def account_edit(self, rtype, username, password, mail, rname='',
                         irc=''):
        """Modify/add an account."""
        cookies = {'AURSID': self.sid}
        data = {'U': username, 'P': password, 'C': password, 'E': mail, 'R':
                rname, 'I': irc, 'L': 'en', 'Action': rtype}
        if rtype == 'UpdateAccount':
            data.update({'ID': self.get_account_data(), 'token': self.sid})

        r = requests.post(self.url, data=data, cookies=cookies)
        root = lxml.html.document_fromstring(r.text)
        body = root.find_class('pgboxbody')[0]
        error = body.find_class('error')
        if error:
            raise AQError('aurweb', 'accedit', error[0].text_content())
        else:
            return body.text_content()
