#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class BeingBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Being element.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple)
    #    MISSING: set_usage
    # ADDITIONAL: set_entry_type, set_time_or_duration_ref
    def __init__(self):
        super().__init__()
        self.entry_type = None
        self.time_or_duration_ref = None
    def add_name(self, *args, **kwargs):
        super().add_name_tuple(*args, **kwargs)
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Being element does not have property 'usage'")
    def set_entry_type(self, link_title, set_URI, href_URI=None):
        href = XSDAnyURI(href_URI) if href_URI is not None else None
        set_ref = XSDAnyURI(set_URI) if set_URI is not None else None
        self.entry_type = GenericType(
                              LinkAttributes(
                                  link_title,
                                  href = href
                              ),
                              set_ref = set_ref
                          )
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
    def build(self):
        name_content = self.name_content
        if len(self.name_content) == 1 and self.name_content[0][0] == "generic":
            name_content = name_content[0][1]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        return Being(
                   RoleAttributes(self.role),
                   BeingEntryContent(
                       name_content,
                       qualifiers
                   ),
                   type_  = self.type,
                   class_ = self.class_,
                   scheme_attribute = self.scheme,
                   entry_group_attributes = self.entry_group_attributes,
                   entry_type = self.entry_type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   variants = self.variants,
                   note_list = note_list
               )


class BeingVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a BeingVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple)
    #    MISSING: -
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_name(self, *args, **kwargs):
        super().add_name_tuple(*args, **kwargs)
    def build(self):
        name_content = self.name_content
        if len(self.name_content) == 1 and self.name_content[0][0] == "generic":
            name_content = name_content[0][1]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        return BeingVariantEntry(
                   BeingEntryContent(
                       name_content,
                       qualifiers
                   ),
                   variant_attributes = self.variant_attributes,
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = self.substitute_attribute,
                   scheme_attribute = self.scheme,
                   entry_group_attributes = self.entry_group_attributes,
                   note_list = note_list
               )


class BeingRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a BeingRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple)
    #    MISSING: add_subdivision_link
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_name(self, *args, **kwargs):
        super().add_name_tuple(*args, **kwargs)
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("Being element ref does not have subdivisions")
    def build(self):
        name_content = self.name_content
        if len(self.name_content) == 1 and self.name_content[0][0] == "generic":
            name_content = name_content[0][1]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        return BeingRef(
                   BeingEntryContent(
                       name_content,
                       qualifiers
                   ),
                   link_attributes = self.link_attributes
               )
