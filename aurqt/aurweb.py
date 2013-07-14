#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.2.2
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

from . import AQError
import requests
import bs4

tr = lambda x: x

class AurWeb():
    """Access the aurweb."""
    session = requests.Session()
    sid = None
    username = None
    url = 'https://aur.archlinux.org/'

    def new_session(self):
        """Create a new session."""
        self.session = requests.Session()

    def login(self, username, password, remember):
        """Log into the AUR."""
        r = self.session.post(self.url + 'login', data={'user': username,
                                                        'passwd': password,
                                                        'remember': remember})
        r.raise_for_status()
        if 'AURSID' in self.session.cookies:
            self.sid = self.session.cookies['AURSID']
            self.username = username
        else:
            raise AQError('auth', 'auth', tr('Could not log into the AUR.'))

    def logout(self):
        """Log out of the AUR."""
        r = self.session.get(self.url + 'logout/')
        r.raise_for_status()
        self.new_session()
        self.sid = None
        self.username = None

    @property
    def loggedin(self):
        """Is anyone logged in?"""
        if not self.session.cookies:
            return False

        r = self.session.get(self.url)
        r.raise_for_status()
        if 'logout' in r.text:
            return True
        else:
            return False

    def get_account_data(self):
        r = self.session.get(self.url + 'account/' + self.username + '/edit/')
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
        if self.session.cookies:
            lang = self.session.cookies['AURLANG']
        else:
            lang = 'en'

        data = {'U': username, 'P': password, 'C': password, 'E': mail,
                'R': rname, 'I': irc, 'L': lang, 'K': pgp, 'Action': rtype}

        if rtype == 'UpdateAccount':
            data.update({'ID': self.get_account_data()['id'],
                         'token': self.sid})
            aurl = self.url + 'account/{0}/update/'.format(username)
        else:
            aurl = self.url + 'register/'

        r = self.session.post(aurl, data=data)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        body = soup.find(class_='box')
        error = body.find(class_='error')
        if error:
            error = error.prettify()
            if 'PGP' in error:
                error += '<p>%s' % tr('<strong>Hint:</strong> use gpg '
                                      '--fingerprint')

            raise AQError('aurweb', 'accedit', error)
        else:
            return body.prettify()

    def upload(self, filename, category):
        """Upload a file."""
        r = self.session.post(self.url + 'submit/',
                              data={'pkgsubmit': 1, 'token': self.sid,
                                    'category': category},
                              files={'pfile': open(filename, 'rb')})
        r.raise_for_status()

        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        if r.url.startswith('https://aur.archlinux.org/packages/'):
            return [True, r.url[35:-1]]
        else:
            return [False, soup.find(class_='pkgoutput').string]

    def fetchpkg(self, pkg):
        """Fetch the aurweb page for a package."""
        url = self.url + 'packages/{0}/?comments=all'.format(pkg.name)
        r = self.session.get(url)
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

        url = self.url + 'packages/{0}/?comments=all'.format(pkg.name)

        data = {'token': self.sid, 'ID': pkg.id}
        if action == 'category':
            data.update({'action': 'do_ChangeCategory', 'category_id': params})
            r = self.session.post(url, data=data)
        elif action == 'comment':
            data.update({'comment': params})
            r = self.session.post(url, data=data)
        elif action in urlactions.keys():
            url = self.url + 'packages/{0}/{1}/?comments=all'.format(
                pkg.name, urlactions[action])
            r = self.session.get(url)
        elif action in formactions.keys():
            data.update({formactions[action]: 'aurqt',
                         'IDs[{0}]'.format(pkg.id): '1'})
            r = self.session.post(url, data=data)
        else:
            raise AQError('aurweb', 'pkgaction', 'unknown action type')

        return bs4.BeautifulSoup(r.text, 'html.parser')
