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

    # Geographic Area Code (NR)
    for field in record.get_fields('043'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Place Note' })

    ...
    ...
    ...

    # See Also From Reference, Topical/Language/Time Term (R)
    # for field in record.get_fields('550'):
    #     if 'a' not in field:
    #         # @@@@@@@@@@ TEMPORARY TEMPORARY TEMPORARY TEMPORARY @@@@@@@@@@
    #         # @@@@@@@@@@ concatenate all subfields @@@@@@@@@@
    #         notes.append({ 'content_text' : concat_subfs(field),
    #                        'role' : 'annotation',
    #                         # 'type_link_title' : 'Generic phrase, pre-coordinated qualifier, or obsolete descriptor note'
    #                         })

    # Complex See Also Reference, Name (NR)
    for field in record.get_fields('663'):
       notes.append({ 'content_text' : concat_subfs(field),
                      'role' : 'description',
                      'type_link_title' : 'Relationship Note, Being' })

    # History Reference (NR)
    for field in record.get_fields('665'):
       notes.append({ 'content_text' : concat_subfs(field),
                      'role' : 'documentation',
                      'type_link_title' : 'Historical Note' })

    # Nonpublic General Note (R)  [basically 990 but for MeSH]
    for field in record.get_fields('667'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'documentation',
                           'type_link_title' : 'General Note',
                           'source' : self.mesh_ref if field.indicator1=='8' else 'External' })

    # Biographical or Historical Public Note (Epitome) (R)
    for field in record.get_fields('678'):
        # @@@@@@@@@@ TEMPORARY TEMPORARY TEMPORARY TEMPORARY @@@@@@@@@@
        # @@@@@@@@@@ concatenate all subfields @@@@@@@@@@
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'annotation',
                       'type_link_title' : 'Historical Note' })

    # Public General Note (Lane: reserved for NLM use) (R)
    for field in record.get_fields('680'):
       notes.append({ 'content_text' : field['a'] if 'a' in field and len(field.get_subfields())==1 else concat_subfs(field),
                      'role' : 'description',
                      'type_link_title' : 'General Note',
                      'source' : self.mesh_ref if field.indicator1=='8' else 'External' })

    # Academic Credentials (for persons) (Lane) (R)
    for field in record.get_fields('683'):
       notes.append({ 'content_text' : concat_subfs(field),
                      'role' : 'description',
                      'type_link_title' : 'Relationship Note, Academic Credentials' })

    # Latest / Former Organizational Affiliation (for persons) (Lane) (R)
    for field in record.get_fields('684','685'):
       notes.append({ 'content_text' : concat_subfs(field),
                      'role' : 'description',
                      'type_link_title' : 'Relationship Note, Organizational Affiliation' })

    # Bibliographical Reference (Lane) (R)
    for field in record.get_fields('686'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'description',
                           'type_link_title' : 'Relationship Note, Citation'})

    # Application History Note (R)
    for field in record.get_fields('688'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Application History Note',
                           'source' : self.mesh_ref if field.indicator1=='8' else 'External' })

    # Scope Note (MeSH) (Lane) (R)
    for field in record.get_fields('689'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'annotation',
                           'type_link_title' : 'Scope Note',
                           'source' : self.mesh_ref if field.indicator1=='8' else 'External' })

    ...
    ...
    ...

    # Source Data Found (LC: 670) (R)
    for field in record.get_fields('970'):
        notes.append({ 'content_text' : concat_subfs(field),
                       'role' : 'description',
                       'type_link_title' : 'Source Data Found Note'})

    # Source Data Not Found (LC: 675) (R)
    for field in record.get_fields('975'):
        for val in field.get_subfields('a'):
            notes.append({ 'content_text' : val,
                           'role' : 'description',
                           'type_link_title' : 'Source Data Not Found Note'})

    # Undisplayed/Unindexed terms
    for field in record.get_fields('985','986','987','988','995'):
        # Term type indicator subfield
        field.subfields = [ 'i', {'985' : 'Place',
                                '986' : 'Being',
                                '987' : 'Organization',
                                '988' : 'Event',
                                '995' : 'Concept'}.get(field.tag) ] + field.subfields
        content = concat_subfs(field)
        # Preserve 995 I2 with description
        if field.tag == '995':
            i2_desc = {
                '1' : '1 = Deleted/transferred by NLM',
                '2' : '2 = Unreviewed new MeSH "nonprint" xref (current year changes)',
                '4' : '4 = Demoted "Print" xref (auto copied/deleted from 450 or 451 when 2nd ind = 3)',
                '5' : '5 = Demoted "Print" xref (auto copied/deleted from 550 or 551 when 2nd ind = 3)',
                '6' : '8 = Unreviewed legacy MeSH "nonprint" xref',
                '7' : '9 = Promoted "Nonprint" xref (automatically copied to 450 or 451 with 2nd ind = 9)'
            }.get(field.indicator2, "_ = MeSH Short form and/or Sort version OR other unused xref")
            content = i2_desc + ' ' + content
        notes.append({ 'content_text' : content,
                       'role' : 'documentation',
                       'type_link_title' : 'Undisplayed/Unindexed Term Note' })

    ...
    ...
    ...

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
