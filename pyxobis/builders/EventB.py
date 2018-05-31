#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class EventBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Event element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_role, set_usage
    # ADDITIONAL: add_prequalifier
    def __init__(self):
        super().__init__()
        self.prequalifiers = []
    def set_role(self, *args, **kwargs):
        raise AttributeError("Event element does not have property 'role'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Event element does not have property 'usage'")
    def add_prequalifier(self, prequalifier):
        # assert isinstance(qualifier, PreQualifierRefElement)
        self.prequalifiers.append(prequalifier)
    def add_variant(self, variant):
        # input should be an EventVariantEntry. use EventVariantBuilder to build.
        assert isinstance(variant, EventVariantEntry)
        super().add_variant(variant)
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return Event(
                   EventEntryContent(
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


class EventVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a EventVariantEntry.
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
        return EventVariantEntry(
                   EventEntryContent(
                       GenericName(name_content),
                       PreQualifiersOpt(self.prequalifiers),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = SubstituteAttribute(self.substitute_attribute_type),
                   opt_scheme    = OptScheme(self.scheme),
                   opt_note_list = OptNoteList(self.note_list)
               )


class EventRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a EventRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_subdivision_link
    # ADDITIONAL: add_prequalifier
    def __init__(self):
        super().__init__()
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("Event element ref does not have subdivisions")
    def add_prequalifier(self, prequalifier):
        # assert isinstance(qualifier, PreQualifierRefElement)
        self.prequalifiers.append(prequalifier)
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return EventRef(
                   EventEntryContent(
                       GenericName(name_content),
                       PreQualifiersOpt(self.prequalifiers),
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
