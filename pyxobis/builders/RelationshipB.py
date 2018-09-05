#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *


class RelationshipBuilder:
    """
    Interface for constructing a XOBIS Relationship element.
    """
    def __init__(self):
        self.name_text = None
        self.name_lang = None
        self.note_list = []
        self.element_ref = None
        self.type = None
        self.degree = None
        self.enumeration = None
        self.time_or_duration_ref = None
    def set_name(self, name_text, name_lang=None):
        self.name_text, self.name_lang = name_text, name_lang
    def add_note(self, content_text, content_lang=None, type=None, link_title=None, href_URI=None, set_URI=None):
        self.note_list.append(Note(
            GenericContent(content_text, content_lang),
            type = type,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = LinkAttributes(link_title, XSDAnyURI(href_URI) if href_URI else None) \
                              if link_title else None,
            set_ref = XSDAnyURI(set_URI) if set_URI else None
        ))
    def set_target(self, element_ref):
        # assert isinstance(element_ref, RefElement)
        self.element_ref = element_ref
    def set_type(self, new_type):
        self.type = new_type
    def set_degree(self, degree):
        self.degree = degree
    def set_enumeration(self, enumeration):
        self.enumeration = enumeration
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, RefElement)
        self.time_or_duration_ref = time_or_duration_ref
    def build(self):
        return Relationship(
                   RelationshipContent(
                       RelationshipName(
                           GenericContent( self.name_text,
                                    lang = self.name_lang ),
                           opt_note_list = OptNoteList(self.note_list)
                       ),
                       self.element_ref,
                       type   = self.type,
                       degree = self.degree,
                       enumeration = self.enumeration,
                       time_or_duration_ref = self.time_or_duration_ref
                   )
               )
