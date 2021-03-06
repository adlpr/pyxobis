#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import Component, GenericContent, RefElement, NoteList
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
            element xobis:name { linkAttributes?, genericContent },
            stringRef?,  # enumeration
            (timeRef | durationRef)?,
            element xobis:target { conceptRef }
          )
         |
          (
            attribute xobis:degree { string "primary" | string "secondary" }?,
            element xobis:name { linkAttributes?, genericContent },
            stringRef?,  # enumeration
            (timeRef | durationRef)?,
            element xobis:target {
              (beingRef | stringRef | languageRef | orgRef | placeRef | eventRef | objectRef | workRef | timeRef | durationRef)
            }
          )
        ),
        noteList?
    """
    TYPES = ["subordinate", "superordinate", "preordinate", "postordinate", "associative", "dissociative", None]
    # DEGREES_CONCEPT = ["primary", "secondary", "tertiary", "broad", None]
    # DEGREES_NONCONCEPT = ["primary", "secondary", None]
    DEGREES = ["primary", "secondary", "tertiary", "broad", None]
    def __init__(self, relationship_name, element_ref, type=None, degree=None, enumeration=None, time_or_duration_ref=None, note_list=None):
        assert type in RelationshipContent.TYPES
        self.type = type
        assert isinstance(element_ref, RefElement), f"invalid target type: {type(element_ref)}"
        # self.target_is_concept = isinstance(element_ref, ConceptRef)
        # if self.target_is_concept:
        #     assert degree in RelationshipContent.DEGREES_CONCEPT, f"invalid degree: {degree}"
        # else:
        #     assert degree in RelationshipContent.DEGREES_NONCONCEPT, f"invalid degree: {degree}"
        assert degree in RelationshipContent.DEGREES, f"invalid degree: {degree}"
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
        if note_list is not None:
            assert isinstance(note_list, NoteList)
        self.note_list = note_list
    def serialize_xml(self):
        # Returns a list of two to five Elements and a dict of parent attributes.
        elements, attrs = [], {}
        if self.type:
            attrs['type'] = self.type
        if self.degree:
            attrs['degree'] = self.degree
        relationship_name_e = self.relationship_name.serialize_xml()
        elements.append(relationship_name_e)
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
        # note list
        if self.note_list is not None:
            note_list_e = self.note_list.serialize_xml()
            elements.append(note_list_e)
        return elements, attrs


class RelationshipName(Component):
    """
    element xobis:name { linkAttributes?, genericContent }
    """
    def __init__(self, name_content, link_attributes=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(name_content, GenericContent)
        self.name_content = name_content
    def serialize_xml(self):
        # Returns an Element.
        # name
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = elf.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        name_content_text, name_content_attrs = self.name_content.serialize_xml()
        attrs.update(name_content_attrs)
        name_e = E('name', **attrs)
        name_e.text = name_content_text
        return name_e
