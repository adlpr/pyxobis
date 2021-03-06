#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *


class RelationshipBuilder:
    """
    Interface for constructing a XOBIS Relationship element.
    """
    def __init__(self):
        self.link_attributes = None
        self.name_text = None
        self.name_lang = None
        self.note_list = []
        self.element_ref = None
        self.type = None
        self.degree = None
        self.enumeration = None
        self.time_or_duration_ref = None
    def set_type(self, new_type):
        self.type = new_type
    def set_degree(self, degree):
        self.degree = degree
    def set_name(self, name_text, name_lang=None):
        self.name_text, self.name_lang = name_text, name_lang
    def set_link(self, link_title, href_URI=None):
        self.link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
    def add_note(self, content_text, content_lang=None, role=None, link_title=None, href_URI=None, set_URI=None, type_link_title=None, type_href_URI=None, type_set_URI=None, source=[]):
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
    def set_enumeration(self, enumeration):
        self.enumeration = enumeration
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, RefElement)
        self.time_or_duration_ref = time_or_duration_ref
    def set_target(self, element_ref):
        # assert isinstance(element_ref, RefElement)
        self.element_ref = element_ref
    def build(self):
        note_list = NoteList(self.note_list) if self.note_list else None
        return Relationship(
                   RelationshipContent(
                       RelationshipName(
                           GenericContent( self.name_text,
                                    lang = self.name_lang ),
                           self.link_attributes
                       ),
                       self.element_ref,
                       type   = self.type,
                       degree = self.degree,
                       enumeration = self.enumeration,
                       time_or_duration_ref = self.time_or_duration_ref,
                       note_list = note_list
                   )
               )
