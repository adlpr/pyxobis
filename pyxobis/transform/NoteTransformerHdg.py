#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from . import tf_common_methods as tfcm
from pylmldb.xobis_constants import *

from .Indexer import Indexer


class NoteTransformerHdg:
    """
    Methods for extracting and building Note objects from
    holdings pymarc Records.
    """
    def __init__(self):
        self.lc_org_ref  = tfcm.build_simple_ref("Library of Congress", ORGANIZATION)
        self.nlm_org_ref = tfcm.build_simple_ref("National Library of Medicine (U.S.)", ORGANIZATION)


    def transform_notes(self, record):
        """
        For each field with note information in record, build a Note.
        Returns a list of zero or more Note kwarg dicts.
        """
        notes = []

        # Serial Control Decisions (Lane)
        # -> $d  Misc. series/serials treatment instructions (R)
        # -> $e  Series enumeration/call no. pattern (v. ---, --- ed., etc.) (R)
        #   + ad-hoc subfields from preprocessing:
        # -> $α  Analysis Treatment Note
        # -> $π  Component Parts Note
        # -> $ω  Acquisitions Note
        for field in record.get_fields('907'):
            for val in field.get_subfields('d'):
                notes.append({ 'content_text' : val,
                               'role' : 'documentation',
                               'type_link_title' : "Series/Serial Treatment Note" })
            for val in field.get_subfields('e'):
                notes.append({ 'content_text' : val,
                               'role' : 'documentation',
                               'type_link_title' : "Enumeration Pattern Note" })
            for val in field.get_subfields('α'):
                notes.append({ 'content_text' : val,
                               'role' : 'documentation',
                               'type_link_title' : "Analysis Treatment Note" })
            for val in field.get_subfields('π'):
                notes.append({ 'content_text' : val,
                               'role' : 'documentation',
                               'type_link_title' : "Component Parts Note" })
            for val in field.get_subfields('ω'):
                notes.append({ 'content_text' : val,
                               'role' : 'documentation',
                               'type_link_title' : "Acquisitions Note" })

        # Restrictions on Access Note (R)
        for field in record.get_fields('931'):
            for val in field.get_subfields('a'):
                notes.append({ 'content_text' : val,
                               'role' : 'annotation',
                               'type_link_title' : "General Note" })


        # Moved from bib

        # Restrictions on Access Note (R)
        for field in record.get_fields('506'):
            for val in field.get_subfields('a'):
                notes.append({ 'content_text' : val,
                               'role' : 'annotation',
                               'type_link_title' : "Access Note" })

        # Library of Congress Call Number (R)
        for field in record.get_fields('050'):
            if field.indicator1 != ' ':
                field['1'] = field.indicator1
            if field.indicator2 != ' ':
                field['2'] = field.indicator2
            notes.append({ 'content_text' : tfcm.concat_subfs(field),
                           'role' : 'annotation',
                           'type_link_title' : "Classification Note",
                           'source' : self.lc_org_ref })

        # National Library of Medicine Call Number (R)
        for field in record.get_fields('060'):
            if field.indicator1 != ' ':
                field['1'] = field.indicator1
            if field.indicator2 != ' ':
                field['2'] = field.indicator2
            notes.append({ 'content_text' : tfcm.concat_subfs(field),
                           'role' : 'annotation',
                           'type_link_title' : "Classification Note",
                           'source' : self.nlm_org_ref })

        # Retention Policy/Processing Instruction (Lane) (R)
        for field in record.get_fields('905'):
            notes.append({ 'content_text' : tfcm.concat_subfs(field),
                           'role' : 'documentation',
                           'type_link_title' : "Retention/Processing Note" })

        # Staff Note (Lane) (R)
        for field in record.get_fields('990'):
            for val in field.get_subfields('a'):
                notes.append({ 'content_text' : val,
                               'role' : 'documentation',
                               'type_link_title' : "General Note" })

        # Title-Level Selection Data (Lane) (R)
        for field in record.get_fields('992'):
            notes.append({ 'content_text' : tfcm.concat_subfs(field),
                           'role' : 'documentation',
                           'type_link_title' : "Title-Level Selection Data Note" })

        # Title-Level Usage Statistics (Lane) (NR)
        for field in record.get_fields('993'):
            notes.append({ 'content_text' : tfcm.concat_subfs(field),
                           'role' : 'documentation',
                           'type_link_title' : "Title-Level Usage Statistics Note" })

        # add href and set URIs to all types in notes
        for note in notes:
            if 'type_link_title' in note:
                note['type_href_URI'] = Indexer.simple_lookup(note['type_link_title'], CONCEPT)
                note['type_set_URI'] = Indexer.simple_lookup("Note Type", CONCEPT)

        return notes
