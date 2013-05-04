#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# aurqt v0.1.1
# A graphical AUR manager.
# Copyright © 2012-2013, Kwpolska.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the author of this software nor the names of
#    contributors to this software may be used to endorse or promote
#    products derived from this software without specific prior written
#    consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
    aurqt
    ~~~~~

    A graphical AUR manager.

    :Copyright: © 2012-2013, Kwpolska.
    :License: BSD (see /LICENSE).
"""

__title__ = 'aurqt'
__version__ = '0.1.1'
__author__ = 'Kwpolska'
__license__ = '3-clause BSD'
__docformat__ = 'restructuredtext en'

# import gettext
#
# G = gettext.translation('aurqt', '/usr/share/locale', fallback='C')
_ = lambda x: x


### AQError         errors raised here      ###
class AQError(Exception):
    """Exceptions raised by aurqt."""

    def __init__(self, src, inf, msg):
        """PBError init."""
        DS.log.error('(auto AQError) ' + '/'.join([src, inf, msg]))
        self.src = src
        self.inf = inf
        self.msg = msg

    def __str__(self):
        """You want to see error messages, don’t you?"""
        return self.msg

from .aqds import AQDS
DS = AQDS()

# It’s here to get logging right.  If it was on the top, all the logs from
# aurqt would go over to pkgbuilder.  Now, it’s the other way around.
import pkgbuilder
__pbversion__ = pkgbuilder.__version__
DS.log.info('*** PKGBUILDer v{}'.format(__pbversion__))
