#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Language(PrincipalElement):
    """
    languagePE |=
        element xobis:language {
            attribute type {
                string "natural"
                | string "constructed"
                | string "script"
            }?,
            classAttribute?,
            attribute usage { "subdivision" }?,
            element xobis:entry { entryGroupAttributes?, langEntryContent },
            element xobis:variants { anyVariant+ }?,
            noteList?
        }
    """
    TYPES = ["natural", "constructed", "script", None]
    USAGES = ["subdivision", None]
    def __init__(self, language_entry_content, \
                       type_=None, class_attribute=None, usage=None, \
                       entry_group_attributes=None, \
                       variants=[], note_list=None):
        # attributes
        assert type_ in Language.TYPES
        self.type = type_
        if class_attribute is not None:
            assert isinstance(class_attribute, ClassAttribute)
        self.class_attribute = class_attribute
        assert usage in Language.USAGES
        self.usage = usage
        # for entry element
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(language_entry_content, LanguageEntryContent)
        self.language_entry_content = language_entry_content
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
        language_attrs = {}
        if self.type:
            language_attrs['type'] = self.type
        if self.class_attribute is not None:
            class_attribute_attrs = self.class_attribute.serialize_xml()
            language_attrs.update(class_attribute_attrs)
        if self.usage:
            language_attrs['usage'] = self.usage
        language_e = E('language', **language_attrs)
        # entry element
        entry_attrs = {}
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        language_entry_content_elements = self.language_entry_content.serialize_xml()
        entry_e.extend(language_entry_content_elements)
        language_e.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            language_e.append(variants_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            language_e.append(note_list_e)
        return language_e


class LanguageEntryContent(Component):
    """
    langEntryContent |=
        element xobis:name { nameContent },
        qualifiers?
    """
    def __init__(self, generic_name, qualifiers=None):
        assert isinstance(generic_name, GenericName)
        self.generic_name = generic_name
        if qualifiers is not None:
            assert isinstance(qualifiers, Qualifiers)
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns list of one or two Elements.
        name_e = self.generic_name.serialize_xml()
        elements = [name_e]
        if self.qualifiers is not None:
            qualifiers_e = self.qualifiers.serialize_xml()
            elements.append(qualifiers_e)
        return elements


class LanguageVariantEntry(VariantEntry):
    """
    languageVariant |=
        element xobis:language {
            variantAttributes?,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { substituteAttribute?, entryGroupAttributes?, langEntryContent },
            noteList?
        }
    """
    def __init__(self, language_entry_content, \
                       variant_attributes=None, type_=None, \
                       time_or_duration_ref=None, \
                       substitute_attribute=None, entry_group_attributes=None, \
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
        assert isinstance(language_entry_content, LanguageEntryContent)
        self.language_entry_content = language_entry_content
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        variant_attributes_attrs = {}
        if self.variant_attributes is not None:
            variant_attributes_attrs = self.variant_attributes.serialize_xml()
        variant_e = E('language', **variant_attributes_attrs)
        # type
        if self.type is not None:
            type_e = self.type.serialize_xml()
            variant_e.append(type_e)
        # time/duration ref
        if self.time_or_duration_ref:
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
        language_entry_content_elements = self.language_entry_content.serialize_xml()
        entry_e.extend(language_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            variant_e.append(note_list_e)
        return variant_e


class LanguageRef(RefElement):
    """
    languageRef |=
        element xobis:language {
            linkAttributes?, substituteAttribute?, langEntryContent
        }
    """
    def __init__(self, language_entry_content, \
                       link_attributes=None, substitute_attribute=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(language_entry_content, LanguageEntryContent)
        self.language_entry_content = language_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            attrs.update(substitute_attribute_attrs)
        language_ref_e = E('language', **attrs)
        language_entry_content_elements = self.language_entry_content.serialize_xml()
        language_ref_e.extend(language_entry_content_elements)
        return language_ref_e
