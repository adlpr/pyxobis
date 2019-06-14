#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import Builder, RefBuilder


class HoldingsBuilder(Builder):
    """
    Interface for constructing a XOBIS Holdings element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_name_tuple
    # ADDITIONAL: set_work_or_object_ref, set_concept_ref
    def __init__(self):
        super().__init__()
        self.work_or_object_ref = None
        self.concept_ref = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have name element")
    def add_name_tuple(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have name element")
    def set_work_or_object_ref(self, work_or_object_ref):
        self.work_or_object_ref = work_or_object_ref
    def set_concept_ref(self, concept_ref):
        self.concept_ref = concept_ref
    def build(self):
        return Holdings(
                   HoldingsEntryContent(
                       self.work_or_object_ref,
                       self.concept_ref,
                       QualifiersOpt(self.qualifiers)
                   ),
                   opt_note_list = OptNoteList(self.note_list)
               )


class HoldingsRefBuilder(Builder):
    """
    Interface for constructing a HoldingsRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_name_tuple
    # ADDITIONAL: set_work_or_object_ref, set_concept_ref, set_link
    def __init__(self):
        super().__init__()
        self.work_or_object_ref = None
        self.concept_ref = None
        self.link_attributes = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("Holdings ref element does not have name element")
    def add_name_tuple(self, *args, **kwargs):
        raise AttributeError("Holdings ref element does not have name element")
    def set_work_or_object_ref(self, work_or_object_ref):
        self.work_or_object_ref = work_or_object_ref
    def set_concept_ref(self, concept_ref):
        self.concept_ref = concept_ref
    def set_link(self, link_title, href_URI=None):
        self.link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
    def build(self):
        return HoldingsRef(
                   HoldingsEntryContent(
                       self.work_or_object_ref,
                       self.concept_ref,
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
