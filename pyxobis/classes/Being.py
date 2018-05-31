#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Being(PrincipalElement):
    """
    beingPE |=
        element xobis:being {
            roleAttributes_,
            attribute type { string "human" | string "nonhuman" | string "special" }?,
            attribute class {
                string "individual"
                | string "familial"
                | string "collective"
                | string "undifferentiated"
                | string "referential"
            }?,
            element xobis:entry {
                optScheme_,
                type_?,
                (timeRef | durationRef)?,
                _beingEntryContent
            },
            element xobis:variant {
                type_?,
                (timeRef | durationRef)?,
                element xobis:entry { substituteAttribute, optScheme_, _beingEntryContent },
                optNoteList_
            }*,
            optNoteList_
        }
    """
    TYPES = ["human", "nonhuman", "special", None]
    CLASSES = ["individual", "familial", "collective", "undifferentiated", "referential", None]
    def __init__(self, role_attributes, being_entry_content, \
                       type_=None, class_=None, \
                       opt_scheme=OptScheme(), entry_type=Type(), time_or_duration_ref=None, \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert isinstance(role_attributes, RoleAttributes)
        self.role_attributes = role_attributes
        assert type_ in Being.TYPES, \
            "Being type ({}) must be in: {}".format(type_, str(Being.TYPES))
        self.type = type_
        assert class_ in Being.CLASSES, \
            "Being class ({}) must be in: {}".format(type_, str(Being.CLASSES))
        self.class_ = class_
        # for entry element
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(entry_type, Type)
        self.entry_type = entry_type
        if time_or_duration_ref:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        assert isinstance(being_entry_content, BeingEntryContent)
        self.being_entry_content = being_entry_content
        # for variant elements
        assert all(isinstance(variant, BeingVariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
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
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_e = E('entry', **opt_scheme_attrs)
        type_e = self.entry_type.serialize_xml()
        if type_e is not None:
            entry_e.append(type_e)
        if self.time_or_duration_ref:
            time_or_duration_ref_e = self.time_or_duration_ref.serialize_xml()
            entry_e.append(time_or_duration_ref_e)
        being_entry_content_elements = self.being_entry_content.serialize_xml()
        entry_e.extend(being_entry_content_elements)
        being_e.append(entry_e)
        # variant elements
        variant_elements = [variant.serialize_xml() for variant in self.variants]
        being_e.extend(variant_elements)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            being_e.append(opt_note_list_e)
        return being_e


class BeingEntryContent(Component):
    """
    _beingEntryContent |=
        element xobis:name {
            nameContent_
            | (element xobis:part {
                   attribute type { string "given" | string "surname" | string "expansion" },
                   nameContent_
               }+
               | element xobis:part {
                     attribute type {
                         string "given"
                         | string "paternal surname"
                         | string "maternal surname"
                         | string "expansion"
                     },
                     nameContent_
                 }+)
        },
        qualifiersOpt
    """
    PART_TYPES_1 = ["given", "surname", "expansion"]
    PART_TYPES_2 = ["given", "paternal surname", "maternal surname", "expansion"]
    def __init__(self, name_content, qualifiers_opt=QualifiersOpt()):
        # name_content should be either NameContent,
        # or a list of tuples of form (type string, NameContent)
        self.is_parts = not isinstance(name_content, NameContent)
        if self.is_parts:
            assert name_content
            assert all(len(t) == 2 for t in name_content)
            assert all(t[0] in PART_TYPES_1 for t in name_content) or all(t[0] in PART_TYPES_2 for t in name_content)
            assert all(isinstance(t[1], NameContent) for t in name_content)
        self.name_content = name_content
        assert isinstance(qualifiers_opt, QualifiersOpt)
        self.qualifiers_opt = qualifiers_opt
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
        qualifiers_e = self.qualifiers_opt.serialize_xml()
        if qualifiers_e is not None:
            elements.append(qualifiers_e)
        return elements


class BeingVariantEntry(Component):
    """
    element xobis:variant {
        type_?,
        (timeRef | durationRef)?,
        element xobis:entry { substituteAttribute, optScheme_, _beingEntryContent },
        optNoteList_
    }
    """
    def __init__(self, being_entry_content, \
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
        assert isinstance(being_entry_content, BeingEntryContent)
        self.being_entry_content = being_entry_content
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
        being_entry_content_elements = self.being_entry_content.serialize_xml()
        entry_e.extend(being_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e


class BeingRef(RefElement):
    """
    beingRef |= element xobis:being { linkAttributes_?, _beingEntryContent }
    """
    def __init__(self, being_entry_content, link_attributes=None):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(being_entry_content, BeingEntryContent)
        self.being_entry_content = being_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        variant_e = E('being', **attrs)
        being_entry_content_elements = self.being_entry_content.serialize_xml()
        variant_e.extend(being_entry_content_elements)
        return variant_e
