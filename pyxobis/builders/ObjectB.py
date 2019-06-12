#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class ObjectBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Object element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_scheme, set_usage
    # ADDITIONAL: set_organization
    def __init__(self):
        super().__init__()
        self.org_ref = None
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("Object element does not have property 'scheme'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Object element does not have property 'usage'")
    def set_organization(self, org_ref):
        self.org_ref = org_ref
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return Object(
                   ObjectContent(
                       ObjectEntryContent(
                           GenericName(name_content),
                           QualifiersOpt(self.qualifiers)
                       ),
                       type_ = self.type,
                       org_ref = self.org_ref,
                       opt_entry_group_attributes = self.opt_entry_group_attributes,
                       variants = self.variants,
                       opt_note_list = OptNoteList(self.note_list)
                   ),
                   role   = self.role,
                   class_ = self.class_,
                   opt_class = OptClass(self.class_)
               )


class ObjectVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a ObjectVariantEntry.
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
        return ObjectVariantEntry(
                   ObjectEntryContent(
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


class ObjectRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a ObjectRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_subdivision_link
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("Object element ref does not have subdivisions")
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return ObjectRef(
                   ObjectEntryContent(
                       GenericName(name_content),  # either NameContent or list of NameContents
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
