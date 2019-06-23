#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Work(PrincipalElement):
    """
    workPE |=
        element xobis:work {
            attribute type { string "intellectual" | string "artistic" }?,
            attribute role { string "instance" | string "authority instance" | string "authority" },
            workContent
        }
    """
    TYPES = ["intellectual", "artistic", None]
    ROLES = ["instance", "authority instance", "authority"]
    def __init__(self, work_content, role, type_=None):
        # attributes
        assert type_ in Work.TYPES, f"Work type ({type_}) must be in: {Work.TYPES}"
        self.type = type_
        assert role in Work.ROLES, f"Work role ({role}) must be in: {Work.ROLES}"
        self.role = role
        # content
        assert isinstance(work_content, WorkContent)
        self.work_content = work_content
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        work_attrs = {}
        if self.type:
            work_attrs['type'] = self.type
        if self.role:
            work_attrs['role'] = self.role
        # content
        work_e = E('work', **work_attrs)
        work_content_elements = self.work_content.serialize_xml()
        work_e.extend(work_content_elements)
        return work_e


class WorkContent(Component):
    """
    workContent |=
        element xobis:entry {
            attribute class {
                string "individual" | string "serial" | string "collective" | string "referential"
            }?,
            entryGroupAttributes?,
            workEntryContent
        },
        element xobis:variants { anyVariant+ }?,
        noteList?
    """
    CLASSES = ["individual", "serial", "collective", "referential", None]
    def __init__(self, work_entry_content, \
                       class_=None, \
                       entry_group_attributes=None, \
                       variants=[], note_list=None):
        # attributes
        assert class_ in WorkContent.CLASSES, \
            f"Work entry class ({class_}) must be in: {WorkContent.CLASSES}"
        self.class_ = class_
        # for entry element
        if entry_group_attributes is not None:
            assert isinstance(entry_group_attributes, EntryGroupAttributes)
        self.entry_group_attributes = entry_group_attributes
        assert isinstance(work_entry_content, WorkEntryContent)
        self.work_entry_content = work_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns a list of one or more Elements.
        entry_attrs = {}
        if self.class_ is not None:
            entry_attrs['class'] = self.class_
        if self.entry_group_attributes is not None:
            entry_group_attributes_attrs = self.entry_group_attributes.serialize_xml()
            entry_attrs.update(entry_group_attributes_attrs)
        entry_e = E('entry', **entry_attrs)
        # elements
        elements = []
        # entry element
        work_entry_content_elements = self.work_entry_content.serialize_xml()
        entry_e.extend(work_entry_content_elements)
        elements.append(entry_e)
        # variant elements
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            elements.append(variants_e)
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            elements.append(note_list_e)
        return elements


class WorkEntryContent(Component):
    """
    workEntryContent |=
      ( element xobis:name {
            attribute type { string "generic" },
            nameContent
        },
        qualifiers?
      | ( element xobis:part {
                attribute type { string "subtitle" | string "section" | string "generic" }?,
                nameContent
          },
          qualifiers?
        )+
      )
    """
    def __init__(self, content):
        # content should be either a WorkEntryContentSingleGeneric,
        # or a list of WorkEntryContentPart objects
        self.is_parts = not isinstance(content, WorkEntryContentSingleGeneric)
        if self.is_parts:
            assert content, "Work entry content must have at least one part"
            assert all(isinstance(content_part, WorkEntryContentPart) for content_part in content)
        self.content = content
    def serialize_xml(self):
        # Returns list of one or more Elements.
        if self.is_parts:
            elements = [element for content_parts in self.content for element in content_parts.serialize_xml()]
        else:
            elements = self.content.serialize_xml()
        return elements


class WorkEntryContentSingleGeneric(Component):
    """
    element xobis:name {
          attribute type { string "generic" },
          nameContent
    },
    qualifiers?
    """
    def __init__(self, name_content, qualifiers=None):
        assert isinstance(name_content, NameContent)
        self.name_content = name_content
        if qualifiers is not None:
            assert isinstance(qualifiers, Qualifiers)
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns list of one or two Elements.
        name_content_text, name_content_attrs = self.name_content.serialize_xml()
        name_content_attrs['type'] = 'generic'
        name_e = E('name', **name_content_attrs)
        name_e.text = name_content_text
        elements = [name_e]
        if self.qualifiers is not None:
            qualifiers_e = self.qualifiers.serialize_xml()
            elements.append(qualifiers_e)
        return elements


class WorkEntryContentPart(Component):
    """
    element xobis:part {
          attribute type { string "subtitle" | string "section" | string "generic" }?,
          nameContent
    },
    qualifiers?
    """
    PART_TYPES = ["subtitle", "section", "generic", None]
    def __init__(self, name_content, qualifiers=None):
        # name_content should be a list of tuples of form (type string, NameContent)
        assert name_content, "Work needs at least one name"
        assert all(len(t) == 2 for t in name_content), "Invalid format for name content parts"
        assert all(t[0] in WorkEntryContentPart.PART_TYPES for t in name_content)
        assert all(isinstance(t[1], NameContent) for t in name_content)
        self.name_content = name_content
        if qualifiers is not None:
            assert isinstance(qualifiers, Qualifiers)
        self.qualifiers = qualifiers
    def serialize_xml(self):
        # Returns list of one or more Elements.
        elements = []
        for part_type, part_content in self.name_content:
            name_content_text, name_content_attrs = part_content.serialize_xml()
            name_content_attrs['type'] = part_type
            part_e = E('part', **name_content_attrs)
            part_e.text = name_content_text
            elements.append(part_e)
        if self.qualifiers is not None:
            qualifiers_e = self.qualifiers.serialize_xml()
            elements.append(qualifiers_e)
        return elements


class WorkVariantEntry(VariantEntry):
    """
    workVariant |=
        element xobis:work {
            variantAttributes?,
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { substituteAttribute?, schemeAttribute?, entryGroupAttributes?, workEntryContent },
            noteList?
        }
    """
    def __init__(self, work_entry_content, \
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
        assert isinstance(work_entry_content, WorkEntryContent)
        self.work_entry_content = work_entry_content
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        variant_attributes_attrs = {}
        if self.variant_attributes is not None:
            variant_attributes_attrs = self.variant_attributes.serialize_xml()
        variant_e = E('work', **variant_attributes_attrs)
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
        work_entry_content_elements = self.work_entry_content.serialize_xml()
        entry_e.extend(work_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            variant_e.append(note_list_e)
        return variant_e


class WorkRef(RefElement):
    """
    workRef |= element xobis:work { linkAttributes?, substituteAttribute?, workEntryContent }
    """
    def __init__(self, work_entry_content, link_attributes=None, substitute_attribute=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        if substitute_attribute is not None:
            assert isinstance(substitute_attribute, SubstituteAttribute)
        self.substitute_attribute = substitute_attribute
        assert isinstance(work_entry_content, WorkEntryContent)
        self.work_entry_content = work_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.substitute_attribute is not None:
            substitute_attribute_attrs = self.substitute_attribute.serialize_xml()
            attrs.update(substitute_attribute_attrs)
        work_ref_e = E('work', **attrs)
        work_entry_content_elements = self.work_entry_content.serialize_xml()
        work_ref_e.extend(work_entry_content_elements)
        return work_ref_e
