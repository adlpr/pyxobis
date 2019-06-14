#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Holdings(Component):
    """
    holdings |=
        element xobis:holdings {
            element xobis:entry { holdingsEntryContent },
            optNoteList
        }
    """
    def __init__(self, holdings_entry_content, opt_note_list=OptNoteList()):
        assert isinstance(holdings_entry_content, HoldingsEntryContent)
        self.holdings_entry_content = holdings_entry_content
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        holdings_e = E('holdings')
        # entry element
        entry_e = E('entry')
        holdings_entry_content_elements = self.holdings_entry_content.serialize_xml()
        entry_e.extend(holdings_entry_content_elements)
        holdings_e.append(entry_e)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            holdings_e.append(opt_note_list_e)
        return holdings_e


class HoldingsEntryContent(Component):
    """
    holdingsEntryContent |=
        (workRef | objectRef),  # link to item claimed held
        conceptRef,             # qualification of thing it is (ebook, print book, art original, etc), i.e. GMD
        qualifiersOpt           # any additional qualifying locations, concepts, etc.
    """
    def __init__(self, work_or_object_ref, concept_ref, \
                       qualifiers_opt=QualifiersOpt()):
        assert isinstance(work_or_object_ref, WorkRef) or isinstance(work_or_object_ref, ObjectRef)
        self.work_or_object_ref = work_or_object_ref
        assert isinstance(concept_ref, ConceptRef)
        self.concept_ref = concept_ref
        assert isinstance(qualifiers_opt, QualifiersOpt)
        self.qualifiers_opt = qualifiers_opt
    def serialize_xml(self):
        # Returns list of two or three Elements.
        elements = []
        work_or_object_e = self.work_or_object_ref.serialize_xml()
        elements.append(work_or_object_e)
        concept_e = self.concept_ref.serialize_xml()
        elements.append(concept_e)
        qualifiers_e = self.qualifiers_opt.serialize_xml()
        if qualifiers_e is not None:
            elements.append(qualifiers_e)
        return elements


class HoldingsRef(RefElement):
    """
    holdingsRef |= element xobis:holdings { linkAttributes?, holdingsEntryContent }
    """
    def __init__(self, holdingsEntryContent, link_attributes=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(holdings_entry_content, HoldingsEntryContent)
        self.holdings_entry_content = holdings_entry_content
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        variant_e = E('language', **attrs)
        language_entry_content_elements = self.holdings_entry_content.serialize_xml()
        variant_e.extend(language_entry_content_elements)
        return variant_e

        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        attrs.update(opt_substitute_attribute_attrs)
        variant_e = E('event', **attrs)
        event_entry_content_elements = self.event_entry_content.serialize_xml()
        variant_e.extend(event_entry_content_elements)
        return variant_e
