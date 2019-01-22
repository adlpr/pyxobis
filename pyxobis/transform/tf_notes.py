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

    # See Also From Reference, Topical/Language/Time Term (R)
    for field in record.get_fields('550'):
        if 'a' not in field:
            # @@@@@@@@@@ TEMPORARY TEMPORARY TEMPORARY TEMPORARY @@@@@@@@@@
            # @@@@@@@@@@ concatenate all subfields @@@@@@@@@@
            notes.append({ 'content_text' : concat_subfs(field),
                           'role' : 'annotation',
                            # 'type_link_title' : 'Generic phrase, pre-coordinated qualifier, or obsolete descriptor note'
                            })

    # Nonpublic General Note (R)  [basically 990 but for MeSH]
    """
        External Nonpublic Note (667 1st ind blank)
        MeSH Nonpublic Note (667 1st ind 8)
    """
    for field in record.get_fields('667'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'documentation',
                           'type_link_title' : 'General Note' })

    # Biographical or Historical Public Note (Epitome) (R)
    for field in record.get_fields('678'):
        # @@@@@@@@@@ TEMPORARY TEMPORARY TEMPORARY TEMPORARY @@@@@@@@@@
        # @@@@@@@@@@ concatenate all subfields @@@@@@@@@@
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'annotation',
                       'type_link_title' : 'Historical Note' })

    # Public General Note (Lane: reserved for NLM use) (R)
    """
        External Public Note (aut 680 1st ind blank)
        MeSH Public Note (680 1st ind 8)
    """
    for field in record.get_fields('680'):
       notes.append({ 'content_text' : field['a'] if 'a' in field and len(field.get_subfields())==1 else concat_subfs(field),
                      'role' : 'annotation',
                      'type_link_title' : 'General Note' })

    # Application History Note (R)
    """
        External Application History Note (688 1st ind blank)
        MeSH Application History Note (688 1st ind 8)
    """
    for field in record.get_fields('688'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'MeSH Application History Note' if field.indicator1 == '8' else 'External Application History Note' })

    """
        External Scope Note (689 1st ind blank)
        MeSH Scope Note (689 1st ind 8)
    """
    # Scope Note (MeSH) (Lane) (R)
    for field in record.get_fields('689'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'MeSH Scope Note' if field.indicator1 == '8' else 'External Scope Note' })
    ...
    ...
    ...

    # @@@@@@@@@@ TEMPORARY TEMPORARY TEMPORARY TEMPORARY @@@@@@@@@@
    # Staff Note (Lane) (R)
    # for field in record.get_fields('990'):
    #     # concatenate all subfields
    #     notes.append({ 'content_text' : ' '.join(field.get_subfields()),
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

    # Title Statement (NR)
    for field in record.get_fields('245'):
        for val in field.get_subfields('b'):
            notes.append({ 'content_text' : val,
                           'role' : 'transcription',
                           'type_link_title' : 'Description (Title Remainder) Note' })
        for val in field.get_subfields('c'):
            notes.append({ 'content_text' : val,
                           'role' : 'transcription',
                           'type_link_title' : 'Description (Responsibility) Note' })

    # Edition Statement (R)
    for field in record.get_fields('250'):
        notes.append({ 'content_text' : concat_subfs(field, with_codes=False) if 'b' in field else field['a'],
                       'role' : 'transcription',
                       'type_link_title' : 'Description (Edition) Note' })

    # Computer File Characteristics (Lane: imported only) (NR)
    for field in record.get_fields('256'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Computer File) Note' })

    # Physical Description (R)
    for field in record.get_fields('300'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Extent) Note' })
        for val in field.get_subfields('b'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Illustration) Note' })
        for val in field.get_subfields('c'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Size) Note' })
        for val in field.get_subfields('e'):
            ...
            ...
            ...

    # Playing Time (NR)
    for field in record.get_fields('306'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Playing Time) Note' })

    # Dates of Publication and/or Sequential Designation (R)
    for field in record.get_fields('362'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Serial Enumeration/Chronology, Formatted) Note' if field.indicator1 == '0' else 'Description (Serial Enumeration/Chronology, Unformatted) Note' })

    # General Note (R)
    for field in record.get_fields('500'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'General Note' })

    # Dissertation Note (R)
    for field in record.get_fields('502'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Dissertation Note' })

    # Bibliography/Webliography Note (R)
    for field in record.get_fields('504'):
        notes.append({ 'content_text' : concat_subfs(field) if 'b' in field else field['a'],
                       'role' : 'annotation',
                       'type_link_title' : 'Bibliography Note' })

    # Formatted Contents Note (R)
    for field in record.get_fields('505'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'annotation',
                       'type_link_title' : 'Contents Note' })  # @@@@@@@@@

    # Numbering Peculiarities Note (R)
    for field in record.get_fields('515'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Enumeration Note' })

    # Date/Time and Place of an Event Note (Lane Pending) (R)
    for field in record.get_fields('518'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Event Note' })

    # Language Note (R)
    for field in record.get_fields('546'):
        notes.append({ 'content_text' : concat_subfs(field, with_codes=False),
                       'role' : 'annotation',
                       'type_link_title' : 'Language Note' })

    # Issuing Bodies Note (R)
    for field in record.get_fields('550'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Organizations (Issuing Body) Note' })


    # Issuing Bodies Note (R)
    for field in record.get_fields('550'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Organizations (Issuing Body) Note' })

    # Staff Note (Lane) (R)
    for field in record.get_fields('990'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'documentation',
                           'type_link_title' : 'Staff Note' })  # @@@@@@@@@


    # add href and set URIs to all types in notes
    for note in notes:
        if 'type_link_title' in note:
            note['type_href_URI'] = self.ix.simple_lookup(note['type_link_title'], RELATIONSHIP)
            note['type_set_URI'] = self.ix.simple_lookup("Notes", CONCEPT)

    return notes
