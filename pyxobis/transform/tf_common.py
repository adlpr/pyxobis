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


# concatenate subfields where strict subfield preservation desirable
# couldn't use \x1f (actual subf separator) due to "XML compatibility"
def concat_subfs(field, with_codes=True):
    if with_codes:
        return ' '.join('‡{} {}'.format(code, val) for code, val in zip(field.subfields[::2],field.subfields[1::2]))
    return ' '.join(field.subfields[1::2])
