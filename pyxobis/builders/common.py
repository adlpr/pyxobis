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
    def add_name(self, name_text, lang=None, translit=None, nonfiling=0):
        self.name_content.append(
            NameContent(name_text, lang, translit, nonfiling)
        )
    def add_name_tuple(self, name_text, type_="generic", lang=None, translit=None, nonfiling=0):
        self.name_content.append((
            type_,
            NameContent(name_text, lang=lang, translit=translit, nonfiling=nonfiling)
        ))
    def add_qualifier(self, qualifier):
        # assert isinstance(qualifier, RefElement)
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
    # def add_qualifier(self, *args, **kwargs):
    #     # assert isinstance(qualifier, RefElement)
    #     super().add_qualifier(*args, **kwargs)
    def add_variant(self, variant):
        self.variants.append(variant)
    def add_note(self, content_text, content_lang=None, class_=None, link_title=None, href_URI=None, role_URI=None):
        self.note_list.append(Note(
            Content(content_text, content_lang),
            class_ = class_,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = LinkAttributes(link_title, XLinkAnyURI(href_URI) if href_URI else None) \
                              if link_title else None,
            xlink_role = XLinkAnyURI(role_URI) if role_URI else None
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


"""
FOR PRINCIPAL ELEMENT VARIANT BUILDERS:

COMMON ATTRIBUTES
* self.name_content
* self.qualifiers
self.type
self.time_or_duration_ref
self.substitute_attribute_type
self.scheme
self.note_list

COMMON METHODS
* add_name  [+ add_name_tuple]
* add_qualifier
set_type
set_time_or_duration_ref
set_substitute_attribute_type
set_scheme
add_note
"""

class PrincipalElementVariantBuilder(Builder):
    """
    Superclass for XOBIS PE object variant builders.
    """
    def __init__(self):
        super().__init__()
        self.type = Type()
        self.time_or_duration_ref = None
        self.substitute_attribute_type = None
        self.scheme = None
        self.note_list = []     # Note objs
    def set_type(self, link_title, role_URI, href_URI=None):
        self.type = Type(
                        LinkAttributes(
                            link_title,
                            xlink_href = XLinkAnyURI( href_URI ) \
                                         if href_URI else None
                        ),
                        xlink_role = XLinkAnyURI( role_URI ) \
                                     if role_URI else None
                    )
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
    def set_substitute_attribute_type(self, substitute_attribute_type):
        # string
        self.substitute_attribute_type = substitute_attribute_type
    def set_scheme(self, new_scheme):
        # string
        self.scheme = new_scheme
    def add_note(self, content_text, content_lang=None, class_=None, link_title=None, href_URI=None, role_URI=None):
        if link_title:
            link_attributes = LinkAttributes(link_title, XLinkAnyURI(href_URI) if href_URI else None)
        else:
            link_attributes = None
        self.note_list.append(Note(
            Content(content_text, content_lang),
            class_ = class_,  # ["transcription", "annotation", "documentation", "description", None]
            link_attributes = link_attributes,
            xlink_role = XLinkAnyURI(role_URI) if role_URI else None
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
        self.subdivision_link_contents = None
    def set_link(self, link_title, href_URI=None):
        self.link_attributes = LinkAttributes(
                                   link_title,
                                   XLinkAnyURI(href_URI) if href_URI else None
                               )
    def add_subdivision_link(self, content_text, content_lang=None, link_title=None, href_URI=None, substitute=None):
        self.subdivision_link_contents.append(
            LinkContent(
                Content(content_text, content_lang),
                link_attributes = LinkAttributes(
                                      link_title,
                                      XLinkAnyURI(href_URI) if href_URI else None
                                  ) if link_title else None,
                substitute = substitute
            )
        )

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @                         VERSIONS AND HOLDINGS                              @
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class VersionsHoldingsBuilder(Builder):
    """
    @@@@@@@@@@@@@@@@@@@@@@
         TEMPORARY!!
    @@@@@@@@@@@@@@@@@@@@@@
    Interface for constructing an element suitable for describing
    versions/holdings of a Work or Object.
    """
    def __init__(self):
        # list of either 1+ Version objs, or a single Holdings
        self.versions = []
        self.is_holdings_only = False
    def set_holdings(self, text, lang=None):
        if self.versions:
            print("WARNING: versions list is non-empty!\nemptying to set holdings: {}".format(text))
        self.versions = [ Holdings( Content(text, lang) ) ]
        self.is_holdings_only = True
    def add_version(self, version_text, holdings_text, version_lang=None, version_translit=None, version_nonfiling=0, holdings_lang=None, qualifiers=[], notes=[]):
        if not all(isinstance(version, Version) for version in self.versions):
            print("WARNING: versions list contains non-Version!\nemptying to add version: {}".format(version_text))
            self.versions = []
        self.versions.append( Version(
            NameContent(
                version_text,
                lang=version_lang,
                translit=version_translit,
                nonfiling=version_nonfiling
            ),
            Holdings( Content(holdings_text, holdings_lang) ),
            qualifiers_opt=QualifiersOpt(qualifiers),
            # @@@@@@ NO EASY BUILDER FOR NOTE OBJS HERE RIGHT NOW, MAKE THEM YOURSELF @@@@@@
            opt_note_list=OptNoteList(notes)
        ) )
        self.is_holdings_only = False
    def build(self):
        versions_holdings = self.versions[0]  \
                            if self.is_holdings_only   \
                            else self.versions
        return VersionsHoldingsOpt(versions_holdings)
