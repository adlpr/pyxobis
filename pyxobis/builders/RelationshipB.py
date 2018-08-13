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
        self.modifier_nonfiling = 0
        self.modifier_text = None
        self.modifier_lang = None
        self.element_ref = None
        self.type = None
        self.degree = None
        self.enumeration = None
        self.time_or_duration_ref = None
    def set_name(self, name_text, name_lang=None):
        self.name_text, self.name_lang = name_text, name_lang
    def set_modifier(self, modifier_text, modifier_lang=None, modifier_nonfiling=0):
        self.modifier_text, self.modifier_lang = modifier_text, modifier_lang
        self.modifier_nonfiling = modifier_nonfiling
    def set_target(self, element_ref):
        # assert isinstance(element_ref, RefElement)
        self.element_ref = element_ref
    def set_type(self, new_type):
        self.type = new_type
    def set_degree(self, degree):
        self.degree = degree
    def set_enumeration(self, enumeration):
        self.degree = new_degree
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, RefElement)
        self.time_or_duration_ref = time_or_duration_ref
    def build(self):
        return Relationship(
                   RelationshipContent(
                       RelationshipName(
                           GenericContent( self.name_text,
                                    lang = self.name_lang ),
                           modifier_nonfiling = self.modifier_nonfiling,
                           modifier_content  = GenericContent( self.modifier_text,
                                                       lang = self.modifier_lang ) \
                                              if self.modifier_text else None
                       ),
                       self.element_ref,
                       type   = self.type,
                       degree = self.degree,
                       enumeration = self.enumeration,
                       time_or_duration_ref = self.time_or_duration_ref
                   )
               )
