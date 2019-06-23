#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Being(PrincipalElement):
    """
    beingPE |=
        element xobis:being {
            roleAttributes,
            attribute type { string "human" | string "nonhuman" | string "special" }?,
            attribute class {
                string "individual"
                | string "familial"
                | string "collective"
                | string "undifferentiated"
                | string "referential"
            }?,
            element xobis:entry {
                schemeAttribute?,
                entryGroupAttributes?,
                genericType?,
                (timeRef | durationRef)?,
                beingEntryContent
            },
            element xobis:variants { anyVariant+ }?,
            noteList?
        }
    """
    TYPES = ["human", "nonhuman", "special", None]
    CLASSES = ["individual", "familial", "collective", "undifferentiated", "referential", None]
    def __init__(self, role_attributes, being_entry_content, \
                       type_=None, class_=None, scheme_attribute=None, \
                       entry_group_attributes=None, entry_type=None,
                       time_or_duration_ref=None, variants=[], note_list=None):
        # attributes
        assert isinstance(role_attributes, RoleAttributes)
        self.role_attributes = role_attributes
        assert type_ in Being.TYPES, f"Being type ({type_}) must be in: {Being.TYPES}"
        self.type = type_
        assert class_ in Being.CLASSES, f"Being class ({type_}) must be in: {Being.CLASSES}"
        self.class_ = class_
        # for entry element
        if scheme_attribute is not None:
            assert isinstance(scheme_attribute, SchemeAttribute)
        self.scheme_attribute = scheme_attribute
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        if entry_type is not None:
            assert isinstance(entry_type, GenericType)
        self.entry_type = entry_type
        if time_or_duration_ref is not None:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        assert isinstance(being_entry_content, BeingEntryContent)
        self.being_entry_content = being_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants), \
            f"Invalid type(s) for variant: {', '.join(repr(variant) for variant in variants if not isinstance(variant, VariantEntry))}"
        self.variants = variants
        # for note list
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        being_attrs = {}
        role_attributes_attrs = self.role_attributes.serialize_xml()
        being_attrs.update(role_attributes_attrs)
        if self.type:
            being_attrs['type'] = self.type
        if self.class_:
            being_attrs['class'] = self.class_
        being_e = E('being', **being_attrs)
        # entry element
        entry_attrs = {}
        if self.scheme_attribute is not None:
            scheme_attribute_attrs = self.scheme_attribute.serialize_xml()
            entry_attrs.update(scheme_attribute_attrs)
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        if self.entry_type is not None:
            type_e = self.entry_type.serialize_xml()
            entry_e.append(type_e)
        if self.time_or_duration_ref is not None:
            time_or_duration_ref_e = self.time_or_duration_ref.serialize_xml()
            entry_e.append(time_or_duration_ref_e)
        being_entry_content_elements = self.being_entry_content.serialize_xml()
        entry_e.extend(being_entry_content_elements)
        being_e.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            being_e.append(variants_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            being_e.append(note_list_e)
        return being_e


class BeingEntryContent(Component):
    """
    beingEntryContent |=
        element xobis:name {
            nameContent
            | element xobis:part {
                beingNamePartTypes1,
                nameContent
              }+
            | element xobis:part {
                beingNamePartTypes2,
                nameContent
              }+
        },
        qualifiers?
    beingNamePartTypes1 |=
        attribute type {
          string "given"
          | string "surname"
          | string "patronym"
          | string "matronym"
          | string "teknonym"
          | string "expansion"
        }
    beingNamePartTypes2 |=
        attribute type {
          string "given"
          | string "paternal surname"
          | string "maternal surname"
          | string "patronym"
          | string "matronym"
          | string "teknonym"
          | string "expansion"
        }
    """
    PART_TYPES_1 = ["given", "surname", "patronym", "matronym", "teknonym", "expansion"]
    PART_TYPES_2 = ["given", "paternal surname", "maternal surname", "patronym", "matronym", "teknonym", "expansion"]
    def __init__(self, name_content, qualifiers=None):
        # name_content should be either NameContent,
        # or a list of tuples of form (type string, NameContent)
        self.is_parts = not isinstance(name_content, NameContent)
        if self.is_parts:
            assert name_content
            assert all(len(t) == 2 for t in name_content)
            assert all(t[0] in self.PART_TYPES_1 for t in name_content) or all(t[0] in self.PART_TYPES_2 for t in name_content), \
                f"Invalid part type set: {', '.join(t[0] for t in name_content)}"
            assert all(isinstance(t[1], NameContent) for t in name_content)
        self.name_content = name_content
        if qualifiers is not None:
            assert isinstance(qualifiers, Qualifiers)
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns list of one or two Elements.
        if self.is_parts:
            name_e = E('name')
            for part_type, part_content in self.name_content:
                name_content_text, name_content_attrs = part_content.serialize_xml()
                name_content_attrs['type'] = part_type
                part_e = E('part', **name_content_attrs)
                part_e.text = name_content_text
                name_e.append(part_e)
        else:
            name_content_text, name_content_attrs = self.name_content.serialize_xml()
            name_e = E('name', **name_content_attrs)
            name_e.text = name_content_text
        elements = [name_e]
        if self.qualifiers is not None:
            qualifiers_e = self.qualifiers.serialize_xml()
            elements.append(qualifiers_e)
        return elements


class BeingVariantEntry(VariantEntry):
    """
    beingVariant |=
        element xobis:being {
            variantAttributes?,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { substituteAttribute?, schemeAttribute?, entryGroupAttributes?, beingEntryContent },
            noteList?
        }
    """
    def __init__(self, being_entry_content, \
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
        assert isinstance(being_entry_content, BeingEntryContent)
        self.being_entry_content = being_entry_content
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        variant_attributes_attrs = {}
        if self.variant_attributes is not None:
            variant_attributes_attrs = self.variant_attributes.serialize_xml()
        variant_e = E('being', **variant_attributes_attrs)
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
        being_entry_content_elements = self.being_entry_content.serialize_xml()
        entry_e.extend(being_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            variant_e.append(note_list_e)
        return variant_e


class BeingRef(RefElement):
    """
    beingRef |= element xobis:being { linkAttributes?, substituteAttribute?, beingEntryContent }
    """
    def __init__(self, being_entry_content, \
                       link_attributes=None, substitute_attribute=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(being_entry_content, BeingEntryContent)
        self.being_entry_content = being_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            attrs.update(substitute_attribute_attrs)
        being_ref_e = E('being', **attrs)
        being_entry_content_elements = self.being_entry_content.serialize_xml()
        being_ref_e.extend(being_entry_content_elements)
        return being_ref_e
