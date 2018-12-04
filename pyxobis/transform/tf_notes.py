#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pymarc import Field
from pyxobis.builders import *
from .tf_common import *

def transform_notes_aut(self, record):
    """
    For each field with note information in record, build a Note.
    Returns a list of zero or more Note kwarg dicts.
    """
    notes = []

    ...
    ...
    ...

    # @@@@@@@@@@ TEMPORARY TEMPORARY TEMPORARY TEMPORARY @@@@@@@@@@
    # Biographical or Historical Public Note (Epitome) (R)
    for field in record.get_fields('678'):
        # concatenate all subfields
        note = { 'content_text' : ' '.join(field.get_subfields()),
                 'role' : 'annotation',
                 'type_link_title' : 'Historical Note' }
        notes.append(note)

    ...
    ...
    ...

    # @@@@@@@@@@ TEMPORARY TEMPORARY TEMPORARY TEMPORARY @@@@@@@@@@
    # Staff Note (Lane) (R)
    # for field in record.get_fields('990'):
    #     # concatenate all subfields
    #     note = { 'content_text' : ' '.join(field.get_subfields()),
    #              'role' : 'documentation',
    #              'type_link_title' : 'Staff Note' }
    #     notes.append(note)

    ...
    ...
    ...

    # add href and set URIs to all types in notes
    for note in notes:
        if 'type_link_title' in note:
            note['type_href_URI'] = self.ix.simple_lookup(note['type_link_title'], RELATIONSHIP)
            note['type_set_URI'] = self.ix.simple_lookup("Notes", CONCEPT)

    return notes

def transform_notes_bib(self, record):
    """
    For each field with note information in record, build a Note.
    Returns a list of zero or more Note kwarg dicts.

    { 'content_text' : val,
       'content_lang' : None,
       'role' : None,
       'link_title' : None,
       'href_URI' : None,
       'set_URI' : None,
       'type_link_title' : None,
       'type_href_URI' : None,
       'type_set_URI' : None }
    """
    record_element_type = record.get_xobis_element_type()

    notes = []

    # for field in record.get_fields(*NOTE_FIELDS):
    # Doing this as one large query then using a switch conditional
    # is a way to retain original order.

    # General Note (R)
    for field in record.get_fields('500'):
        for val in field.get_subfields('a'):
            note = { 'content_text' : val,
                     'role' : 'annotation',
                     'type_link_title' : 'General Note' }
            notes.append(note)

    # elif field.tag == '502':
    #     ...
    #     ...
    #     ...

    # Staff Note (Lane) (R)
    for field in record.get_fields('990'):
        for val in field.get_subfields('a'):
            note = { 'content_text' : val,
                     'role' : 'documentation',
                     'type_link_title' : 'Staff Note' }
            notes.append(note)


    # add href and set URIs to all types in notes
    for note in notes:
        if 'type_link_title' in note:
            note['type_href_URI'] = self.ix.simple_lookup(note['type_link_title'], RELATIONSHIP)
            note['type_set_URI'] = self.ix.simple_lookup("Notes", CONCEPT)

    return notes
