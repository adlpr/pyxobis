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
    def add_id_note(self, content_text, content_lang=None, class_=None, link_title=None, href_URI=None, set_URI=None):
        self.note_list.append(Note(
            GenericContent(content_text, content_lang),
            class_ = class_,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = LinkAttributes(link_title, XSDAnyURI(href_URI) if href_URI else None) \
                              if link_title else None,
            set_ref = XSDAnyURI(set_URI) if set_URI else None
        ))
    def add_id_alternate(self, id_descriptions, id_value, id_status=None, opt_note_list=OptNoteList()):
        if not isinstance(id_descriptions, list):
            id_descriptions = [id_descriptions]
            self.id_alternates.append( IDContent(id_descriptions, id_value, id_status, opt_note_list) )
    def add_type(self, xlink_title=None, xlink_href=None, set_ref=None):
        self.types.append(
            GenericType( LinkAttributes(xlink_title, XSDAnyURI(xlink_href)  \
                                                  if xlink_href else None)  \
                      if xlink_title else None,
                  XSDAnyURI(set_ref) if set_ref else None )
        )
    def set_principal_element(self, principal_element):
        # assert isinstance(principal_element, RefElement)
        self.principal_element = principal_element
    def add_action(self, time_or_duration_ref, xlink_title=None, xlink_href=None, set_ref=None):
        self.actions.append(
            ControlDataAction(
                GenericType( LinkAttributes(xlink_title, XSDAnyURI(xlink_href)  \
                                                      if xlink_href else None)  \
                          if xlink_title else None,
                      XSDAnyURI(set_ref) if set_ref else None ),
                time_or_duration_ref
            )
        )
    def add_relationship(self, relationship):
        # assert isinstance(relationship, Relationship)
        self.relationships.append(relationship)
    def build(self):
        return Record(
                   ControlData(
                       IDContent( self.id_descriptions,
                                  self.id_value,
                                  self.id_status,
                                  OptNoteList(self.note_list) ),
                       self.id_alternates,
                       self.types,
                       self.actions
                   ),
                   self.principal_element,
                   self.lang,
                   self.relationships
               )
