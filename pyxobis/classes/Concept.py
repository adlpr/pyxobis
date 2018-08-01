#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


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
            element xobis:entry { optScheme, conceptEntryContent },
            element xobis:variants { anyVariant+ }?,
            optNoteList
        }
    """
    TYPES = ["abstract", "collective", "control", "specific", None]
    USAGES = ["subdivision", None]
    SUBTYPES = ["general", "form", "topical", "unspecified", None]
    def __init__(self, concept_entry_content, \
                       type_=None, usage=None, subtype=None, \
                       opt_scheme=OptScheme(), \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert type_ in Concept.TYPES
        self.type = type_
        assert not (bool(usage) ^ bool(subtype)), "Need both or neither: usage / subtype"
        assert usage in Concept.USAGES
        self.usage = usage
        assert subtype in Concept.SUBTYPES
        self.subtype = subtype
        # for entry element
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(concept_entry_content, ConceptEntryContent)
        self.concept_entry_content = concept_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
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
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_e = E('entry', **opt_scheme_attrs)
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
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            concept_e.append(opt_note_list_e)
        return concept_e




class ConceptEntryContent(Component):
    """
    _conceptEntryContent |= genericName, qualifiersOpt
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


class ConceptVariantEntry(VariantEntry):
    """
    conceptVariant |=
        element xobis:concept {
            optVariantAttributes,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { optSubstituteAttribute, optScheme, conceptEntryContent },
            optNoteList
        }
    """
    def __init__(self, concept_entry_content, \
                       opt_variant_attributes=OptVariantAttributes(), \
                       type_=None, time_or_duration_ref=None, \
                       opt_substitute_attribute=OptSubstituteAttribute(), \
                       opt_scheme=OptScheme(), \
                       opt_note_list=OptNoteList()):
        assert isinstance(opt_variant_attributes, OptVariantAttributes)
        self.opt_variant_attributes = opt_variant_attributes
        if type_ is not None:
            assert isinstance(type_, GenericType)
        self.type = type_
        if time_or_duration_ref:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(concept_entry_content, ConceptEntryContent)
        self.concept_entry_content = concept_entry_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        opt_variant_attributes_attrs = self.opt_variant_attributes.serialize_xml()
        variant_e = E('concept', **opt_variant_attributes_attrs)
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
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_attrs.update(opt_scheme_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        concept_entry_content_elements = self.concept_entry_content.serialize_xml()
        entry_e.extend(concept_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e



class ConceptRef(RefElement):
    """
    conceptRef |= element xobis:concept { linkAttributes?, optSubstituteAttribute, conceptEntryContent, optSubdivisions }
    """
    def __init__(self, concept_entry_content, link_attributes=None, opt_substitute_attribute=OptSubstituteAttribute(), opt_subdivision=OptSubdivisions()):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(concept_entry_content, ConceptEntryContent)
        self.concept_entry_content = concept_entry_content
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
        variant_e = E('concept', **attrs)
        concept_entry_content_elements = self.concept_entry_content.serialize_xml()
        variant_e.extend(concept_entry_content_elements)
        opt_subdivision_elements = self.opt_subdivision.serialize_xml()
        variant_e.extend(opt_subdivision_elements)
        return variant_e
