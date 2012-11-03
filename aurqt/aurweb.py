#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.0.99
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
import bs4
import re  # IT IS NOT FOR HTML PARSING!


### AurWeb         Access the aurweb       ###
class AurWeb():
    """Access the aurweb."""
    url = 'https://aur.archlinux.org/'
    sid = None
    cookies = None

    def login(self, username, password, remember):
        """Log into the AUR."""
        r = requests.post(self.url, data={'user': username,
                                          'passwd': password,
                                          'remember': remember})
        r.raise_for_status()
        c = r.cookies
        return [c, username]

    def logout(self):
        """Log out of the AUR."""
        r = requests.get(self.url + 'logout.php')
        r.raise_for_status()

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
        r = requests.get(self.url + 'account.php', cookies=self.cookies)
        r.raise_for_status()
        if 'logout' in r.text:
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            form = soup.find(class_='pgboxbody').find('form')
            v = {}
            for i in form.find_all('input'):
                if i['type'] in ['text', 'hidden']:
                    v.update({i['name']: i['value']})
            return {'id': v['ID'], 'username': v['U'], 'mail': v['E'],
                    'rname': v['R'], 'irc': v['I']}
        else:
            return {'id': '', 'username': '', 'mail': '', 'rname': '',
                    'irc': ''}

    def account_edit(self, rtype, username, password, mail, rname='',
                     irc=''):
        """Modify/add an account."""
        data = {'U': username, 'P': password, 'C': password, 'E': mail,
                'R': rname, 'I': irc, 'L': 'en', 'Action': rtype}

        if rtype == 'UpdateAccount':
            data.update({'ID': self.get_account_data()['id'],
                         'token': self.sid})

        r = requests.post(self.url + 'account.php', data=data,
                          cookies=self.cookies)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        body = soup.find(class_='pgboxbody')
        error = body.find(class_='error')
        if error:
            raise AQError('aurweb', 'accedit', error)
        else:
            return body.prettify()

    def upload(self, filename, category):
        """Upload a file."""
        r = requests.post(self.url + 'pkgsubmit.php', cookies=self.cookies,
                          data={'pkgsubmit': 1, 'token': self.sid,
                                'category': category},
                          files={'pfile': open(filename, 'rb')})
        r.raise_for_status()

        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        if r.url.startswith('https://aur.archlinux.org/packages.php'):
            title = soup.head.title
            match = re.match('AUR \(.*\) - ', title.string)
            # see?  That is what re is used for over here.  I am not an idiot
            # and I do not do HTML parsing with regexps.  And you do know the
            # StackOverflow HTML parsing post, right?  http://kwpl.tk/WAlq5b
            pkgname = title.string[match.endpos:]
            print(pkgname)
            # Although I do understand that it is a cheat, but this is the best
            # method to do this.  AUR does not allow for info-by-pkgid and this
            # part of the code is not bothering with webscraping it from the
            # page contents.
            return [True, pkgname]
        else:
            return [False, soup.find(class_='pkgoutput').string]

    def fetchpkg(self, pkgid):
        """Fetch the aurweb page for a package."""
        url = self.url + 'packages.php?ID={}&comments=all'.format(pkgid)
        r = requests.get(url, cookies=self.cookies)
        return bs4.BeautifulSoup(r.text, 'html.parser')

    def fetchcomments(self, soup):
        """Fetch the comments."""
        cbox = soup.find_all(class_='pgbox')[-2]
        if cbox.find_all(class_='comment-header'):
            return cbox
        else:
            return None

    def pkgaction(self, pkgid, action, params=None):
        """
        Perform an action related to the AUR packages.

        Valid actions are: category, comment, ±vote, ±notify, ±flag, ±own.
        """

        actions = {'+vote': 'do_Vote', '-vote': 'do_UnVote', '+notify':
                'do_Notify', '-notify': 'do_UnNotify', '+ood': 'do_Flag',
                '-flag': 'do_UnFlag', '+flag': 'do_Adopt',
                '-own': 'do_Disown'}

        url = self.url + 'packages.php?ID={}&comments=all'.format(pkgid)

        data = {'token': self.sid, 'ID': pkgid}
        if action == 'category':
            data.update({'action': 'do_ChangeCategory', 'category_id': params})
        elif action == 'comment':
            data.update({'comment': params})
        elif action in actions.keys():
            data.update({actions[action]: 'aurqtRocksButItsDeveloperIsLazy'})
            data.update({'IDs[{}]'.format(pkgid): '1'})
        else:
            raise AQError('aurweb', 'pkgaction', 'unknown action type')

        r = requests.post(url, cookies=self.cookies, data=data)
        return bs4.BeautifulSoup(r.text, 'html.parser')
