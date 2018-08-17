#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class WorkBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Work element.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple + extra)
    #    MISSING: set_scheme, set_usage
    # ADDITIONAL: set_holdings
    def __init__(self):
        super().__init__()
        # holdings
        self.holdings = VersionsHoldingsOpt()
        self.contents = []
    def add_name(self, *args, **kwargs):
        # If already a name, dump name(s) + qualifier(s) to self.contents
        # before adding another
        self.__dump_to_content()
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
    def __dump_to_content(self):
        # Put name(s) + qualifier(s) into self.contents and reset them
        if self.name_content:
            self.contents.append((self.name_content, QualifiersOpt(self.qualifiers)))
            self.name_content, self.qualifiers = [], []
    def build(self):
        # Dump current name(s)/qualifier(s) to content
        self.__dump_to_content()
        # Build the right content object
        if len(self.contents) == 1 and self.contents[0][0][0][0] == "generic":
            content = WorkEntryContentSingleGeneric(self.contents[0][0][0][1], self.contents[0][1])
        else:
            content = [WorkEntryContentPart(*content_part) for content_part in self.contents]
        return Work(
                   WorkContent(
                       WorkEntryContent( content ),
                       class_ = self.class_,
                       opt_entry_group_attributes = self.opt_entry_group_attributes,
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
    #  ALTERNATE: add_name (--> add_name_tuple + extra)
    #    MISSING: -
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
        self.contents = []
    def add_name(self, *args, **kwargs):
        # If already a name, dump name(s) + qualifier(s) to self.contents
        # before adding another
        self.__dump_to_content()
        super().add_name_tuple(*args, **kwargs)
    def __dump_to_content(self):
        # Put name(s) + qualifier(s) into self.contents and reset them
        if self.name_content:
            self.contents.append((self.name_content, QualifiersOpt(self.qualifiers)))
            self.name_content, self.qualifiers = [], []
    def build(self):
        # Dump current name(s)/qualifier(s) to content
        self.__dump_to_content()
        # Build the right content object
        if len(self.contents) == 1 and self.contents[0][0][0][0] == "generic":
            content = WorkEntryContentSingleGeneric(self.contents[0][0][0][1], self.contents[0][1])
        else:
            content = [WorkEntryContentPart(*content_part) for content_part in self.contents]
        return WorkVariantEntry(
                   WorkEntryContent( content ),
                   opt_variant_attributes = self.opt_variant_attributes,
                   type_ = self.type,
                   time_or_duration_ref = self.time_or_duration_ref,
                   opt_substitute_attribute = OptSubstituteAttribute(self.substitute_attribute),
                   opt_scheme = OptScheme(self.scheme),
                   opt_entry_group_attributes = self.opt_entry_group_attributes,
                   opt_note_list = OptNoteList(self.note_list)
               )


class WorkRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a WorkRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: add_name (--> add_name_tuple + extra)
    #    MISSING: add_subdivision_link
    # ADDITIONAL: -
    def __init__(self):
        super().__init__()
        self.contents = []
    def add_name(self, *args, **kwargs):
        # If already a name, dump name(s) + qualifier(s) to self.contents
        # before adding another
        self.__dump_to_content()
        super().add_name_tuple(*args, **kwargs)
    def __dump_to_content(self):
        # Put name(s) + qualifier(s) into self.contents and reset them
        if self.name_content:
            self.contents.append((self.name_content, QualifiersOpt(self.qualifiers)))
            self.name_content, self.qualifiers = [], []
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("Work element ref does not have subdivisions")
    def build(self):
        # Dump current name(s)/qualifier(s) to content
        self.__dump_to_content()
        # Build the right content object
        if len(self.contents) == 1 and self.contents[0][0][0][0] == "generic":
            content = WorkEntryContentSingleGeneric(self.contents[0][0][0][1], self.contents[0][1])
        else:
            content = [WorkEntryContentPart(*content_part) for content_part in self.contents]
        return WorkRef(
                   WorkEntryContent( content ),
                   link_attributes = self.link_attributes
               )
