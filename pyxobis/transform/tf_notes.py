#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pymarc import Field
from pyxobis.builders import *
from .tf_common import *


NOTE_FIELDS = [
    '500','502','504','505'
]

def transform_notes(self, record):
    """
    For each field with note information in record, build a Note.
    Returns a list of zero or more Note objects.
    """
    record_element_type = record.get_xobis_element_type()

    notes = []

    for field in record.get_fields(*NOTE_FIELDS):
        # Doing this as one large query then using a switch conditional
        # is a way to retain original order.

        if field.tag == '500':
            ...
            ...
            ...

        elif field.tag == '502':
            ...
            ...
            ...

    return notes
