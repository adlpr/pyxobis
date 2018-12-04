#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# xml pretty print for debug
from lxml import etree
def xmlpp(element):
    print(etree.tounicode(element, pretty_print=True))

# XOBIS element type codes.
WORK_AUT     = 'wka'
WORK_INST    = 'wki'
BEING        = 'bei'
CONCEPT      = 'cnc'
EVENT        = 'eve'
LANGUAGE     = 'lan'
OBJECT       = 'obj'
ORGANIZATION = 'org'
PLACE        = 'pla'
TIME         = 'tim'
STRING       = 'str'
RELATIONSHIP = 'rel'
HOLDINGS     = 'hol'
