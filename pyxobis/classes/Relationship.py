#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import Component, GenericContent, RefElement, OptNoteList
from .Time import TimeRef, DurationRef
from .Concept import ConceptRef
from .String import StringRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Relationship(Component):
    """
    element xobis:relationship {
        relationshipContent
    }
    """
    def __init__(self, relationship_content, link_attributes=None):
        assert isinstance(relationship_content, RelationshipContent)
        self.relationship_content = relationship_content
    def serialize_xml(self):
        # Returns an Element.
        content_elements, content_attrs = self.relationship_content.serialize_xml()
        relationship_e = E('relationship', **content_attrs)
        relationship_e.extend(content_elements)
        return relationship_e


class RelationshipContent(Component):
    """
    relationshipContent |=
        attribute xobis:type {
            string "subordinate"
            | string "superordinate"
            | string "preordinate"
            | string "postordinate"
            | string "associative"
            | string "dissociative"
        }?,
        (
          (
            attribute xobis:degree {
              string "primary" | string "secondary" | string "tertiary" | string "broad"
            }?,
            relationshipName,
            stringRef?,  # enumeration
            (timeRef | durationRef)?,
            element xobis:target { conceptRef },
          )
         |
          (
            attribute xobis:degree { string "primary" | string "secondary" }?,
            relationshipName,
            stringRef?,  # enumeration
            (timeRef | durationRef)?,
            element xobis:target {
              (beingRef | stringRef | languageRef | orgRef | placeRef | eventRef | objectRef | workRef | timeRef | durationRef)
            },
          )
        )
    """
    TYPES = ["subordinate", "superordinate", "preordinate", "postordinate", "associative", "dissociative", None]
    # DEGREES_CONCEPT = ["primary", "secondary", "tertiary", "broad", None]
    # DEGREES_NONCONCEPT = ["primary", "secondary", None]
    DEGREES = ["primary", "secondary", "tertiary", "broad", None]
    def __init__(self, relationship_name, element_ref, type=None, degree=None, enumeration=None, time_or_duration_ref=None):
        assert type in RelationshipContent.TYPES
        self.type = type
        assert isinstance(element_ref, RefElement)
        # self.target_is_concept = isinstance(element_ref, ConceptRef)
        # if self.target_is_concept:
        #     assert degree in RelationshipContent.DEGREES_CONCEPT, "invalid degree: {}".format(degree)
        # else:
        #     assert degree in RelationshipContent.DEGREES_NONCONCEPT, "invalid degree: {}".format(degree)
        assert degree in RelationshipContent.DEGREES, "invalid degree: {}".format(degree)
        self.degree = degree
        assert isinstance(relationship_name, RelationshipName)
        self.relationship_name = relationship_name
        if enumeration is not None:
            assert isinstance(enumeration, StringRef)
        self.enumeration = enumeration
        if time_or_duration_ref is not None:
            assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
        self.element_ref = element_ref
    def serialize_xml(self):
        # Returns a list of two to five Elements and a dict of parent attributes.
        elements, attrs = [], {}
        if self.type:
            attrs['type'] = self.type
        if self.degree:
            attrs['degree'] = self.degree
        relationship_name_es = self.relationship_name.serialize_xml()
        elements.extend(relationship_name_es)
        if self.enumeration is not None:
            enumeration_e = self.enumeration.serialize_xml()
            elements.append(enumeration_e)
        if self.time_or_duration_ref is not None:
            time_or_duration_ref_e = self.time_or_duration_ref.serialize_xml()
            elements.append(time_or_duration_ref_e)
        target_e = E('target')
        element_ref_e = self.element_ref.serialize_xml()
        target_e.append(element_ref_e)
        elements.append(target_e)
        return elements, attrs


class RelationshipName(Component):
    """
    relationshipName |=
        element xobis:name { linkAttributes?, genericContent },
        optNoteList
    """
    def __init__(self, name_content, link_attributes=None, opt_note_list=OptNoteList()):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(name_content, GenericContent)
        self.name_content = name_content
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns a list of one or two Elements.
        elements = []
        # name
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = elf.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        name_content_text, name_content_attrs = self.name_content.serialize_xml()
        attrs.update(name_content_attrs)
        name_e = E('name', **attrs)
        name_e.text = name_content_text
        elements.append(name_e)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            elements.append(opt_note_list_e)
        return elements
