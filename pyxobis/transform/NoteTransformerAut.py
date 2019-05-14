#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from . import tf_common_methods as tfcm
from .tf_constants import *

from .Indexer import Indexer


class NoteTransformerAut:
    """
    Methods for extracting and building Note objects from
    authority pymarc Records.
    """
    def __init__(self):
        self.mesh_ref = tfcm.build_simple_ref("Medical subject headings", WORK_AUT)


    def transform_notes(self, record):
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
        #         notes.append({ 'content_text' : tfcm.concat_subfs(field),
        #                        'role' : 'annotation',
        #                         # 'type_link_title' : 'Generic phrase, pre-coordinated qualifier, or obsolete descriptor note'
        #                         })

        # Series Dates of Publication and/or Volume Designation (R) (Lane)
        for field in record.get_fields('640'):
            for val in field.get_subfields('a'):
                notes.append({ 'content_text' : val,
                               'role' : 'annotation',
                               'type_link_title' : 'Description (Serial Enumeration/Chronology, Unformatted) Note' })

        # Series Numbering Peculiarities (R)
        for field in record.get_fields('641'):
            for val in field.get_subfields('a'):
                notes.append({ 'content_text' : val,
                               'role' : 'annotation',
                               'type_link_title' : 'Enumeration Note' })

        # Series Place and Publisher/Issuing Body (R)
        for field in record.get_fields('643'):
           notes.append({ 'content_text' : tfcm.concat_subfs(field),
                          'role' : 'description',
                          'type_link_title' : 'Organizations (Imprint) Note' })

        # Complex See Also Reference, Name (NR)
        for field in record.get_fields('663'):
           notes.append({ 'content_text' : tfcm.concat_subfs(field),
                          'role' : 'description',
                          'type_link_title' : 'Relationship Note, Being' })

        # History Reference (NR)
        for field in record.get_fields('665'):
           notes.append({ 'content_text' : tfcm.concat_subfs(field),
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
            is_unprocessed_rda = field.indicator1 == '7'
            if is_unprocessed_rda:
                field.subfields = ['9', { '0': 'Associated Place',
                                        '1': 'Address',
                                        '2': 'Field of Activity',
                                        '3': 'Affiliation',
                                        '4': 'Occupation',
                                        '6': 'Family Information',
                                        '7': 'Associated Language',
                                        '8': 'Fuller Form of Personal Name' }.get(field.indicator2, 'Undefined')] + field.subfields
            notes.append({ 'content_text' : tfcm.concat_subfs(field),
                           'role' : 'annotation',
                           'type_link_title' : 'Relationship Note, Unprocessed RDA' if is_unprocessed_rda else 'Historical Note' })

        # Public General Note (Lane: reserved for NLM use) (R)
        for field in record.get_fields('680'):
           notes.append({ 'content_text' : field['a'] if 'a' in field and len(field.get_subfields())==1 else tfcm.concat_subfs(field),
                          'role' : 'description',
                          'type_link_title' : 'General Note',
                          'source' : self.mesh_ref if field.indicator1=='8' else 'External' })

        # Note that 683/684/685 fields that successfully map to Organizational Relationships
        # should have been converted to 610s before now

        # Academic Credentials (for persons) (Lane) (R)
        for field in record.get_fields('683'):
           notes.append({ 'content_text' : tfcm.concat_subfs(field),
                          'role' : 'description',
                          'type_link_title' : 'Relationship Note, Academic Credentials' })

        # Latest / Former Organizational Affiliation (for persons) (Lane) (R)
        for field in record.get_fields('684','685'):
           notes.append({ 'content_text' : tfcm.concat_subfs(field),
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
            notes.append({ 'content_text' : tfcm.concat_subfs(field),
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
            content = tfcm.concat_subfs(field)
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
                note['type_href_URI'] = Indexer.simple_lookup(note['type_link_title'], CONCEPT)
                note['type_set_URI'] = Indexer.simple_lookup("Note Type", CONCEPT)

        return notes
