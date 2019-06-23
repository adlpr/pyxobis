#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class PlaceBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Place element.
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
        class_attribute = None if self.class_ is None else ClassAttribute(self.class_)
        note_list = NoteList(self.note_list) if self.note_list else None
        return Place(
                   RoleAttributes(self.role),
                   PlaceEntryContent(
                       GenericName(name_content),
                       qualifiers
                   ),
                   type_ = self.type,
                   class_attribute = class_attribute,
                   usage = self.usage,
                   scheme_attribute = self.scheme,
                   entry_group_attributes = self.entry_group_attributes,
                   variants = self.variants,
                   note_list = note_list
               )


class PlaceVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a PlaceVariantEntry.
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
        note_list = NoteList(self.note_list) if self.note_list else None
        return PlaceVariantEntry(
                   PlaceEntryContent(
                       GenericName(name_content),
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


class PlaceRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a PlaceRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_subdivision_link
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("Place element ref does not have subdivisions")
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        return PlaceRef(
                   PlaceEntryContent(
                       GenericName(name_content),  # either NameContent or list of NameContents
                       qualifiers
                   ),
                   link_attributes = self.link_attributes
               )
