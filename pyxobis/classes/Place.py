#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Place(PrincipalElement):
    """
    placePE |=
        element xobis:place {
            roleAttributes,
            attribute type { string "natural" | string "constructed" | string "jurisdictional" }?,
            classAttribute?,
            attribute usage { string "subdivision" }?,
            element xobis:entry { schemeAttribute?, entryGroupAttributes?, placeEntryContent },
            element xobis:variants { anyVariant+ }?,
            noteList?
        }
    """
    TYPES = ["natural", "constructed", "jurisdictional", None]
    USAGES = ["subdivision", None]
    def __init__(self, role_attributes, place_entry_content, \
                       type_=None, class_attribute=None, usage=None, \
                       scheme_attribute=None, \
                       entry_group_attributes=None, \
                       variants=[], note_list=None):
        # attributes
        assert isinstance(role_attributes, RoleAttributes)
        self.role_attributes = role_attributes
        assert type_ in Place.TYPES
        self.type = type_
        if class_attribute is not None:
            assert isinstance(class_attribute, ClassAttribute)
        self.class_attribute = class_attribute
        assert usage in Place.USAGES
        self.usage = usage
        # for entry element
        if scheme_attribute is not None:
            assert isinstance(scheme_attribute, SchemeAttribute)
        self.scheme_attribute = scheme_attribute
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(place_entry_content, PlaceEntryContent)
        self.place_entry_content = place_entry_content
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
        place_attrs = {}
        role_attributes_attrs = self.role_attributes.serialize_xml()
        place_attrs.update(role_attributes_attrs)
        if self.type:
            place_attrs['type'] = self.type
        if self.class_attribute is not None:
            class_attribute_attrs = self.class_attribute.serialize_xml()
            place_attrs.update(class_attribute_attrs)
        if self.usage:
            place_attrs['usage'] = self.usage
        place_e = E('place', **place_attrs)
        # entry element
        entry_attrs = {}
        if self.scheme_attribute is not None:
            scheme_attribute_attrs = self.scheme_attribute.serialize_xml()
            entry_attrs.update(scheme_attribute_attrs)
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        place_entry_content_elements = self.place_entry_content.serialize_xml()
        entry_e.extend(place_entry_content_elements)
        place_e.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            place_e.append(variants_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            place_e.append(note_list_e)
        return place_e


class PlaceEntryContent(Component):
    """
    placeEntryContent |= genericName, qualifiers?
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


class PlaceVariantEntry(VariantEntry):
    """
    placeVariant |=
        element xobis:place {
            variantAttributes?,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { substituteAttribute?, schemeAttribute?, entryGroupAttributes?, placeEntryContent },
            noteList?
        }
    """
    def __init__(self, place_entry_content, \
                       variant_attributes=None, \
                       type_=None, time_or_duration_ref=None, \
                       substitute_attribute=None, \
                       scheme_attribute=None, \
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
        if scheme_attribute is not None:
            assert isinstance(scheme_attribute, SchemeAttribute)
        self.scheme_attribute = scheme_attribute
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(place_entry_content, PlaceEntryContent)
        self.place_entry_content = place_entry_content
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        variant_attributes_attrs = {}
        if self.variant_attributes is not None:
            variant_attributes_attrs = self.variant_attributes.serialize_xml()
        variant_e = E('place', **variant_attributes_attrs)
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
        if self.scheme_attribute is not None:
            scheme_attribute_attrs = self.scheme_attribute.serialize_xml()
            entry_attrs.update(scheme_attribute_attrs)
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        place_entry_content_elements = self.place_entry_content.serialize_xml()
        entry_e.extend(place_entry_content_elements)
        variant_e.append(entry_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            variant_e.append(note_list_e)
        return variant_e


class PlaceRef(PrequalifierRefElement):
    """
    placeRef |= element xobis:place { linkAttributes?, substituteAttribute?, placeEntryContent }
    """
    def __init__(self, place_entry_content, \
                       link_attributes=None, substitute_attribute=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(place_entry_content, PlaceEntryContent)
        self.place_entry_content = place_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            attrs.update(substitute_attribute_attrs)
        place_ref_e = E('place', **attrs)
        place_entry_content_elements = self.place_entry_content.serialize_xml()
        place_ref_e.extend(place_entry_content_elements)
        return place_ref_e
