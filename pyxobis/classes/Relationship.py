#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import Component, GenericContent, RefElement
from .Time import TimeRef, DurationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Relationship(Component):
    def __init__(self, relationship_content):
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
            element xobis:enumeration { xsd:integer }?,
            (timeRef | durationRef)?,
            element xobis:target { conceptRef },
          )
         |
          (
            attribute xobis:degree { string "primary" | string "secondary" }?,
            relationshipName,
            element xobis:enumeration { xsd:integer }?,
            (timeRef | durationRef)?,
            element xobis:target {
              (beingRef | stringRef | languageRef | orgRef | placeRef | eventRef | objectRef | workRef | timeRef | durationRef)
            },
          )
        )
    """
    TYPES = ["subordinate", "superordinate", "preordinate", "postordinate", "associative", "dissociative", None]
    DEGREES_CONCEPT = ["primary", "secondary", "tertiary", "broad", None]
    DEGREES_NONCONCEPT = ["primary", "secondary", None]
    def __init__(self, relationship_name, element_ref, type=None, degree=None, enumeration=None, time_or_duration_ref=None):
        assert type in RelationshipContent.TYPES
        self.type = type
        assert isinstance(element_ref, RefElement)
        self.has_concept_ref = isinstance(element_ref, ConceptRef)
        if self.has_concept_ref:
            assert degree in RelationshipContent.DEGREES_CONCEPT
        else:
            assert degree in RelationshipContent.DEGREES_NONCONCEPT
        self.degree = degree
        assert isinstance(relationship_name, RelationshipName)
        self.relationship_name = relationship_name
        if enumeration is not None:
            assert isinstance(enumeration, int) or str(enumeration).lstrip('-').isdigit()
        self.enumeration = int(enumeration)
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
            enumeration_e = E('enumeration')
            enumeration_e.text = str(self.enumeration)
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
        element xobis:name { genericContent },
        element xobis:modifier {
            attribute nonfiling { xsd:positiveInteger }?,
            genericContent
        }?
    """
    def __init__(self, name_content, modifier_nonfiling=0, modifier_content=None):
        assert isinstance(name_content, GenericContent)
        self.name_content = name_content
        assert isinstance(modifier_nonfiling, int) and modifier_nonfiling >= 0
        self.modifier_nonfiling = modifier_nonfiling
        if modifier_content: assert isinstance(modifier_content, GenericContent)
        self.modifier_content = modifier_content
    def serialize_xml(self):
        # Returns a list of one or two Elements.
        elements = []
        name_content_text, name_content_attrs = self.name_content.serialize_xml()
        name_e = E('name', **name_content_attrs)
        name_e.text = name_content_text
        elements.append(name_e)
        if self.modifier_content:
            modifier_content_elements, modifier_content_attrs = self.modifier_content.serialize_xml()
            modifier_e = E('modifier', **modifier_content_attrs)
            modifier_e.extend(modifier_content_elements)
            elements.append(modifier_e)
        return elements
