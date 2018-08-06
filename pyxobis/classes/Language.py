#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Language(PrincipalElement):
    """
    languagePE |=
        element xobis:language {
            attribute type {
                string "natural"
                | string "constructed"
                | string "script"
            }?,
            optClass,
            attribute usage { "subdivision" }?,
            element xobis:entry { optEntryGroupAttributes, langEntryContent },
            element xobis:variants { anyVariant+ }?,
            optNoteList
        }
    """
    TYPES = ["natural", "constructed", "script", None]
    USAGES = ["subdivision", None]
    def __init__(self, language_entry_content, \
                       type_=None, opt_class=OptClass(), usage=None, \
                       opt_entry_group_attributes=OptEntryGroupAttributes(), \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert type_ in Language.TYPES
        self.type = type_
        assert isinstance(opt_class, OptClass)
        self.opt_class = opt_class
        assert usage in Language.USAGES
        self.usage = usage
        # for entry element
        assert isinstance(opt_entry_group_attributes, OptEntryGroupAttributes)
        self.opt_entry_group_attributes = opt_entry_group_attributes
        assert isinstance(language_entry_content, LanguageEntryContent)
        self.language_entry_content = language_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        language_attrs = {}
        if self.type:
            language_attrs['type'] = self.type
        opt_class_attrs = self.opt_class.serialize_xml()
        language_attrs.update(opt_class_attrs)
        if self.usage:
            language_attrs['usage'] = self.usage
        language_e = E('language', **language_attrs)
        # entry element
        opt_entry_group_attributes_attrs = self.opt_entry_group_attributes.serialize_xml()
        entry_e = E('entry', **opt_entry_group_attributes_attrs)
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
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            language_e.append(opt_note_list_e)
        return language_e


class LanguageEntryContent(Component):
    """
    langEntryContent |=
        element xobis:name { nameContent },
        qualifiersOpt
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


class LanguageVariantEntry(VariantEntry):
    """
    languageVariant |=
        element xobis:language {
            optVariantAttributes,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { optSubstituteAttribute, optEntryGroupAttributes, langEntryContent },
            optNoteList
        }
    """
    def __init__(self, language_entry_content, \
                       opt_variant_attributes=OptVariantAttributes(), \
                       type_=None, time_or_duration_ref=None, \
                       opt_substitute_attribute=OptSubstituteAttribute(), \
                       opt_entry_group_attributes=OptEntryGroupAttributes(), \
                       opt_note_list=OptNoteList()):
        assert isinstance(opt_variant_attributes, OptVariantAttributes)
        self.opt_variant_attributes = opt_variant_attributes
        if type_ is not None:
            assert isinstance(type_, GenericType)
        self.type = type_
        if time_or_duration_ref is not None:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(opt_entry_group_attributes, OptEntryGroupAttributes)
        self.opt_entry_group_attributes = opt_entry_group_attributes
        assert isinstance(language_entry_content, LanguageEntryContent)
        self.language_entry_content = language_entry_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        opt_variant_attributes_attrs = self.opt_variant_attributes.serialize_xml()
        variant_e = E('language', **opt_variant_attributes_attrs)
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
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        entry_attrs.update(opt_substitute_attribute_attrs)
        opt_entry_group_attributes_attrs = self.opt_entry_group_attributes.serialize_xml()
        entry_attrs.update(opt_entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        language_entry_content_elements = self.language_entry_content.serialize_xml()
        entry_e.extend(language_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e


class LanguageRef(RefElement):
    """
    languageRef |= element xobis:language { linkAttributes?, optSubstituteAttribute, langEntryContent, optSubdivisions }
    """
    def __init__(self, language_entry_content, link_attributes=None, opt_substitute_attribute=OptSubstituteAttribute(), opt_subdivision=OptSubdivisions()):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(language_entry_content, LanguageEntryContent)
        self.language_entry_content = language_entry_content
        assert isinstance(opt_subdivision, OptSubdivisions)
        self.opt_subdivision = opt_subdivision
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        attrs.update(opt_substitute_attribute_attrs)
        variant_e = E('language', **attrs)
        language_entry_content_elements = self.language_entry_content.serialize_xml()
        variant_e.extend(language_entry_content_elements)
        opt_subdivision_elements = self.opt_subdivision.serialize_xml()
        variant_e.extend(opt_subdivision_elements)
        return variant_e
