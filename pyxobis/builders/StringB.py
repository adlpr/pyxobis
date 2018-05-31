#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class StringBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS String element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_role, set_scheme, set_usage
    # ADDITIONAL: set_grammar
    def __init__(self):
        super().__init__()
        self.grammar = None
    def set_role(self, *args, **kwargs):
        raise AttributeError("String element does not have property 'role'")
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("String element does not have property 'scheme'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("String element does not have property 'usage'")
    def set_grammar(self, new_grammar):
        self.grammar = new_grammar
    def add_variant(self, variant):
        # input should be an StringVariantEntry. use StringVariantBuilder to build.
        assert isinstance(variant, StringVariantEntry)
        super().add_variant(variant)
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return String(
                   StringEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_    = self.type,
                   class_   = self.class_,
                   grammar  = self.grammar,
                   variants = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
               )


class StringVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a StringVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_scheme
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("StringVariant element does not have property 'scheme'")
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return StringVariantEntry(
                   StringEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = SubstituteAttribute(self.substitute_attribute_type),
                   opt_note_list = OptNoteList(self.note_list)
               )


class StringRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a StringRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_subdivision_link
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("String element ref does not have subdivisions")
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return StringRef(
                   StringEntryContent(
                       GenericName(name_content),
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
