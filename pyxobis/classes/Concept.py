#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Language import LanguageRef
from .Place import PlaceRef
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Concept(PrincipalElement):
    """
    conceptPE |=
        element xobis:concept {
            attribute type {
                string "abstract" | string "collective" | string "control" | string "specific"
            }?,
            (attribute usage { string "subdivision" },
             attribute subtype {
                 string "general" | string "form" | string "topical" | string "unspecified"
             })?,
            element xobis:entry { schemeAttribute?, entryGroupAttributes?, conceptEntryContent },
            element xobis:variants { anyVariant+ }?,
            noteList?
        }
    """
    TYPES = ["abstract", "collective", "control", "specific", None]
    USAGES = ["subdivision", None]
    SUBTYPES = ["general", "form", "topical", "unspecified", None]
    def __init__(self, concept_entry_content, \
                       type_=None, usage=None, subtype=None, \
                       scheme_attribute=None, entry_group_attributes=None, \
                       variants=[], note_list=None):
        # attributes
        assert type_ in Concept.TYPES
        self.type = type_
        assert not (bool(usage) ^ bool(subtype)), "Need both or neither: usage / subtype"
        assert usage in Concept.USAGES
        self.usage = usage
        assert subtype in Concept.SUBTYPES
        self.subtype = subtype
        # for entry element
        if scheme_attribute is not None:
            assert isinstance(scheme_attribute, SchemeAttribute)
        self.scheme_attribute = scheme_attribute
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(concept_entry_content, ConceptEntryContent)
        self.concept_entry_content = concept_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        concept_e = E('concept')
        # attributes
        if self.type:
            concept_e.attrib['type'] = self.type
        if self.usage:
            concept_e.attrib['usage'] = self.usage
            concept_e.attrib['subtype'] = self.subtype
        # entry element
        entry_attrs = {}
        if self.scheme_attribute is not None:
            scheme_attribute_attrs = self.scheme_attribute.serialize_xml()
            entry_attrs.update(scheme_attribute_attrs)
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        concept_entry_content_elements = self.concept_entry_content.serialize_xml()
        entry_e.extend(concept_entry_content_elements)
        concept_e.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            concept_e.append(variants_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            concept_e.append(note_list_e)
        return concept_e




class ConceptEntryContent(Component):
    """
    conceptEntryContent |= genericName, qualifiers?
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


class ConceptVariantEntry(VariantEntry):
    """
    conceptVariant |=
        element xobis:concept {
            variantAttributes?,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { substituteAttribute?, schemeAttribute?, entryGroupAttributes?, conceptEntryContent },
            noteList?
        }
    """
    def __init__(self, concept_entry_content, \
                       variant_attributes=None, type_=None, \
                       time_or_duration_ref=None, \
                       substitute_attribute=None, scheme_attribute=None, \
                       entry_group_attributes=None, note_list=None):
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
        assert isinstance(concept_entry_content, ConceptEntryContent)
        self.concept_entry_content = concept_entry_content
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        variant_attributes_attrs = {}
        if self.variant_attributes is not None:
            variant_attributes_attrs = self.variant_attributes.serialize_xml()
        variant_e = E('concept', **variant_attributes_attrs)
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
        if self.scheme_attribute is not None:
            scheme_attribute_attrs = self.scheme_attribute.serialize_xml()
            entry_attrs.update(scheme_attribute_attrs)
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        concept_entry_content_elements = self.concept_entry_content.serialize_xml()
        entry_e.extend(concept_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            variant_e.append(note_list_e)
        return variant_e



class ConceptRef(RefElement):
    """
    conceptRef |=
        element xobis:concept {
            linkAttributes?,
            substituteAttribute?,
            conceptEntryContent,
            subdivisions?
        }
    """
    def __init__(self, concept_entry_content, \
                       link_attributes=None, substitute_attribute=None, \
                       subdivisions=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(concept_entry_content, ConceptEntryContent)
        self.concept_entry_content = concept_entry_content
        if subdivisions is not None:
            assert isinstance(subdivisions, Subdivisions)
        self.subdivisions = subdivisions
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            attrs.update(substitute_attribute_attrs)
        concept_ref_e = E('concept', **attrs)
        concept_entry_content_elements = self.concept_entry_content.serialize_xml()
        concept_ref_e.extend(concept_entry_content_elements)
        if self.subdivisions is not None:
            subdivisions_e = self.subdivisions.serialize_xml()
            concept_ref_e.append(subdivisions_e)
        return concept_ref_e


class Subdivisions(Component):
    """
    subdivisions |=
        element xobis:subdivisions {
            ( conceptRef | languageRef | placeRef | timeRef | durationRef )+
        }
    """
    VALID_REFS = (ConceptRef, LanguageRef, PlaceRef, TimeRef, DurationRef)
    def __init__(self, subdivisions):
        assert subdivisions, "Subdivisions must contain one or more Refs"
        for subdivision in subdivisions:
            assert type(subdivision) in Subdivisions.VALID_REFS, \
                f"Invalid subdivision type: {type(subdivision)}"
        self.subdivisions = subdivisions
    def serialize_xml(self):
        # Returns an Element.
        subdivisions_e = E('subdivisions')
        for subdivision in self.subdivisions:
            ref_e = subdivision.serialize_xml()
            subdivisions_e.append(ref_e)
        return subdivisions_e
