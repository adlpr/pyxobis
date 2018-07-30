#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class LanguageBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Language element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_type, set_role, set_scheme
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def set_type(self, *args, **kwargs):
        raise AttributeError("Language element does not have property 'type'")
    def set_role(self, *args, **kwargs):
        raise AttributeError("Language element does not have property 'role'")
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("Language element does not have property 'scheme'")
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return Language(
                   LanguageEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   opt_class = OptClass(self.class_),
                   usage     = self.usage,
                   variants  = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return LanguageVariantEntry(
                   LanguageEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   opt_substitute_attribute = OptSubstituteAttribute(self.substitute_attribute),
                   opt_note_list = OptNoteList(self.note_list)
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
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return LanguageRef(
                   LanguageEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes,
                   opt_subdivision = OptSubdivisions(self.subdivision_link_contents)
               )
