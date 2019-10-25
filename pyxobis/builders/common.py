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
        self.name_content = []    # NameContent objs (parts of entry name)
        self.qualifiers = []      # RefElement objs
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
self.entry_group_attributes
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
        # should PE main entry be preferred=True unless otherwise noted?
        # self.entry_group_attributes = EntryGroupAttributes(id=None, group=None, preferred=True)
        self.entry_group_attributes = EntryGroupAttributes()
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
        self.scheme = SchemeAttribute(new_scheme)
    def set_class(self, new_class):
        self.class_ = new_class
    def set_usage(self, new_usage):
        self.usage = new_usage
    def set_entry_group_attributes(self, id=None, group=None, preferred=None):
        self.entry_group_attributes = EntryGroupAttributes(id, group, preferred)


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
self.variant_attributes
self.entry_group_attributes

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
        self.variant_attributes = None
        self.entry_group_attributes = EntryGroupAttributes()
        self.type = None
        self.time_or_duration_ref = None
        self.substitute_attribute = None
        self.scheme = None
        self.note_list = []     # Note objs
    def set_included(self, included):
        if included is not None:
            self.variant_attributes = VariantAttributes(included)
    def set_entry_group_attributes(self, id=None, group=None, preferred=None):
        self.entry_group_attributes = EntryGroupAttributes(id, group, preferred)
    def set_type(self, link_title, set_URI, href_URI=None):
        href = XSDAnyURI(href_URI) if href_URI is not None else None
        set_ref = XSDAnyURI(set_URI) if set_URI is not None else None
        self.type = GenericType(
                        LinkAttributes(
                            link_title,
                            href = href
                        ),
                        set_ref = set_ref
                    )
    def set_time_or_duration_ref(self, time_or_duration_ref):
        # assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
    def set_substitute_attribute(self, substitute_attribute):
        # str
        self.substitute_attribute = SubstituteAttribute(substitute_attribute)
    def set_scheme(self, new_scheme):
        # str
        self.scheme = SchemeAttribute(new_scheme)
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

COMMON METHODS
* add_name  [+ add_name_tuple]
* add_qualifier
set_link
"""

class PrincipalElementRefBuilder(Builder):
    """
    Superclass for XOBIS PE object ref builders.
    """
    def __init__(self):
        super().__init__()
        self.link_attributes = None    # LinkAttributes
    def set_link(self, link_title, href_URI=None):
        self.link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
