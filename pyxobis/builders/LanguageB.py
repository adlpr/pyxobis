#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class LanguageBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Language element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_role, set_scheme
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def set_role(self, *args, **kwargs):
        raise AttributeError("Language element does not have property 'role'")
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("Language element does not have property 'scheme'")
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        class_attribute = None if self.class_ is None else ClassAttribute(self.class_)
        note_list = NoteList(self.note_list) if self.note_list else None
        return Language(
                   LanguageEntryContent(
                       GenericName(name_content),
                       qualifiers
                   ),
                   type_     = self.type,
                   class_attribute = class_attribute,
                   usage     = self.usage,
                   entry_group_attributes = self.entry_group_attributes,
                   variants  = self.variants,
                   note_list = note_list
               )


class LanguageVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a LanguageVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_scheme
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("LanguageVariant element does not have property 'scheme'")
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        return LanguageVariantEntry(
                   LanguageEntryContent(
                       GenericName(name_content),
                       qualifiers
                   ),
                   variant_attributes = self.variant_attributes,
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = self.substitute_attribute,
                   entry_group_attributes = self.entry_group_attributes,
                   note_list = note_list
               )


class LanguageRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a LanguageRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: -
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        subdivisions = Subdivisions(self.subdivision_link_contents) if self.subdivision_link_contents else None
        return LanguageRef(
                   LanguageEntryContent(
                       GenericName(name_content),
                       qualifiers
                   ),
                   link_attributes = self.link_attributes,
                   subdivisions = subdivisions
               )
