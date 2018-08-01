#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Object(PrincipalElement):
    """
    objectPE |=
        element xobis:object {
            (attribute role { string "instance" | string "authority instance" },
             attribute class { string "individual" | string "collective" }?,
             objectContent,
             versionsHoldingsOpt)
            | (attribute role { string "authority" },
               optClass,
               objectContent)
        }
    """
    ROLES_1 = ["instance", "authority instance"]
    ROLES_2 = ["authority"]
    CLASSES_1 = ["individual", "collective", None]
    def __init__(self, object_content, role,
                       class_=None, \
                       opt_class=OptClass(), \
                       versions_holdings_opt=VersionsHoldingsOpt()):
        # attributes
        self.is_authority = role in Object.ROLES_2
        if self.is_authority:
            assert class_ is None
        else:
            assert role in Object.ROLES_1
            assert class_ in Object.CLASSES_1
        self.role = role
        self.class_ = class_
        assert isinstance(opt_class, OptClass)
        self.opt_class = opt_class
        # content
        assert isinstance(object_content, ObjectContent)
        self.object_content = object_content
        assert isinstance(versions_holdings_opt, VersionsHoldingsOpt)
        self.versions_holdings_opt = versions_holdings_opt
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        object_attrs = {}
        if self.role:
            object_attrs['role'] = self.role
        if self.class_:
            object_attrs['class'] = self.class_
        if self.is_authority:
            opt_class_attrs = self.opt_class.serialize_xml()
            object_attrs.update(opt_class_attrs)
        # content
        object_content_elements, object_content_attrs = self.object_content.serialize_xml()
        object_attrs.update(object_content_attrs)
        object_e = E('object', **object_attrs)
        object_e.extend(object_content_elements)
        if not self.is_authority:
            versions_holdings_opt_e = self.versions_holdings_opt.serialize_xml()
            if versions_holdings_opt_e is not None:
                object_e.append(versions_holdings_opt_e)
        return object_e


class ObjectContent(Component):
    """
    objectContent |=
        ((attribute type { string "natural" | string "crafted" }?,
          element xobis:entry {
              objectEntryContent,
              element xobis:organization {
                  linkAttributes,
                  element xobis:identifier { genericContent }?
              }
          })
         | (attribute type { string "manufactured" }?,
            element xobis:entry { objectEntryContent })),
        element xobis:variants { anyVariant+ }?,
        optNoteList
    """
    TYPES_1 = ["natural", "crafted", None]
    TYPES_2 = ["manufactured", None]
    def __init__(self, object_entry_content,
                       type_=None, organization_link_attributes=None, \
                       organization_id_content=None, \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        self.is_manufactured = not organization_link_attributes
        if self.is_manufactured:
            assert type_ in ObjectContent.TYPES_2, \
                "manufactured (no Org ID) Object type ({}) must be in: {}".format(type_, str(ObjectContent.TYPES_2))
        else:
            assert type_ in ObjectContent.TYPES_1, \
                "non-manufactured Object type ({}) must be in: {}".format(type_, str(ObjectContent.TYPES_1))
            assert isinstance(organization_link_attributes, LinkAttributes)
            if organization_id_content:
                assert isinstance(organization_id_content, GenericContent)
        self.type = type_
        # for entry element
        assert isinstance(object_entry_content, ObjectEntryContent)
        self.object_entry_content = object_entry_content
        self.organization_link_attributes = organization_link_attributes
        self.organization_id_content = organization_id_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns a list of one or more Elements, and a dict of parent attributes.
        # parent attributes
        content_attrs = {}
        if self.type:
            content_attrs['type'] = self.type
        # entry element
        elements = []
        entry_e = E('entry')
        object_entry_content_elements = self.object_entry_content.serialize_xml()
        entry_e.extend(object_entry_content_elements)
        if not self.is_manufactured:
            organization_link_attributes = self.organization_link_attributes.serialize_xml()
            organization_e = E('organization', **organization_link_attributes)
            if self.organization_id_content:
                organization_id_content_text, organization_id_content_attrs = self.organization_id_content.serialize_xml()
                organization_identifier_e = E('identifier', **organization_id_content_attrs)
                organization_identifier_e.text = organization_id_content_text
                organization_e.append(organization_identifier_e)
            entry_e.append(organization_e)
        elements.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            elements.append(variants_e)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            elements.append(opt_note_list_e)
        return elements, content_attrs



class ObjectEntryContent(Component):
    """
    objectEntryContent |= genericName, qualifiersOpt
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


class ObjectVariantEntry(VariantEntry):
    """
    objectVariant |=
        element xobis:object {
            optVariantAttributes,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { optSubstituteAttribute, optScheme, objectEntryContent },
            optNoteList
        }
    """
    def __init__(self, object_entry_content, \
                       opt_variant_group_attributes=OptVariantGroupAttributes(), \
                       type_=None, time_or_duration_ref=None, \
                       opt_substitute_attribute=OptSubstituteAttribute(), \
                       opt_scheme=OptScheme(), \
                       opt_note_list=OptNoteList()):
        assert isinstance(opt_variant_group_attributes, OptVariantGroupAttributes)
        self.opt_variant_group_attributes = opt_variant_group_attributes
        if type_ is not None:
            assert isinstance(type_, GenericType)
        self.type = type_
        if time_or_duration_ref is not None:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(object_entry_content, ObjectEntryContent)
        self.object_entry_content = object_entry_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        opt_variant_group_attributes_attrs = self.opt_variant_group_attributes.serialize_xml()
        variant_e = E('object', **opt_variant_group_attributes_attrs)
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
        object_entry_content_elements = self.object_entry_content.serialize_xml()
        entry_e.extend(object_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e


class ObjectRef(RefElement):
    """
    objectRef |= element xobis:object { linkAttributes?, optSubstituteAttribute, objectEntryContent }
    """
    def __init__(self, object_entry_content, link_attributes=None, opt_substitute_attribute=OptSubstituteAttribute()):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(object_entry_content, ObjectEntryContent)
        self.object_entry_content = object_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        attrs.update(opt_substitute_attribute_attrs)
        variant_e = E('object', **attrs)
        object_entry_content_elements = self.object_entry_content.serialize_xml()
        variant_e.extend(object_entry_content_elements)
        return variant_e
