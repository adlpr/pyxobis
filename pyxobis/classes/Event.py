#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/"})


class Event(PrincipalElement):
    """
    eventPE |=
        element xobis:event {
            attribute type {
                string "natural"
                | string "meeting"
                | string "journey"
                | string "occurrence"
                | string "miscellaneous"
            }?,
            optClass,
            element xobis:entry { optScheme, optEntryGroupAttributes, eventEntryContent },
            element xobis:variants { anyVariant+ }?,
            optNoteList
        }
    """
    TYPES = ["natural", "meeting", "journey", "occurrence", "miscellaneous", None]
    def __init__(self, event_entry_content, \
                       type_=None, opt_class=OptClass(), \
                       opt_scheme=OptScheme(), \
                       opt_entry_group_attributes=OptEntryGroupAttributes(), \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert type_ in Event.TYPES
        self.type = type_
        assert isinstance(opt_class, OptClass)
        self.opt_class = opt_class
        # for entry element
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(opt_entry_group_attributes, OptEntryGroupAttributes)
        self.opt_entry_group_attributes = opt_entry_group_attributes
        assert isinstance(event_entry_content, EventEntryContent)
        self.event_entry_content = event_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        event_attrs = {}
        if self.type:
            event_attrs['type'] = self.type
        opt_class_attrs = self.opt_class.serialize_xml()
        event_attrs.update(opt_class_attrs)
        event_e = E('event', **event_attrs)
        # entry element
        entry_attrs = {}
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_attrs.update(opt_scheme_attrs)
        opt_entry_group_attributes_attrs = self.opt_entry_group_attributes.serialize_xml()
        entry_attrs.update(opt_entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        event_entry_content_elements = self.event_entry_content.serialize_xml()
        entry_e.extend(event_entry_content_elements)
        event_e.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            event_e.append(variants_e)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            event_e.append(opt_note_list_e)
        return event_e




class EventEntryContent(Component):
    """
    eventEntryContent |= preQualifiersOpt, genericName, qualifiersOpt
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


class EventVariantEntry(VariantEntry):
    """
    eventVariant |=
        element xobis:event {
            optVariantAttributes,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { optSubstituteAttribute, optScheme, optEntryGroupAttributes, eventEntryContent },
            optNoteList
        }
    """
    def __init__(self, event_entry_content, \
                       opt_variant_attributes=OptVariantAttributes(), \
                       type_=None, time_or_duration_ref=None, \
                       opt_substitute_attribute=OptSubstituteAttribute(), \
                       opt_scheme=OptScheme(), \
                       opt_entry_group_attributes=OptEntryGroupAttributes(), \
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
        assert isinstance(opt_entry_group_attributes, OptEntryGroupAttributes)
        self.opt_entry_group_attributes = opt_entry_group_attributes
        assert isinstance(event_entry_content, EventEntryContent)
        self.event_entry_content = event_entry_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        opt_variant_attributes_attrs = self.opt_variant_attributes.serialize_xml()
        variant_e = E('event', **opt_variant_attributes_attrs)
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
        opt_entry_group_attributes_attrs = self.opt_entry_group_attributes.serialize_xml()
        entry_attrs.update(opt_entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        # --> content
        event_entry_content_elements = self.event_entry_content.serialize_xml()
        entry_e.extend(event_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e



class EventRef(PreQualifierRefElement):
    """
    eventRef |= element xobis:event { linkAttributes?, optSubstituteAttribute, eventEntryContent }
    """
    def __init__(self, event_entry_content, link_attributes=None, opt_substitute_attribute=OptSubstituteAttribute()):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(event_entry_content, EventEntryContent)
        self.event_entry_content = event_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        attrs.update(opt_substitute_attribute_attrs)
        variant_e = E('event', **attrs)
        event_entry_content_elements = self.event_entry_content.serialize_xml()
        variant_e.extend(event_entry_content_elements)
        return variant_e
