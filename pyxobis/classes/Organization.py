#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import Component, PrincipalElement, PrequalifierRefElement, VariantEntry, GenericName, SchemeAttribute, ClassAttribute, GenericType, LinkAttributes, SubstituteAttribute, NoteList, Prequalifiers, Qualifiers, VariantAttributes, EntryGroupAttributes
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Organization(PrincipalElement):
    """
    orgPE |=
        element xobis:organization {
            attribute type {
                ( string "business"
                | string "government"
                | string "nonprofit"
                | string "other" )
            }?,
            classAttribute?,
            element xobis:entry {
                schemeAttribute?,
                entryGroupAttributes?,
                orgEntryContent
            },
            element xobis:variants { anyVariant+ }?,
            noteList?
        }
    """
    TYPES = ["business", "government", "nonprofit", "other", None]
    def __init__(self, organization_entry_content, \
                       type_=None, class_attribute=None, \
                       scheme_attribute=None, \
                       entry_group_attributes=None, \
                       variants=[], note_list=None):
        # attributes
        assert type_ in Organization.TYPES
        self.type = type_
        if class_attribute is not None:
            assert isinstance(class_attribute, ClassAttribute)
        self.class_attribute = class_attribute
        # for entry element
        if scheme_attribute is not None:
            assert isinstance(scheme_attribute, SchemeAttribute)
        self.scheme_attribute = scheme_attribute
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(organization_entry_content, OrganizationEntryContent)
        self.organization_entry_content = organization_entry_content
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
        organization_attrs = {}
        if self.type:
            organization_attrs['type'] = self.type
        if self.class_attribute is not None:
            class_attribute_attrs = self.class_attribute.serialize_xml()
            organization_attrs.update(class_attribute_attrs)
        organization_e = E('organization', **organization_attrs)
        # entry element
        entry_attrs = {}
        if self.scheme_attribute is not None:
            scheme_attribute_attrs = self.scheme_attribute.serialize_xml()
            entry_attrs.update(scheme_attribute_attrs)
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        organization_entry_content_elements = self.organization_entry_content.serialize_xml()
        entry_e.extend(organization_entry_content_elements)
        organization_e.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            organization_e.append(variants_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            organization_e.append(note_list_e)
        return organization_e


class OrganizationEntryContent(Component):
    """
    orgEntryContent |= prequalifiers?, genericName, qualifiers?
    """
    def __init__(self, generic_name, prequalifiers=None, qualifiers=None):
        if prequalifiers is not None:
            assert isinstance(prequalifiers, Prequalifiers)
        self.prequalifiers = prequalifiers
        assert isinstance(generic_name, GenericName)
        self.generic_name = generic_name
        if qualifiers is not None:
            assert isinstance(qualifiers, Qualifiers)
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns list of one, two, or three Elements.
        elements = []
        if self.prequalifiers is not None:
            prequalifiers_e = self.prequalifiers.serialize_xml()
            elements.append(prequalifiers_e)
        name_e = self.generic_name.serialize_xml()
        elements.append(name_e)
        if self.qualifiers is not None:
            qualifiers_e = self.qualifiers.serialize_xml()
            elements.append(qualifiers_e)
        return elements


class OrganizationVariantEntry(VariantEntry):
    """
    orgVariant |=
        element xobis:organization {
            variantAttributes?,
            genericType?,
            ( timeRef | durationRef )?,
            element xobis:entry {
                substituteAttribute?,
                schemeAttribute?,
                entryGroupAttributes?,
                orgEntryContent
            },
            noteList?
        }
    """
    def __init__(self, organization_entry_content, \
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
        assert isinstance(organization_entry_content, OrganizationEntryContent)
        self.organization_entry_content = organization_entry_content
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        variant_attributes_attrs = {}
        if self.variant_attributes is not None:
            variant_attributes_attrs = self.variant_attributes.serialize_xml()
        variant_e = E('organization', **variant_attributes_attrs)
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
        organization_entry_content_elements = self.organization_entry_content.serialize_xml()
        entry_e.extend(organization_entry_content_elements)
        variant_e.append(entry_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            variant_e.append(note_list_e)
        return variant_e



class OrganizationRef(PrequalifierRefElement):
    """
    orgRef |=
        element xobis:organization {
            linkAttributes?, substituteAttribute?, orgEntryContent
        }
    """
    def __init__(self, organization_entry_content,
                       link_attributes=None, substitute_attribute=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(organization_entry_content, OrganizationEntryContent)
        self.organization_entry_content = organization_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            attrs.update(substitute_attribute_attrs)
        org_ref_e = E('organization', **attrs)
        organization_entry_content_elements = self.organization_entry_content.serialize_xml()
        org_ref_e.extend(organization_entry_content_elements)
        return org_ref_e
