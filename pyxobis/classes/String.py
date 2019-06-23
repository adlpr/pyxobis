#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class String(PrincipalElement):
    """
    stringPE |=
        element xobis:string {
            attribute type { string "textual" | string "numeric" | string "mixed" }?,
            attribute class { string "word" | string "phrase" }?,
            element xobis:entry { entryGroupAttributes?, stringEntryContent },
            element xobis:variants { anyVariant+ }?,
            noteList?
        }
    """
    TYPES = ["textual", "numeric", "mixed", None]
    CLASSES = ["word", "phrase", None]
    def __init__(self, string_entry_content, \
                       type_=None, class_=None, \
                       entry_group_attributes=None, \
                       variants=[], note_list=None):
        # attributes
        assert type_ in String.TYPES
        self.type = type_
        assert class_ in String.CLASSES
        self.class_ = class_
        # for entry element
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(string_entry_content, StringEntryContent)
        self.string_entry_content = string_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        string_attrs = {}
        if self.type:
            string_attrs['type'] = self.type
        if self.class_:
            string_attrs['class'] = self.class_
        string_e = E('string', **string_attrs)
        # entry element
        entry_attrs = {}
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        string_entry_content_elements = self.string_entry_content.serialize_xml()
        entry_e.extend(string_entry_content_elements)
        string_e.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            string_e.append(variants_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            string_e.append(note_list_e)
        return string_e


class StringEntryContent(Component):
    """
    stringEntryContent |= genericName, partOfSpeech*, qualifiers?
    """
    def __init__(self, generic_name, parts_of_speech=[], qualifiers=None):
        assert isinstance(generic_name, GenericName)
        self.generic_name = generic_name
        assert all(isinstance(pos, PartOfSpeech) for pos in parts_of_speech)
        self.parts_of_speech = parts_of_speech
        if qualifiers is not None:
            assert isinstance(qualifiers, Qualifiers)
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns list of one or two Elements.
        name_e = self.generic_name.serialize_xml()
        elements = [name_e]
        pos_elements = [pos.serialize_xml() for pos in self.parts_of_speech]
        elements.extend(pos_elements)
        if self.qualifiers is not None:
            qualifiers_e = self.qualifiers.serialize_xml()
            elements.append(qualifiers_e)
        return elements


class PartOfSpeech(Component):
    """
    partOfSpeech |=
        element xobis:pos {
            linkAttributes?,
            genericContent
        }
    """
    def __init__(self, content, link_attributes=None):
        assert isinstance(content, GenericContent)
        self.content = content
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
    def serialize_xml(self):
        # Returns an Element.
        content_text, attrs = self.content.serialize_xml()
        if self.link_attributes is not None:
            link_attributes_attrs = elf.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        pos_e = E('pos', **attrs)
        pos_e.text = content_text
        return pos_e


class StringVariantEntry(VariantEntry):
    """
    stringVariant |=
        element xobis:string {
            variantAttributes?,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { substituteAttribute?, entryGroupAttributes?, stringEntryContent },
            noteList?
        }
    """
    def __init__(self, string_entry_content, \
                       variant_attributes=None, \
                       type_=None, time_or_duration_ref=None, \
                       substitute_attribute=None, \
                       entry_group_attributes=None, \
                       note_list=None):
        if variant_attributes is not None:
            assert isinstance(variant_attributes, VariantAttributes)
        self.variant_attributes = variant_attributes
        if type_ is not None:
            assert isinstance(type_, GenericType)
        self.type = type_
        if time_or_duration_ref is not None:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(string_entry_content, StringEntryContent)
        self.string_entry_content = string_entry_content
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        variant_attributes_attrs = {}
        if self.variant_attributes is not None:
            variant_attributes_attrs = self.variant_attributes.serialize_xml()
        variant_e = E('string', **variant_attributes_attrs)
        # type
        if self.type is not None:
            type_e = self.type.serialize_xml()
            variant_e.append(type_e)
        # time/duration ref
        if self.time_or_duration_ref is not None:
            time_or_duration_ref_e = self.time_or_duration_ref.serialize_xml()
            variant_e.append(time_or_duration_ref_e)
        # entry element
        # --> attrs
        entry_attrs = {}
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            entry_attrs.update(substitute_attribute_attrs)
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        string_entry_content_elements = self.string_entry_content.serialize_xml()
        entry_e.extend(string_entry_content_elements)
        variant_e.append(entry_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            variant_e.append(note_list_e)
        return variant_e


class StringRef(RefElement):
    """
    stringRef |= element xobis:string { linkAttributes?, substituteAttribute?, stringEntryContent }
    """
    def __init__(self, string_entry_content, link_attributes=None, substitute_attribute=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(string_entry_content, StringEntryContent)
        self.string_entry_content = string_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            attrs.update(substitute_attribute_attrs)
        string_ref_e = E('string', **attrs)
        string_entry_content_elements = self.string_entry_content.serialize_xml()
        string_ref_e.extend(string_entry_content_elements)
        return string_ref_e
