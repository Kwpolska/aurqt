#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.0
# INSERT TAGLINE HERE.
# Copyright © 2012, Kwpolska.
# See /LICENSE for licensing information.

"""
    aurqt.upgrade
    ~~~~~~~~~~~~~
    aurqt upgrade magic.

    :Copyright: © 2011-2012, Kwpolska.
    :License: BSD (see /LICENSE).
"""

from . import AQError, _, __version__
import pkgbuilder.upgrade


### Upgrade        upgrade magic           ###
class Upgrade():
    """aurqt upgrade magic."""
    u = pkgbuilder.upgrade.Upgrade()
    def list(self):
        return self.u.list_upgradable(self.u.gather_foreign_pkgs())
