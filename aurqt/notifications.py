#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.notifications
    ~~~~~~~~~~~~~~~~~~~
    Notifications for aurqt.

    :Copyright: © 2011-2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import AQError, DS
import pickle
import pkgbuilder.aur

def get(dryrun=False):
    """Get all the notifications."""
    if DS.username:
        try:
            with open(DS.archdir + DS.username + '.pickle', 'rb') as fh:
                old = pickle.load(fh).sort()
        except IOError:
            new = pkgbuilder.aur.AUR().request('msearch', DS.username).sort()
            notify = [{'nodata': DS.username}]
        else:
            new = pkgbuilder.aur.AUR().request('msearch', DS.username).sort()
            notify = []

            while len(old) != len(new):
                for i, j in zip(enumerate(old), new):
                    if i[1]['Name'] != j['Name']:
                        notify.append({j['Name']: [0, DS.username]})
                        old.append(i[1])
                        old.sort()
                        break

            for i, j in zip(old, new):
                    if i['OutOFDate'] != j['OutOfDate']:
                        notify.append({i['Name']: [1, j['OutOfDate']]})
        finally:
            if not dryrun:
                with open(DS.archdir + DS.username + '.pickle', 'wb') as fh:
                    pickle.dump(new, fh)

            return {'nodata': DS.username}
    else:
        raise AQError('notify', 'nologin', 'Not logged in.')
