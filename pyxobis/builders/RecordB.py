#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *


class RecordBuilder:
    """
    Interface for constructing a XOBIS Record element.
    """
    def __init__(self):
        self.lang = None
        self.id_descriptions = []
        self.id_value = None
        self.id_status = None
        self.id_alternates = []
        self.current_id_alternate_descriptions = []
        self.current_id_alternate_value = None
        self.current_id_alternate_status = None
        self.current_id_alternate_notes = []
        self.types = []
        self.actions = []
        self.principal_element = None
        self.relationships = []
        self.note_list = []
    def set_lang(self, lang):
        self.lang = lang
    def add_id_description(self, id_description):
        self.id_descriptions.append(id_description)
    def set_id_value(self, id_value):
        self.id_value = id_value
    def set_id_status(self, id_status):
        self.id_status = id_status
    def add_id_note(self, content_text, content_lang=None, role=None, link_title=None, href_URI=None, set_URI=None, type_link_title=None, type_href_URI=None, type_set_URI=None, source=[]):
        if not isinstance(source, list):
            source = [source]
        assert all(any(isinstance(source_part, valid_type) for valid_type in (OrganizationRef, WorkRef, str)) for source_part in source)
        self.note_list.append(Note(
            GenericContent(content_text, content_lang),
            role = role,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = LinkAttributes(link_title, XSDAnyURI(href_URI) if href_URI else None) \
                              if link_title else None,
            set_ref = XSDAnyURI(set_URI) if set_URI else None,
            generic_type = GenericType(
                               LinkAttributes(
                                   type_link_title,
                                   href = XSDAnyURI( type_href_URI ) \
                                                if type_href_URI else None
                               ),
                               set_ref = XSDAnyURI( type_set_URI ) \
                                         if type_set_URI else None
                           ) if type_link_title else None,
            source = source if isinstance(source, list) else [source]
        ))
    def set_id_alternate(self, id_descriptions, id_value, id_status=None):
        if not isinstance(id_descriptions, list):
            id_descriptions = [id_descriptions]
        self.current_id_alternate_descriptions = id_descriptions
        self.current_id_alternate_value = id_value
        self.current_id_alternate_status = id_status
    def add_id_alternate_note(self, content_text, content_lang=None, role=None, link_title=None, href_URI=None, set_URI=None, type_link_title=None, type_href_URI=None, type_set_URI=None, source=[]):
        if not isinstance(source, list):
            source = [source]
        assert all(any(isinstance(source_part, valid_type) for valid_type in (OrganizationRef, WorkRef, str)) for source_part in source)
        href = XSDAnyURI( type_href_URI ) if type_href_URI else None
        set_ref = XSDAnyURI( type_set_URI ) if type_set_URI else None
        self.current_id_alternate_notes.append(Note(
            GenericContent(content_text, content_lang),
            role = role,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = LinkAttributes(link_title, XSDAnyURI(href_URI) if href_URI else None) \
                              if link_title else None,
            set_ref = XSDAnyURI(set_URI) if set_URI else None,
            generic_type = GenericType(
                               LinkAttributes(
                                   type_link_title,
                                   href = href
                               ),
                               set_ref = set_ref
                           ) if type_link_title else None,
            source = source if isinstance(source, list) else [source]
        ))
    def add_id_alternate(self, *args):
        # this set of methods is extremely awkward, maybe figure something better out
        if args:
            self.set_id_alternate(*args)
            self.add_id_alternate()
        else:
            note_list = NoteList(self.current_id_alternate_notes) if self.current_id_alternate_notes else None
            self.id_alternates.append( IDContent(self.current_id_alternate_descriptions,
                                                 self.current_id_alternate_value,
                                                 self.current_id_alternate_status,
                                                 note_list ) )
            self.current_id_alternate_descriptions = []
            self.current_id_alternate_value = None
            self.current_id_alternate_status = None
            self.current_id_alternate_notes = []
    def add_type(self, title=None, href=None, set_ref=None):
        self.types.append(
            GenericType( LinkAttributes(title, XSDAnyURI(href)  \
                                                  if href else None)  \
                      if title else None,
                  XSDAnyURI(set_ref) if set_ref else None )
        )
    def set_principal_element(self, principal_element):
        # assert isinstance(principal_element, RefElement)
        self.principal_element = principal_element
    def add_action(self, time_or_duration_ref, title=None, href=None, set_ref=None):
        self.actions.append(
            ControlDataAction(
                GenericType( LinkAttributes(title, XSDAnyURI(href)  \
                                                      if href else None)  \
                          if title else None,
                      XSDAnyURI(set_ref) if set_ref else None ),
                time_or_duration_ref
            )
        )
    def add_relationship(self, relationship):
        # assert isinstance(relationship, Relationship)
        self.relationships.append(relationship)
    def build(self):
        note_list = NoteList(self.note_list) if self.note_list else None
        return Record(
                   ControlData(
                       IDContent( self.id_descriptions,
                                  self.id_value,
                                  self.id_status,
                                  note_list ),
                       self.id_alternates,
                       self.types,
                       self.actions
                   ),
                   self.principal_element,
                   self.lang,
                   self.relationships
               )
