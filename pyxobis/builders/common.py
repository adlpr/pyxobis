#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @                               SUPERCLASSES                                 @
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class Builder:
    """
    Superclass for all builders.
    """
    def __init__(self):
        self.name_content = []  # NameContent objs (parts of entry name)
        self.qualifiers = []     # RefElement objs
    def add_name(self, name_text, lang=None, script=None, nonfiling=0):
        self.name_content.append(
            NameContent(name_text, lang, script, nonfiling)
        )
    def add_name_tuple(self, name_text, type_="generic", lang=None, script=None, nonfiling=0):
        self.name_content.append((
            type_,
            NameContent(name_text, lang=lang, script=script, nonfiling=nonfiling)
        ))
    def add_qualifier(self, qualifier):
        self.qualifiers.append(qualifier)


"""
FOR PRINCIPAL ELEMENT BUILDERS:

COMMON ATTRIBUTES
* self.name_content
* self.qualifiers
self.variants
self.note_list
self.type
self.role
self.scheme
self.class_
self.usage
self.opt_entry_group_attributes
self.versions_holdings_opt

COMMON METHODS
* add_name
* add_qualifier
add_variant
add_note
set_type
set_role
set_scheme
set_class
set_usage
set_entry_group_attributes
set_holdings
"""

class PrincipalElementBuilder(Builder):
    """
    Superclass for XOBIS PE object builders.
    """
    def __init__(self):
        super().__init__()
        self.variants = []      # VariantEntry objs for appropriate PE
        self.note_list = []     # Note objs
        self.type = None
        self.role = None
        self.scheme = None
        self.class_ = None
        self.usage  = None
        # should PE main entry be preferred=true unless otherwise noted?
        # self.opt_entry_group_attributes = OptEntryGroupAttributes(id=None, group=None, preferred=True)
        self.opt_entry_group_attributes = OptEntryGroupAttributes()
    # def add_qualifier(self, *args, **kwargs):
    #     # assert isinstance(qualifier, RefElement)
    #     super().add_qualifier(*args, **kwargs)
    def add_variant(self, variant):
        self.variants.append(variant)
    def add_note(self, content_text, content_lang=None, role=None, link_title=None, href_URI=None, set_URI=None, type_link_title=None, type_href_URI=None, type_set_URI=None, source=[]):
        if not isinstance(source, list):
            source = [source]
        assert all(any(isinstance(source_part, valid_type) for valid_type in (OrganizationRef, WorkRef, str)) for source_part in source)
        self.note_list.append(Note(
            GenericContent(content_text, content_lang),
            role = role,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = LinkAttributes(link_title, XSDAnyURI(href_URI) if href_URI else None) \
                              if link_title else None,
            set_ref = XSDAnyURI(set_URI) if set_URI else None,
            generic_type = GenericType(
                               LinkAttributes(
                                   type_link_title,
                                   href = XSDAnyURI( type_href_URI ) \
                                                if type_href_URI else None
                               ),
                               set_ref = XSDAnyURI( type_set_URI ) \
                                         if type_set_URI else None
                           ) if type_link_title else None,
            source = source if isinstance(source, list) else [source]
        ))
    def set_type(self, new_type):
        self.type = new_type
    def set_role(self, new_role):
        self.role = new_role
    def set_scheme(self, new_scheme):
        self.scheme = new_scheme
    def set_class(self, new_class):
        self.class_ = new_class
    def set_usage(self, new_usage):
        self.usage = new_usage
    def set_entry_group_attributes(self, id=None, group=None, preferred=None):
        self.opt_entry_group_attributes = OptEntryGroupAttributes(id, group, preferred)


"""
FOR PRINCIPAL ELEMENT VARIANT BUILDERS:

COMMON ATTRIBUTES
* self.name_content
* self.qualifiers
self.type
self.time_or_duration_ref
self.substitute_attribute
self.scheme
self.note_list
self.opt_variant_attributes
self.opt_entry_group_attributes

COMMON METHODS
* add_name  [+ add_name_tuple]
* add_qualifier
set_included
set_entry_group_attributes
set_type
set_time_or_duration_ref
set_substitute_attribute
set_scheme
add_note
"""

class PrincipalElementVariantBuilder(Builder):
    """
    Superclass for XOBIS PE object variant builders.
    """
    def __init__(self):
        super().__init__()
        self.opt_variant_attributes = OptVariantAttributes()
        self.opt_entry_group_attributes = OptEntryGroupAttributes()
        self.type = None
        self.time_or_duration_ref = None
        self.substitute_attribute = None
        self.scheme = None
        self.note_list = []     # Note objs
    def set_included(self, included):
        self.opt_variant_attributes = OptVariantAttributes(included)
    def set_entry_group_attributes(self, id=None, group=None, preferred=None):
        self.opt_entry_group_attributes = OptEntryGroupAttributes(id, group, preferred)
    def set_type(self, link_title, set_URI, href_URI=None):
        self.type = GenericType(
                        LinkAttributes(
                            link_title,
                            href = XSDAnyURI( href_URI ) \
                                         if href_URI else None
                        ),
                        set_ref = XSDAnyURI( set_URI ) \
                                     if set_URI else None
                    )
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
    def set_substitute_attribute(self, substitute_attribute):
        # string
        self.substitute_attribute = substitute_attribute
    def set_scheme(self, new_scheme):
        # string
        self.scheme = new_scheme
    def add_note(self, content_text, content_lang=None, role=None, link_title=None, href_URI=None, set_URI=None, type_link_title=None, type_href_URI=None, type_set_URI=None, source=[]):
        if not isinstance(source, list):
            source = [source]
        assert all(any(isinstance(source_part, valid_type) for valid_type in (OrganizationRef, WorkRef, str)) for source_part in source)
        self.note_list.append(Note(
            GenericContent(content_text, content_lang),
            role = role,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = LinkAttributes(link_title, XSDAnyURI(href_URI) if href_URI else None) \
                              if link_title else None,
            set_ref = XSDAnyURI(set_URI) if set_URI else None,
            generic_type = GenericType(
                               LinkAttributes(
                                   type_link_title,
                                   href = XSDAnyURI( type_href_URI ) \
                                                if type_href_URI else None
                               ),
                               set_ref = XSDAnyURI( type_set_URI ) \
                                         if type_set_URI else None
                           ) if type_link_title else None,
            source = source if isinstance(source, list) else [source]
        ))


"""
FOR PRINCIPAL ELEMENT REF BUILDERS:

COMMON ATTRIBUTES
* self.name_content
* self.qualifiers
self.link_attributes
self.subdivision_link_contents

COMMON METHODS
* add_name  [+ add_name_tuple]
* add_qualifier
set_link
add_subdivision_link
"""

class PrincipalElementRefBuilder(Builder):
    """
    Superclass for XOBIS PE object ref builders.
    """
    def __init__(self):
        super().__init__()
        self.link_attributes = None  # LinkAttributes
        self.subdivision_link_contents = []
    def set_link(self, link_title, href_URI=None):
        self.link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
    def add_subdivision_link(self, content_text, content_lang=None, link_title=None, href_URI=None, substitute=None):
        self.subdivision_link_contents.append(
            SubdivisionContent(
                GenericContent(content_text, content_lang),
                link_attributes = LinkAttributes(
                                      link_title,
                                      XSDAnyURI(href_URI) if href_URI else None
                                  ) if link_title else None,
                opt_substitute_attribute = OptSubstituteAttribute(substitute)
            )
        )

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @                         VERSIONS AND HOLDINGS                              @
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# class VersionsHoldingsBuilder(Builder):
#     """
#     @@@@@@@@@@@@@@@@@@@@@@
#          TEMPORARY!!
#     @@@@@@@@@@@@@@@@@@@@@@
#     Interface for constructing an element suitable for describing
#     versions/holdings of a Work or Object.
#     """
#     def __init__(self):
#         # list of either 1+ Version objs, or a single Holdings
#         self.versions = []
#         self.is_holdings_only = False
#     def set_holdings(self, text, lang=None):
#         if self.versions:
#             print(f"WARNING: versions list is non-empty!\nemptying to set holdings: {text}")
#         self.versions = [ Holdings( GenericContent(text, lang) ) ]
#         self.is_holdings_only = True
#     def add_version(self, version_text, holdings_text, version_lang=None, version_script=None, version_nonfiling=0, holdings_lang=None, qualifiers=[], notes=[]):
#         if not all(isinstance(version, Version) for version in self.versions):
#             print(f"WARNING: versions list contains non-Version!\nemptying to add version: {version_text}")
#             self.versions = []
#         self.versions.append( Version(
#             NameContent(
#                 version_text,
#                 lang=version_lang,
#                 script=version_script,
#                 nonfiling=version_nonfiling
#             ),
#             Holdings( GenericContent(holdings_text, holdings_lang) ),
#             qualifiers_opt=QualifiersOpt(qualifiers),
#             # @@@@@@ NO EASY BUILDER FOR NOTE OBJS HERE RIGHT NOW, MAKE THEM YOURSELF @@@@@@
#             opt_note_list=OptNoteList(notes)
#         ) )
#         self.is_holdings_only = False
#     def build(self):
#         versions_holdings = self.versions[0]  \
#                             if self.is_holdings_only   \
#                             else self.versions
#         return VersionsHoldingsOpt(versions_holdings)
