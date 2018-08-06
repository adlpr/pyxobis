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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return Place(
                   RoleAttributes(self.role),
                   PlaceEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   opt_class = OptClass(self.class_),
                   usage = self.usage,
                   opt_scheme = OptScheme(self.scheme),
                   opt_entry_group_attributes = self.opt_entry_group_attributes,
                   variants = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return PlaceVariantEntry(
                   PlaceEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   opt_variant_attributes = self.opt_variant_attributes,
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   opt_substitute_attribute = OptSubstituteAttribute(self.substitute_attribute),
                   opt_scheme = OptScheme(self.scheme),
                   opt_entry_group_attributes = self.opt_entry_group_attributes,
                   opt_note_list = OptNoteList(self.note_list)
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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return PlaceRef(
                   PlaceEntryContent(
                       GenericName(name_content),  # either NameContent or list of NameContents
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
