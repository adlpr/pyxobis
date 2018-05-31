#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class WorkBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Work element.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple)
    #    MISSING: set_scheme, set_usage
    # ADDITIONAL: set_holdings
    def __init__(self):
        super().__init__()
        # holdings
        self.holdings = VersionsHoldingsOpt()
    def add_name(self, *args, **kwargs):
        super().add_name_tuple(*args, **kwargs)
    def set_scheme(self, *args, **kwargs):
        raise AttributeError("Work element does not have property 'scheme'")
    def set_usage(self, *args, **kwargs):
        raise AttributeError("Work element does not have property 'usage'")
    def set_holdings(self, versions_holdings_opt):
        # input should be a VersionsHoldingsOpt object (TEMPORARY UNTIL BETTER SCHEME).
        # use VersionsHoldingsBuilder to build.
        # assert isinstance(versions_holdings_opt, VersionsHoldingsOpt)
        self.holdings = versions_holdings_opt
    def add_variant(self, variant):
        # input should be a WorkVariantEntry. use WorkVariantBuilder to build.
        assert isinstance(variant, WorkVariantEntry)
        super().add_variant(variant)
    def build(self):
        name_content = self.name_content[0][1]                       \
                       if len(self.name_content) == 1                \
                           and self.name_content[0][0] == "generic"  \
                       else self.name_content
        return Work(
                   WorkContent(
                       WorkEntryContent(
                           name_content,
                           QualifiersOpt(self.qualifiers)
                       ),
                       class_ = self.class_,
                       variants = self.variants,
                       opt_note_list = OptNoteList(self.note_list)
                   ),
                   role  = self.role,
                   type_ = self.type,
                   versions_holdings_opt = self.holdings
               )


class WorkVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a WorkVariantEntry.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple)
    #    MISSING: -
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_name(self, *args, **kwargs):
        super().add_name_tuple(*args, **kwargs)
    def build(self):
        name_content = self.name_content[0][1]                       \
                       if len(self.name_content) == 1                \
                           and self.name_content[0][0] == "generic"  \
                       else self.name_content
        return WorkVariantEntry(
                   WorkEntryContent(
                       name_content,
                       QualifiersOpt(self.qualifiers)
                   ),
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   substitute_attribute = SubstituteAttribute(self.substitute_attribute_type),
                   opt_scheme = OptScheme(self.scheme),
                   opt_note_list = OptNoteList(self.note_list)
               )


class WorkRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a WorkRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple)
    #    MISSING: add_subdivision_link
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
    def add_name(self, *args, **kwargs):
        super().add_name_tuple(*args, **kwargs)
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("Work element ref does not have subdivisions")
    def build(self):
        name_content = self.name_content[0][1]                       \
                       if len(self.name_content) == 1                \
                           and self.name_content[0][0] == "generic"  \
                       else self.name_content
        return WorkRef(
                   WorkEntryContent(
                       name_content,
                       QualifiersOpt(self.qualifiers)
                   ),
                   link_attributes = self.link_attributes
               )
