#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class OrganizationBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Organization element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_role, set_usage
    # ADDITIONAL: add_prequalifier
    def __init__(self):
        super().__init__()
        self.prequalifiers = []
    def set_role(self, *args, **kwargs):
        raise AttributeError("Organization element does not have property 'role'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Organization element does not have property 'usage'")
    def add_prequalifier(self, prequalifier):
        # assert isinstance(qualifier, PreQualifierRefElement)
        self.prequalifiers.append(prequalifier)
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return Organization(
                   OrganizationEntryContent(
                       GenericName(name_content),
                       PreQualifiersOpt(self.prequalifiers),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   opt_class  = OptClass(self.class_),
                   opt_scheme = OptScheme(self.scheme),
                   variants   = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
               )


class OrganizationVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a OrganizationVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: -
    # ADDITIONAL: add_prequalifier
    def __init__(self):
        super().__init__()
        self.prequalifiers = []
    def add_prequalifier(self, prequalifier):
        # assert isinstance(qualifier, PreQualifierRefElement)
        self.prequalifiers.append(prequalifier)
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return OrganizationVariantEntry(
                   OrganizationEntryContent(
                       GenericName(name_content),
                       PreQualifiersOpt(self.prequalifiers),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   opt_substitute_attribute = OptSubstituteAttribute(self.substitute_attribute),
                   opt_scheme    = OptScheme(self.scheme),
                   opt_note_list = OptNoteList(self.note_list)
               )


class OrganizationRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a OrganizationRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: -
    # ADDITIONAL: add_prequalifier
    def __init__(self):
        super().__init__()
        self.prequalifiers = []
    def add_prequalifier(self, prequalifier):
        # assert isinstance(qualifier, PreQualifierRefElement)
        self.prequalifiers.append(prequalifier)
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return OrganizationRef(
                   OrganizationEntryContent(
                       GenericName(name_content),
                       PreQualifiersOpt(self.prequalifiers),
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes,
                   opt_subdivision = OptSubdivisions(self.subdivision_link_contents)
               )
