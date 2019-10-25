#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class OrganizationBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Organization element.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_qualifier
    #    MISSING: set_role, set_usage
    # ADDITIONAL: add_prequalifier (?)
    def __init__(self):
        super().__init__()
        self.prequalifiers = []
    def set_role(self, *args, **kwargs):
        raise AttributeError("Organization element does not have property 'role'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Organization element does not have property 'usage'")
    # def add_prequalifier(self, prequalifier):
    #     self.prequalifiers.append(prequalifier)
    def add_qualifier(self, qualifier):
        if not self.name_content:
            self.prequalifiers.append(qualifier)
        else:
            self.qualifiers.append(qualifier)
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        prequalifiers = Prequalifiers(self.prequalifiers) if self.prequalifiers else None
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        class_attribute = None if self.class_ is None else ClassAttribute(self.class_)
        note_list = NoteList(self.note_list) if self.note_list else None
        return Organization(
                   OrganizationEntryContent(
                       GenericName(name_content),
                       prequalifiers,
                       qualifiers
                   ),
                   type_ = self.type,
                   class_attribute  = class_attribute,
                   scheme_attribute = self.scheme,
                   entry_group_attributes = self.entry_group_attributes,
                   variants   = self.variants,
                   note_list = note_list
               )


class OrganizationVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a OrganizationVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_qualifier
    #    MISSING: -
    # ADDITIONAL: add_prequalifier (?)
    def __init__(self):
        super().__init__()
        self.prequalifiers = []
    # def add_prequalifier(self, prequalifier):
    #     self.prequalifiers.append(prequalifier)
    def add_qualifier(self, qualifier):
        if not self.name_content:
            self.prequalifiers.append(qualifier)
        else:
            self.qualifiers.append(qualifier)
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        prequalifiers = Prequalifiers(self.prequalifiers) if self.prequalifiers else None
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        return OrganizationVariantEntry(
                   OrganizationEntryContent(
                       GenericName(name_content),
                       prequalifiers,
                       qualifiers
                   ),
                   variant_attributes = self.variant_attributes,
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = self.substitute_attribute,
                   scheme_attribute    = self.scheme,
                   entry_group_attributes = self.entry_group_attributes,
                   note_list = note_list
               )


class OrganizationRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a OrganizationRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_qualifier
    #    MISSING: -
    # ADDITIONAL: add_prequalifier (?)
    def __init__(self):
        super().__init__()
        self.prequalifiers = []
    # def add_prequalifier(self, prequalifier):
    #     self.prequalifiers.append(prequalifier)
    def add_qualifier(self, qualifier):
        if not self.name_content:
            self.prequalifiers.append(qualifier)
        else:
            self.qualifiers.append(qualifier)
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        prequalifiers = Prequalifiers(self.prequalifiers) if self.prequalifiers else None
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        return OrganizationRef(
                   OrganizationEntryContent(
                       GenericName(name_content),
                       prequalifiers,
                       qualifiers
                   ),
                   link_attributes = self.link_attributes
               )
