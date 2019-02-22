#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pymarc import Field
from pyxobis.builders import *
from .tf_common import *

def transform_notes_bib(self, record):
    """
    For each field with note information in record, build a Note.
    Returns a list of zero or more Note kwarg dicts.
    """
    # record_element_type = record.get_xobis_element_type()

    notes = []

    # for field in record.get_fields(*NOTE_FIELDS):
    # Doing this as one large query then using a switch conditional
    # is a way to retain original order.

    # Geographic Area Code (NR)
    for field in record.get_fields('043'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Place Note' })

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
                       'role' : 'description',
                       'type_link_title' : 'Description (Edition) Note' })

    # Computer File Characteristics (Lane: imported only) (NR)
    for field in record.get_fields('256'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Computer File) Note' })


    # LC Publication, Distribution, etc. (Imprint) (Lane: cf. 265) (R)
    for field in record.get_fields('260'):
        ...
        ...
        ...
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Organizations (Imprint) Note' })

    # Production, Publication, Distribution, Manufacture, and Copyright Notice (R) (R)
    for field in record.get_fields('264'):
        if field.indicator2 == '4':
            # these are Relationships to copyright date
            continue
        ...
        ...
        ...
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Organizations (Imprint) Note' })


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

    # With Note (R)
    for field in record.get_fields('501'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Relationship Note, With' })

    # Dissertation Note (R)
    for field in record.get_fields('502'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Dissertation Note' })

    # Bibliography/Webliography Note (R)
    for field in record.get_fields('504'):
        notes.append({ 'content_text' : concat_subfs(field) if 'b' in field else field['a'],
                       'role' : 'description',
                       'type_link_title' : 'Bibliography Note' })

    # Formatted Contents Note (R)
    for field in record.get_fields('505'):
        notes.append({ 'content_text' : field['a'] if 'a' in field and len(field.get_subfields())==1 else concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : { '1' : 'Contents Note, Incomplete',
                                             '2' : 'Contents Note, Partial',
                                             '8' : 'Contents Note, Continued' }.get(field.indicator1, 'Contents Note') })

    # Citation/References Note (R)
    for field in record.get_fields('510'):
        if 'w' not in field:
            notes.append({ 'content_text' : concat_subfs(field),
                           'role' : 'description',
                           'type_link_title' : 'Relationship Note, Citation' })

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

    # Summary, etc. (R)
    for field in record.get_fields('520'):
        # From aut record, dm:
        #   If 1st ind values indicated are present, prepend a $e (0 = Subject;
        #   1 = Review; 2 = Scope and content; 3 = Abstract; 8 = Continued),
        #   retaining this and other subfields in order found.
        label = { '0' : "Subject",
                  '1' : "Review",
                  '2' : "Scope and content",
                  '3' : "Abstract",
                  '8' : "Continued" }.get(field.indicator1)
        if label:
            field.subfields = ['e', label] + field.subfields
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Summary Note' })

    # Target Audience Note (R)
    for field in record.get_fields('521'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Audience Note' })

    # Supplement Note (R)
    for field in record.get_fields('525'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Supplement Note' })

    # Reproduction Note (R)
    for field in record.get_fields('533'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Relationship Note, Reproduction' })

    # Original Version Note (R)
    for field in record.get_fields('534'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Relationship Note, Original Version' })

    # Funding Information Note (R)
    for field in record.get_fields('536'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Funding Note' })

    # Location of Other Archival Materials Note (R)
    for field in record.get_fields('544'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Archival Materials (Associated/Related) Note' })

    # Biographical or Historical Data (R)
    for field in record.get_fields('545'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Archival Materials (Administrative) Note' if field.indicator1=='1' else 'Archival Materials (Biographical) Note' })

    # Language Note (R)
    for field in record.get_fields('546'):
        notes.append({ 'content_text' : concat_subfs(field, with_codes=False),
                       'role' : 'description',
                       'type_link_title' : 'Language Note' })

    # Former Title Complexity Note (R)
    for field in record.get_fields('547'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Serial Title Complexity) Note' })

    # Issuing Bodies Note (R)
    for field in record.get_fields('550'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Organizations (Issuing Body) Note' })

    # Cumulative Index/Finding Aids Note (R)
    for field in record.get_fields('555'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Archival Materials (Finding Aid) Note' if field.indicator1=='0' else 'Description (Serial Index) Note' })

    # Information about Documentation Note (R)
    for field in record.get_fields('556'):
        notes.append({ 'content_text' : field['a'] if 'a' in field and len(field.get_subfields())==1 else concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Relationship (Documentation) Note' })

    # Ownership and Custodial History (Provenance) (R)
    for field in record.get_fields('561'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Archival Materials (Provenance) Note' })

    # Editor(s) Note for Serials (Lane) (R)
    for field in record.get_fields('570'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Description (Serial Responsibility) Note' })

    # Linking Entry Complexity Note (R)
    for field in record.get_fields('580'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Relationship Note' })

    # Publications About Described Materials Note (R)
    for field in record.get_fields('581'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Relationship Note, Subject' })

    # Awards Note (R)
    for field in record.get_fields('586'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Awards Note' })

    # Local Note (Lane) (R)
    for field in record.get_fields('590'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Lane Local Note' })

    # Staff Note (Lane) (R)
    for field in record.get_fields('990'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'documentation',
                           'type_link_title' : 'General Note' })

    # add href and set URIs to all types in notes
    for note in notes:
        if 'type_link_title' in note:
            note['type_href_URI'] = self.ix.simple_lookup(note['type_link_title'], RELATIONSHIP)
            note['type_set_URI'] = self.ix.simple_lookup("Notes", CONCEPT)

    return notes