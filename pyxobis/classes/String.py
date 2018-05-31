#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class String(PrincipalElement):
    """
    stringPE |=
        element xobis:string {
            attribute type { string "textual" | string "numeric" | string "mixed" }?,
            ((attribute class { string "word" },
              attribute grammar {
                  string "noun"
                  | string "verb"
                  | string "pronoun"
                  | string "adjective"
                  | string "adverb"
                  | string "preposition"
                  | string "conjunction"
                  | string "interjection"
              }?)
             | attribute class { string "phrase" })?,
            element xobis:entry { _stringEntryContent },
            element xobis:variant {
                type_?,
                (timeRef | durationRef)?,
                element xobis:entry { substituteAttribute, _stringEntryContent },
                optNoteList_
            }*,
            optNoteList_
        }
    """
    TYPES = ["textual", "numeric", "mixed", None]
    CLASSES = ["word", "phrase", None]
    GRAMMARS = ["noun", "verb", "pronoun", "adjective", "adverb", "preposition", "conjunction", "interjection", None]
    def __init__(self, string_entry_content, \
                       type_=None, class_=None, grammar=None, \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert type_ in String.TYPES
        self.type = type_
        assert class_ in String.CLASSES
        self.class_ = class_
        if grammar:
            assert self.class_ == "word"
            assert grammar in String.GRAMMARS
            self.grammar = grammar
        # for entry element
        assert isinstance(string_entry_content, StringEntryContent)
        self.string_entry_content = string_entry_content
        # for variant elements
        assert all(isinstance(variant, StringVariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        string_attrs = {}
        if self.type:
            string_attrs['type'] = self.type
        if self.class_:
            string_attrs['class'] = self.class_
            if self.grammar:
                string_attrs['grammar'] = self.grammar
        string_e = E('string', **string_attrs)
        # entry element
        entry_e = E('entry')
        string_entry_content_elements = self.string_entry_content.serialize_xml()
        entry_e.extend(string_entry_content_elements)
        string_e.append(entry_e)
        # variant elements
        variant_elements = [variant.serialize_xml() for variant in self.variants]
        string_e.extend(variant_elements)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            string_e.append(opt_note_list_e)
        return string_e




class StringEntryContent(Component):
    """
    _stringEntryContent |= genericName, qualifiersOpt
    """
    def __init__(self, generic_name, qualifiers_opt=QualifiersOpt()):
        assert isinstance(generic_name, GenericName)
        self.generic_name = generic_name
        assert isinstance(qualifiers_opt, QualifiersOpt)
        self.qualifiers_opt = qualifiers_opt
    def serialize_xml(self):
        # Returns list of one or two Elements.
        name_e = self.generic_name.serialize_xml()
        elements = [name_e]
        qualifiers_e = self.qualifiers_opt.serialize_xml()
        if qualifiers_e is not None:
            elements.append(qualifiers_e)
        return elements


class StringVariantEntry(Component):
    """
    element xobis:variant {
        type_?,
        (timeRef | durationRef)?,
        element xobis:entry { substituteAttribute, _stringEntryContent },
        optNoteList_
    }
    """
    def __init__(self, string_entry_content, \
                       type_=Type(), time_or_duration_ref=None, \
                       substitute_attribute=SubstituteAttribute(), \
                       opt_note_list=OptNoteList()):
        assert isinstance(type_, Type)
        self.type = type_
        if time_or_duration_ref:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(string_entry_content, StringEntryContent)
        self.string_entry_content = string_entry_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        variant_e = E('variant')
        # type
        type_e = self.type.serialize_xml()
        if type_e is not None:
            variant_e.append(type_e)
        # time/duration ref
        if self.time_or_duration_ref:
            time_or_duration_ref_e = self.time_or_duration_ref.serialize_xml()
            variant_e.append(time_or_duration_ref_e)
        # entry element
        # --> attrs
        entry_attrs = {}
        substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
        entry_attrs.update(substitute_attribute_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        string_entry_content_elements = self.string_entry_content.serialize_xml()
        entry_e.extend(string_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e


class StringRef(RefElement):
    """
    stringRef |= element xobis:string { linkAttributes_?, _stringEntryContent }
    """
    def __init__(self, string_entry_content, link_attributes=None):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(string_entry_content, StringEntryContent)
        self.string_entry_content = string_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        variant_e = E('string', **attrs)
        string_entry_content_elements = self.string_entry_content.serialize_xml()
        variant_e.extend(string_entry_content_elements)
        return variant_e
