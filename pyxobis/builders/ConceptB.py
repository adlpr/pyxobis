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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return Concept(
                   ConceptEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   usage = self.usage,
                   subtype = self.subtype,
                   opt_scheme = OptScheme(self.scheme),
                   opt_entry_group_attributes = self.opt_entry_group_attributes,
                   variants = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return ConceptVariantEntry(
                   ConceptEntryContent(
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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return ConceptRef(
                   ConceptEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes,
                   opt_subdivision = OptSubdivisions(self.subdivision_link_contents)
               )
