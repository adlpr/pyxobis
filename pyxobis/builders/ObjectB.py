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
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("Object element does not have property 'scheme'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Object element does not have property 'usage'")
    def build(self):
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        class_attribute = None
        if self.class_ is not None and self.role in Object.ROLES_2:
            class_attribute = ClassAttribute(self.class_)
        return Object(
                   role = self.role,
                   object_entry_content = ObjectEntryContent(
                       GenericName(name_content),
                       qualifiers
                   ),
                   class_ = self.class_,
                   class_attribute = class_attribute,
                   type_ = self.type,
                   entry_group_attributes = self.entry_group_attributes,
                   variants = self.variants,
                   note_list = note_list
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
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        note_list = NoteList(self.note_list) if self.note_list else None
        return ObjectVariantEntry(
                   ObjectEntryContent(
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
        name_content = self.name_content
        if len(name_content) == 1:
            name_content = name_content[0]
        qualifiers = Qualifiers(self.qualifiers) if self.qualifiers else None
        return ObjectRef(
                   ObjectEntryContent(
                       GenericName(name_content),  # either NameContent or list of NameContents
                       qualifiers
                   ),
                   link_attributes = self.link_attributes
               )
