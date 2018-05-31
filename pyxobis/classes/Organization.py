#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Organization(PrincipalElement):
    """
    orgPE |=
        element xobis:organization {
            attribute type {
                string "business" | string "government" | string "nonprofit" | string "other"
            }?,
            optClass_,
            element xobis:entry { optScheme_, _orgEntryContent },
            element xobis:variant {
                type_?,
                (timeRef | durationRef)?,
                element xobis:entry { substituteAttribute, optScheme_, _orgEntryContent },
                optNoteList_
            }*,
            optNoteList_
        }
    """
    TYPES = ["business", "government", "nonprofit", "other", None]
    def __init__(self, organization_entry_content, \
                       type_=None, opt_class=OptClass(), \
                       opt_scheme=OptScheme(), \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert type_ in Organization.TYPES
        self.type = type_
        assert isinstance(opt_class, OptClass)
        self.opt_class = opt_class
        # for entry element
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(organization_entry_content, OrganizationEntryContent)
        self.organization_entry_content = organization_entry_content
        # for variant elements
        assert all(isinstance(variant, OrganizationVariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        organization_attrs = {}
        if self.type:
            organization_attrs['type'] = self.type
        opt_class_attrs = self.opt_class.serialize_xml()
        organization_attrs.update(opt_class_attrs)
        organization_e = E('organization', **organization_attrs)
        # entry element
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_e = E('entry', **opt_scheme_attrs)
        organization_entry_content_elements = self.organization_entry_content.serialize_xml()
        entry_e.extend(organization_entry_content_elements)
        organization_e.append(entry_e)
        # variant elements
        variant_elements = [variant.serialize_xml() for variant in self.variants]
        organization_e.extend(variant_elements)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            organization_e.append(opt_note_list_e)
        return organization_e




class OrganizationEntryContent(Component):
    """
    _orgEntryContent |= preQualifiersOpt, genericName, qualifiersOpt
    """
    def __init__(self, generic_name, pre_qualifiers_opt=PreQualifiersOpt(), qualifiers_opt=QualifiersOpt()):
        assert isinstance(generic_name, GenericName)
        self.generic_name = generic_name
        assert isinstance(pre_qualifiers_opt, PreQualifiersOpt)
        self.pre_qualifiers_opt = pre_qualifiers_opt
        assert isinstance(qualifiers_opt, QualifiersOpt)
        self.qualifiers_opt = qualifiers_opt
    def serialize_xml(self):
        # Returns list of one, two, or three Elements.
        elements = []
        pre_qualifiers_e = self.pre_qualifiers_opt.serialize_xml()
        if pre_qualifiers_e is not None:
            elements.append(pre_qualifiers_e)
        name_e = self.generic_name.serialize_xml()
        elements.append(name_e)
        qualifiers_e = self.qualifiers_opt.serialize_xml()
        if qualifiers_e is not None:
            elements.append(qualifiers_e)
        return elements


class OrganizationVariantEntry(Component):
    """
    element xobis:variant {
        type_?,
        (timeRef | durationRef)?,
        element xobis:entry { substituteAttribute, optScheme_, _orgEntryContent },
        optNoteList_
    }
    """
    def __init__(self, organization_entry_content, \
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
        assert isinstance(organization_entry_content, OrganizationEntryContent)
        self.organization_entry_content = organization_entry_content
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
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_attrs.update(opt_scheme_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        organization_entry_content_elements = self.organization_entry_content.serialize_xml()
        entry_e.extend(organization_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e



class OrganizationRef(PreQualifierRefElement):
    """
    orgRef |= element xobis:organization { linkAttributes_?, _orgEntryContent, optSubdivision_ }
    """
    def __init__(self, organization_entry_content, link_attributes=None, opt_subdivision=OptSubdivision()):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(organization_entry_content, OrganizationEntryContent)
        self.organization_entry_content = organization_entry_content
        assert isinstance(opt_subdivision, OptSubdivision)
        self.opt_subdivision = opt_subdivision
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        variant_e = E('organization', **attrs)
        organization_entry_content_elements = self.organization_entry_content.serialize_xml()
        variant_e.extend(organization_entry_content_elements)
        opt_subdivision_elements = self.opt_subdivision.serialize_xml()
        variant_e.extend(opt_subdivision_elements)
        return variant_e
