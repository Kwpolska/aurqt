#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.aurweb
    ~~~~~~~~~~~~
    Access the aurweb.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import AQError, _
import requests
import bs4


### AurWeb         Access the aurweb       ###
class AurWeb():
    """Access the aurweb."""
    cookies = None
    sid = None
    username = None
    url = 'https://aur.archlinux.org/'

    def login(self, username, password, remember):
        """Log into the AUR."""
        r = requests.post(self.url + 'login', data={'user': username,
                                                    'passwd': password,
                                                    'remember': remember})
        r.raise_for_status()
        if 'AURSID' in r.cookies:
            self.cookies = r.cookies
            self.sid = r.cookies['AURSID']
            self.username = username
        else:
            raise AQError('auth', 'auth', _('Could not log into the AUR.'))

    def logout(self):
        """Log out of the AUR."""
        r = requests.get(self.url + 'logout/')
        r.raise_for_status()
        self.cookies = None
        self.sid = None
        self.username = None

    @property
    def loggedin(self):
        """Is anyone logged in?"""
        if not self.cookies:
            return False

        r = requests.get(self.url, cookies=self.cookies)
        r.raise_for_status()
        if 'logout' in r.text:
            return True
        else:
            return False

    def get_account_data(self):
        r = requests.get(self.url + 'account/{}/edit/'.format(self.username),
                         cookies=self.cookies)
        r.raise_for_status()
        if 'logout' in r.text:
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            form = soup.find(class_='box').find('form')
            v = {}
            for i in form.find_all('input'):
                if i['type'] in ['text', 'hidden']:
                    v.update({i['name']: i['value']})
            return {'id': v['ID'], 'username': v['U'], 'mail': v['E'],
                    'rname': v['R'], 'irc': v['I'], 'pgp': v['K']}
        else:
            return {'id': '', 'username': '', 'mail': '', 'rname': '',
                    'irc': '', 'pgp': ''}

    def account_edit(self, rtype, username, password, mail, rname='',
                     irc='', pgp=''):
        """Modify/add an account."""
        if self.cookies:
            lang = self.cookies['AURLANG']
        else:
            lang = 'en'

        data = {'U': username, 'P': password, 'C': password, 'E': mail,
                'R': rname, 'I': irc, 'L': lang, 'K': pgp, 'Action': rtype}

        if rtype == 'UpdateAccount':
            data.update({'ID': self.get_account_data()['id'],
                         'token': self.sid})
            aurl = self.url + 'account/{}/update/'.format(username)
        else:
            aurl = self.url + 'register/'

        r = requests.post(aurl,  data=data, cookies=self.cookies)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        body = soup.find(class_='box')
        error = body.find(class_='error')
        if error:
            error = error.prettify()
            if 'PGP' in error:
                error += '<p><strong>{}</strong> {}'.format(
                    _('Hint:'), 'gpg --fingerprint')

            raise AQError('aurweb', 'accedit', error)
        else:
            return body.prettify()

    def upload(self, filename, category):
        """Upload a file."""
        r = requests.post(self.url + 'submit/', cookies=self.cookies,
                          data={'pkgsubmit': 1, 'token': self.sid,
                                'category': category},
                          files={'pfile': open(filename, 'rb')})
        r.raise_for_status()

        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        if r.url.startswith('https://aur.archlinux.org/packages/'):
            return [True, r.url[35:-1]]
        else:
            return [False, soup.find(class_='pkgoutput').string]

    def fetchpkg(self, pkgid):
        """Fetch the aurweb page for a package."""
        url = self.url + 'packages.php?ID={}&comments=all'.format(pkgid)
        r = requests.get(url, cookies=self.cookies)
        return bs4.BeautifulSoup(r.text, 'html.parser')

    def fetchcomments(self, soup):
        """Fetch the comments."""
        cbox = soup.find_all(id='news')
        if cbox:
            return cbox[0]
        else:
            return None

    def pkgaction(self, pkg, action, params=None):
        """
        Perform an action related to the AUR packages.

        Valid actions are: category, comment, ±vote, ±notify, ±flag, ±own.
        """

        urlactions = {'+vote': 'vote', '-vote': 'unvote', '+notify':
                'notify', '-notify': 'unnotify', '+flag': 'flag',
                '-flag': 'unflag'}
        formactions = {'+own': 'do_Adopt', '-own': 'do_Disown'}

        url = self.url + 'packages/{}/?comments=all'.format(pkg['Name'])

        data = {'token': self.sid, 'ID': pkg['ID']}
        if action == 'category':
            data.update({'action': 'do_ChangeCategory', 'category_id': params})
            r = requests.post(url, cookies=self.cookies, data=data)
        elif action == 'comment':
            data.update({'comment': params})
            r = requests.post(url, cookies=self.cookies, data=data)
        elif action in urlactions.keys():
            url = self.url + 'packages/{}/{}/?comments=all'.format(
                    pkg['Name'], urlactions[action])
            r = requests.get(url, cookies=self.cookies)
        elif action in formactions.keys():
            data.update({formactions[action]: 'aurqt',
                         'IDs[{}]'.format(pkg['ID']): '1'})
            r = requests.post(url, cookies=self.cookies, data=data)
        else:
            raise AQError('aurweb', 'pkgaction', 'unknown action type')

        return bs4.BeautifulSoup(r.text, 'html.parser')
