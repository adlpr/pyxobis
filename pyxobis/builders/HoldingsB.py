#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import Builder, PrincipalElementBuilder


class HoldingsBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Holdings element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_name_tuple, add_variant, set_type, set_role,
    #             set_scheme, set_class, set_usage, set_entry_group_attributes
    # ADDITIONAL: set_work_or_object_ref, set_concept_ref,
    #             set_summary, add_summary_note
    def __init__(self):
        super().__init__()
        self.work_or_object_ref = None
        self.concept_ref = None
        self.holdings_summary_enumeration = None
        self.holdings_summary_chronology = None
        self.holdings_summary_notes = []
    def add_name(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have name element")
    def add_name_tuple(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have name element")
    def add_variant(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have variants element")
    def set_type(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have property 'type'")
    def set_role(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have property 'role'")
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have property 'scheme'")
    def set_class(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have property 'class'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have property 'usage'")
    def set_entry_group_attributes(self, *args, **kwargs):
        raise AttributeError("Holdings element does not have entry group attributes")
    def set_work_or_object_ref(self, work_or_object_ref):
        self.work_or_object_ref = work_or_object_ref
    def set_concept_ref(self, concept_ref):
        self.concept_ref = concept_ref
    def set_summary(self, enumeration, chronology):
        self.holdings_summary_enumeration = enumeration
        self.holdings_summary_chronology = chronology
    def add_summary_note(self, content_text, content_lang=None, role=None, link_title=None, href_URI=None, set_URI=None, type_link_title=None, type_href_URI=None, type_set_URI=None, source=[]):
        if not isinstance(source, list):
            source = [source]
        assert all(any(isinstance(source_part, valid_type) for valid_type in (OrganizationRef, WorkRef, str)) for source_part in source)
        self.holdings_summary_notes.append(Note(
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
    def build(self):
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        holdings_summary = None
        if (self.holdings_summary_enumeration is not None) or (self.holdings_summary_chronology is not None):
            summary_note_list = NoteList(self.holdings_summary_notes) if self.holdings_summary_notes else None
            holdings_summary = HoldingsSummary(
                                   self.holdings_summary_enumeration,
                                   self.holdings_summary_chronology,
                                   summary_note_list
                               )
        return Holdings(
                   HoldingsEntryContent(
                       self.work_or_object_ref,
                       self.concept_ref,
                       qualifiers
                   ),
                   holdings_summary = holdings_summary,
                   note_list = note_list
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
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        return HoldingsRef(
                   HoldingsEntryContent(
                       self.work_or_object_ref,
                       self.concept_ref,
                       qualifiers
                   ),
                   link_attributes = self.link_attributes
               )
