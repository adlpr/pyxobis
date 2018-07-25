#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Work(PrincipalElement):
    """
    workPE |=
        element xobis:work {
            attribute type { string "intellectual" | string "artistic" }?,
            ((attribute role { string "instance" | string "authority instance" },
              workContent,
              versionsHoldingsOpt)
             | (attribute role { string "authority" },
                workContent))
        }
    """
    TYPES = ["intellectual", "artistic", None]
    ROLES_1 = ["instance", "authority instance"]
    ROLES_2 = ["authority"]
    def __init__(self, work_content, role, type_=None, \
                       versions_holdings_opt=VersionsHoldingsOpt()):
        # attributes
        assert type_ in Work.TYPES, \
            "Work type ({}) must be in: {}".format(type_, str(Work.TYPES))
        self.is_authority = role in Work.ROLES_2
        if not self.is_authority:
            assert role in Work.ROLES_1, \
                "Non-authority Work role ({}) must be in: {}".format(role, str(Work.ROLES_1))
        self.type = type_
        self.role = role
        # content
        assert isinstance(work_content, WorkContent)
        self.work_content = work_content
        assert isinstance(versions_holdings_opt, VersionsHoldingsOpt)
        self.versions_holdings_opt = versions_holdings_opt
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
        if not self.is_authority:
            versions_holdings_opt_e = self.versions_holdings_opt.serialize_xml()
            if versions_holdings_opt_e is not None:
                work_e.append(versions_holdings_opt_e)
        return work_e


class WorkContent(Component):
    """
    workContent |=
        element xobis:entry {
            attribute class {
                string "individual" | string "serial" | string "collective" | string "referential"
            }?,
            workEntryContent
        },
        element xobis:variants { anyVariant+ }?,
        optNoteList
    """
    CLASSES = ["individual", "serial", "collective", "referential", None]
    def __init__(self, work_entry_content, \
                       class_=None, variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert class_ in WorkContent.CLASSES, \
            "Work entry class ({}) must be in: {}".format(class_, str(WorkContent.CLASSES))
        self.class_ = class_
        # for entry element
        assert isinstance(work_entry_content, WorkEntryContent)
        self.work_entry_content = work_entry_content
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns a list of one or more Elements.
        entry_attrs = {}
        if self.class_:
            entry_attrs['class'] = self.class_
        entry_e = E('entry', **entry_attrs)
        elements = []
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
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            elements.append(opt_note_list_e)
        return elements


class WorkEntryContent(Component):
    """
    workEntryContent |=
        element xobis:name {
            (attribute type { string "generic" },
             nameContent)
            | element xobis:part {
                  attribute type { string "subtitle" | string "section" | string "generic" }?,
                  nameContent
              }+
        },
        qualifiersOpt
    """
    PART_TYPES = ["subtitle", "section", "generic", None]
    def __init__(self, name_content, qualifiers_opt=QualifiersOpt()):
        # name_content should be either NameContent,
        # or a list of tuples of form (type string, NameContent)
        self.is_parts = not isinstance(name_content, NameContent)
        if self.is_parts:
            assert name_content, "Work needs at least one name"
            assert all(len(t) == 2 for t in name_content), "Invalid format for name content parts"
            assert all(t[0] in WorkEntryContent.PART_TYPES for t in name_content)
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
            name_content_attrs['type'] = 'generic'
            name_e = E('name', **name_content_attrs)
            name_e.text = name_content_text
        elements = [name_e]
        qualifiers_e = self.qualifiers_opt.serialize_xml()
        if qualifiers_e is not None:
            elements.append(qualifiers_e)
        return elements


class WorkVariantEntry(VariantEntry):
    """
    workVariant |=
        element xobis:work {
            genericType?,
            (timeRef | durationRef)?,
            element xobis:entry { optSubstituteAttribute, optScheme, workEntryContent },
            optNoteList
        }
    """
    def __init__(self, work_entry_content, \
                       type_=None, time_or_duration_ref=None, \
                       opt_substitute_attribute=OptSubstituteAttribute(), \
                       opt_scheme=OptScheme(), \
                       opt_note_list=OptNoteList()):
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
        assert isinstance(work_entry_content, WorkEntryContent)
        self.work_entry_content = work_entry_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        variant_e = E('work')
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
        work_entry_content_elements = self.work_entry_content.serialize_xml()
        entry_e.extend(work_entry_content_elements)
        variant_e.append(entry_e)
        # notelist
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e


class WorkRef(RefElement):
    """
    workRef |= element xobis:work { linkAttributes?, optSubstituteAttribute, workEntryContent }
    """
    def __init__(self, work_entry_content, link_attributes=None, opt_substitute_attribute=OptSubstituteAttribute()):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(work_entry_content, WorkEntryContent)
        self.work_entry_content = work_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        attrs.update(opt_substitute_attribute_attrs)
        variant_e = E('work', **attrs)
        work_entry_content_elements = self.work_entry_content.serialize_xml()
        variant_e.extend(work_entry_content_elements)
        return variant_e
