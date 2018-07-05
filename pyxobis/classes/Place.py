#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Place(PrincipalElement):
    """
    placePE |=
        element xobis:place {
            roleAttributes_,
            attribute type { string "natural" | string "constructed" | string "jurisdictional" }?,
            optClass_,
            attribute usage { string "subdivision" }?,
            element xobis:entry { optScheme_, _placeEntryContent },
            element xobis:variants { anyVariant+ }?,
            optNoteList_
        }
    """
    TYPES = ["natural", "constructed", "jurisdictional", None]
    USAGES = ["subdivision", None]
    def __init__(self, role_attributes, place_entry_content, \
                       type_=None, opt_class=OptClass(), usage=None, \
                       opt_scheme=OptScheme(), \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert isinstance(role_attributes, RoleAttributes)
        self.role_attributes = role_attributes
        assert type_ in Place.TYPES
        self.type = type_
        assert isinstance(opt_class, OptClass)
        self.opt_class = opt_class
        assert usage in Place.USAGES
        self.usage = usage
        # for entry element
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(place_entry_content, PlaceEntryContent)
        self.place_entry_content = place_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        place_attrs = {}
        role_attributes_attrs = self.role_attributes.serialize_xml()
        place_attrs.update(role_attributes_attrs)
        if self.type:
            place_attrs['type'] = self.type
        opt_class_attrs = self.opt_class.serialize_xml()
        place_attrs.update(opt_class_attrs)
        if self.usage:
            place_attrs['usage'] = self.usage
        place_e = E('place', **place_attrs)
        # entry element
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_e = E('entry', **opt_scheme_attrs)
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
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            place_e.append(opt_note_list_e)
        return place_e




class PlaceEntryContent(Component):
    """
    _placeEntryContent |= genericName, qualifiersOpt
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


class PlaceVariantEntry(VariantEntry):
    """
    placeVariant |=
        element xobis:place {
            type_?,
            (timeRef | durationRef)?,
            element xobis:entry { substituteAttribute, optScheme_, _placeEntryContent },
            optNoteList_
        }
    """
    def __init__(self, place_entry_content, \
                       type_=Type(), time_or_duration_ref=None, \
                       substitute_attribute=SubstituteAttribute(), \
                       opt_scheme=OptScheme(), \
                       opt_note_list=OptNoteList()):
        assert isinstance(type_, Type)
        self.type = type_
        if time_or_duration_ref:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(place_entry_content, PlaceEntryContent)
        self.place_entry_content = place_entry_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        variant_e = E('place')
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
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_attrs.update(opt_scheme_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        place_entry_content_elements = self.place_entry_content.serialize_xml()
        entry_e.extend(place_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e



class PlaceRef(PreQualifierRefElement):
    """
    placeRef |= element xobis:place { linkAttributes_?, _placeEntryContent }
    """
    def __init__(self, place_entry_content, link_attributes=None):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(place_entry_content, PlaceEntryContent)
        self.place_entry_content = place_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        variant_e = E('place', **attrs)
        place_entry_content_elements = self.place_entry_content.serialize_xml()
        variant_e.extend(place_entry_content_elements)
        return variant_e
