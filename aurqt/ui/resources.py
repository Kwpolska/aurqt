# -*- coding: utf-8 -*-

# Resource object code
#
# Created: Sun May 26 21:04:32 2013
#      by: The Resource Compiler for PyQt (Qt v4.8.4)
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore

qt_resource_data = b"\
\x00\x00\x00\x5e\
\x3c\
\xb8\x64\x18\xca\xef\x9c\x95\xcd\x21\x1c\xbf\x60\xa1\xbd\xdd\x42\
\x00\x00\x00\x08\x04\xa7\x74\x5a\x00\x00\x00\x00\x69\x00\x00\x00\
\x2d\x03\x00\x00\x00\x0a\x00\x42\x01\x41\x01\x04\x00\x44\x00\x3a\
\x08\x00\x00\x00\x00\x06\x00\x00\x00\x06\x45\x52\x52\x4f\x52\x3a\
\x07\x00\x00\x00\x08\x40\x64\x65\x66\x61\x75\x6c\x74\x01\x88\x00\
\x00\x00\x0a\x01\x01\xff\x14\x02\x04\xfd\x2c\x0a\x13\
"

qt_resource_name = b"\
\x00\x06\
\x07\x35\x98\x25\
\x00\x6c\
\x00\x6f\x00\x63\x00\x61\x00\x6c\x00\x65\
\x00\x02\
\x00\x00\x07\x6c\
\x00\x70\
\x00\x6c\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x12\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()