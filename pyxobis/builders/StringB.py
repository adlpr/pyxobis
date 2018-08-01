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
    # ADDITIONAL: add_pos
    def __init__(self):
        super().__init__()
        self.parts_of_speech = []
    def set_role(self, *args, **kwargs):
        raise AttributeError("String element does not have property 'role'")
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("String element does not have property 'scheme'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("String element does not have property 'usage'")
    def add_pos(self, pos_text, pos_lang=None, xlink_title=None, xlink_href=None):
        self.parts_of_speech.append(
            PartOfSpeech(
                GenericContent(pos_text, pos_lang),
                LinkAttributes(xlink_title, xlink_href) if xlink_title else None
            )
        )
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return String(
                   StringEntryContent(
                       GenericName(name_content),
                       self.parts_of_speech,
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_    = self.type,
                   class_   = self.class_,
                   # grammar  = self.grammar,
                   variants = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
               )


class StringVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a StringVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: set_scheme
    # ADDITIONAL: add_pos
    def __init__(self):
        super().__init__()
        self.parts_of_speech = []
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("StringVariant element does not have property 'scheme'")
    def add_pos(self, pos_text, pos_lang=None, xlink_title=None, xlink_href=None):
        self.parts_of_speech.append(
            PartOfSpeech(
                GenericContent(pos_text, pos_lang),
                LinkAttributes(xlink_title, xlink_href) if xlink_title else None
            )
        )
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return StringVariantEntry(
                   StringEntryContent(
                       GenericName(name_content),
                       self.parts_of_speech,
                       QualifiersOpt(self.qualifiers)
                   ),
                   opt_variant_attributes = self.opt_variant_attributes,
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   opt_substitute_attribute = OptSubstituteAttribute(self.substitute_attribute),
                   opt_note_list = OptNoteList(self.note_list)
               )


class StringRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a StringRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_subdivision_link
    # ADDITIONAL: add_pos
    def __init__(self):
        super().__init__()
        self.parts_of_speech = []
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("String element ref does not have subdivisions")
    def add_pos(self, pos_text, pos_lang=None, xlink_title=None, xlink_href=None):
        self.parts_of_speech.append(
            PartOfSpeech(
                GenericContent(pos_text, pos_lang),
                LinkAttributes(xlink_title, xlink_href) if xlink_title else None
            )
        )
    def build(self):
        name_content = self.name_content[0]               \
                       if len(self.name_content) == 1     \
                       else self.name_content
        return StringRef(
                   StringEntryContent(
                       GenericName(name_content),
                       self.parts_of_speech,
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
