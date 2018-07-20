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
        self.entry_type = Type()
        self.time_or_duration_ref = None
    def add_name(self, *args, **kwargs):
        super().add_name_tuple(*args, **kwargs)
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Being element does not have property 'usage'")
    def set_entry_type(self, link_title, role_URI, href_URI=None):
        self.entry_type = Type(
                              LinkAttributes(
                                  link_title,
                                  xlink_href = XSDAnyURI( href_URI ) \
                                               if href_URI else None
                              ),
                              xlink_role = XSDAnyURI( role_URI ) \
                                           if role_URI else None
                          )
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
    def add_variant(self, variant):
        # assert isinstance(variant, VariantEntry)
        super().add_variant(variant)
    def build(self):
        name_content = self.name_content[0][1]                       \
                       if len(self.name_content) == 1                \
                           and self.name_content[0][0] == "generic"  \
                       else self.name_content
        return Being(
                   RoleAttributes(self.role),
                   BeingEntryContent(
                       name_content,
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_  = self.type,
                   class_ = self.class_,
                   opt_scheme = OptScheme(self.scheme),
                   entry_type = self.entry_type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   variants = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
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
        name_content = self.name_content[0][1]                       \
                       if len(self.name_content) == 1                \
                           and self.name_content[0][0] == "generic"  \
                       else self.name_content
        return BeingVariantEntry(
                   BeingEntryContent(
                       name_content,
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = SubstituteAttribute(self.substitute_attribute_type),
                   opt_scheme = OptScheme(self.scheme),
                   opt_note_list = OptNoteList(self.note_list)
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
        name_content = self.name_content[0][1]                       \
                       if len(self.name_content) == 1                \
                           and self.name_content[0][0] == "generic"  \
                       else self.name_content
        return BeingRef(
                   BeingEntryContent(
                       name_content,
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
