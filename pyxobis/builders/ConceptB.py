#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class ConceptBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Concept element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_role, set_class
    # ADDITIONAL: set_subtype
    def __init__(self):
        super().__init__()
        self.subtype = None
    def set_role(self, *args, **kwargs):
        raise AttributeError("Concept element does not have property 'role'")
    def set_class(self, *args, **kwargs):
        raise AttributeError("Concept element does not have property 'class'")
    def set_subtype(self, new_subtype):
        self.subtype = new_subtype
    def build(self):
        name_content = self.name_content
        if len(self.name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        return Concept(
                   ConceptEntryContent(
                       GenericName(name_content),
                       qualifiers
                   ),
                   type_ = self.type,
                   usage = self.usage,
                   subtype = self.subtype,
                   scheme_attribute = self.scheme,
                   entry_group_attributes = self.entry_group_attributes,
                   variants = self.variants,
                   note_list = note_list
               )


class ConceptVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a ConceptVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: -
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def build(self):
        name_content = self.name_content
        if len(self.name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        return ConceptVariantEntry(
                   ConceptEntryContent(
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


class ConceptRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a ConceptRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: -
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def build(self):
        name_content = self.name_content
        if len(self.name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        subdivisions = Subdivisions(self.subdivision_link_contents) \
            if self.subdivision_link_contents else None
        return ConceptRef(
                   ConceptEntryContent(
                       GenericName(name_content),
                       qualifiers
                   ),
                   link_attributes = self.link_attributes,
                   subdivisions = subdivisions
               )
