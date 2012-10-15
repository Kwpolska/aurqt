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
        r.raise_for_status()
        c = r.cookies.get_dict()
        return [c['AURSID'], username]

    def logout(self):
        """Log out of the AUR."""
        r = requests.get(self.url + 'logout.php')
        r.raise_for_status()

    @property
    def loggedin(self):
        """Is anyone logged in?"""
        if not self.sid:
            return False

        cookies = {'AURSID': self.sid}

        r = requests.get(self.url, cookies=cookies)
        r.raise_for_status()
        if logout in r.text:
            return True
        else:
            return False

    def get_account_data(self):
        cookies = {'AURSID': self.sid}
        r = requests.get(self.url + 'account.php', cookies=cookies)
        r.raise_for_status()
        if 'logout' in r.text:
            root = lxml.html.document_fromstring(str(r.content))
            form = root.find_class('pgboxbody')[0].forms[0]
            v = form.form_values()
            # v = {i[0]: i[1] for i in v} — TODO, see:
            # https://bugs.launchpad.net/lxml/+bug/1067004
            v = {i[0].strip('\\\''): i[1].strip('\\\'') for i in v}
            # But this is still wrong for fields containing spaces,
            # as envisioned in the bug report linked above.
            return {'id': v['ID'], 'username': v['U'], 'mail': v['E'],
                    'rname': v['R'], 'irc': v['I']}
        else:
            return {'id': '', 'username': '', 'mail': '', 'rname': '',
                    'irc': ''}

    def account_edit(self, rtype, username, password, mail, rname='',
                     irc=''):
        """Modify/add an account."""
        cookies = {'AURSID': self.sid}
        data = {'U': username, 'P': password, 'C': password, 'E': mail,
                'R': rname, 'I': irc, 'L': 'en', 'Action': rtype}

        if rtype == 'UpdateAccount':
            data.update({'ID': self.get_account_data()['id'],
                         'token': self.sid})

        r = requests.post(self.url + 'account.php', data=data, cookies=cookies)
        r.raise_for_status()
        root = lxml.html.document_fromstring(str(r.content))
        body = root.find_class('pgboxbody')[0]
        error = body.find_class('error')
        if error:
            raise AQError('aurweb', 'accedit', error[0].text_content())
        else:
            return body.text_content()
