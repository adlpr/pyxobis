#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *
from .Time import TimeRef, DurationRef
from .Organization import OrganizationRef

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Record(Component):
    """
    element xobis:record {
        attribute lang { text }?,
        controlData,
        (conceptPE
        | beingPE
        | stringPE
        | languagePE
        | orgPE
        | placePE
        | eventPE
        | objectPE
        | workPE),
        element xobis:relationships {
            element xobis:relationship {
                attribute idref { xsd:IDREF }?,
                _relationshipContent
            }+
        }?
    }
    """
    def __init__(self, control_data, principal_element, lang=None, relationships=[]):
        if lang: assert isinstance(lang, str)
        self.lang = lang
        assert isinstance(control_data, ControlData)
        self.control_data = control_data
        assert isinstance(principal_element, PrincipalElement), "Record must contain valid PrincipalElement"
        self.principal_element = principal_element
        assert all(isinstance(relationship, Relationship) for relationship in relationships)
        self.relationships = relationships
    def serialize_xml(self):
        # Returns an Element.
        record_attrs = {}
        if self.lang:
            record_attrs['lang'] = self.lang
        record_e = E('record', **record_attrs)
        # <controlData>
        control_data_e = self.control_data.serialize_xml()
        record_e.append(control_data_e)
        # principal element
        principal_element_e = self.principal_element.serialize_xml()
        record_e.append(principal_element_e)
        # <relationships>
        relationships_e = E('relationships')
        relationship_elements = [relationship.serialize_xml() for relationship in self.relationships]
        relationships_e.extend(relationship_elements)
        record_e.append(relationships_e)
        return record_e


class ControlData(Component):
    """
    controlData |=
        element xobis:controlData {
            element xobis:id {
                idContent,
                element xobis:alternates {
                    element xobis:id { idContent }+
                }?
            },
            element xobis:types { genericType+ }?,
            element xobis:actions {
              element xobis:action {
                  genericType,
                  (timeRef | durationRef)
                  # optional note?
              }+
            }?
        }
    """
    def __init__(self, id_content, id_alternates=[], types=[], actions=[]):
        assert isinstance(id_content, IDContent)
        self.id_content = id_content
        assert all(isinstance(id_alternate, IDContent) for id_alternate in id_alternates)
        self.id_alternates = id_alternates
        assert all(isinstance(type, GenericType) for type in types)
        self.types = types
        assert all(isinstance(action, ControlDataAction) for action in actions)
        self.actions = actions
    def serialize_xml(self):
        # Returns an Element.
        control_data_e = E('controlData')
        # <id>
        id_content_elements, id_content_attrs = self.id_content.serialize_xml()
        id_e = E('id', **id_content_attrs)
        id_e.extend(id_content_elements)
        if self.id_alternates:
            variants_e = E('alternates')
            for id_alternate in self.id_alternates:
                id_alternate_elements, id_alternate_attrs = id_alternate.serialize_xml()
                id_alternate_e = E('id', **id_alternate_attrs)
                id_alternate_e.extend(id_alternate_elements)
                variants_e.append(id_alternate_e)
            id_e.append(variants_e)
        control_data_e.append(id_e)
        # <types>
        if self.types:
            types_e = E('types')
            type_elements = [type for type in  \
                                [type.serialize_xml() for type in self.types]  \
                             if type is not None]
            types_e.extend(type_elements)
            control_data_e.append(types_e)
        # <actions>
        if self.actions:
            actions_e = E('actions')
            action_elements = [action.serialize_xml() for action in self.actions]
            actions_e.extend(action_elements)
            control_data_e.append(actions_e)
        return control_data_e


class ControlDataAction(Component):
    """
    element xobis:action {
        genericType,
        (timeRef | durationRef)
        # optional note?
    }
    """
    def __init__(self, type, time_or_duration_ref):
        assert isinstance(type, GenericType)
        self.type = type
        assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
    def serialize_xml(self):
        # Returns an Element.
        action_e = E('action')
        # <type>
        type_e = self.type.serialize_xml()
        action_e.append(type_e)
        # time/duration ref
        time_or_duration_ref_e = self.time_or_duration_ref.serialize_xml()
        action_e.append(time_or_duration_ref_e)
        return action_e


class IDContent(Component):
    """
    idContent |=
        attribute status {
            (string "valid" | string "invalid" | string "cancelled" | string "incorrect")
            (~ string " linking")?
        }?,
        ( orgRef | element xobis:description { text } ),
        element xobis:value { text }
    """
    STATUSES = ["valid", "invalid", "cancelled", "incorrect",
                "valid linking", "invalid linking",
                "cancelled linking", "incorrect linking", None]
    def __init__(self, org_ref_or_description, id_value, status=None):
        assert status in IDContent.STATUSES
        self.status = status
        self.has_org_ref = isinstance(org_ref_or_description, OrganizationRef)
        assert self.has_org_ref or isinstance(org_ref_or_description, str)
        self.org_ref_or_description = org_ref_or_description
        assert isinstance(id_value, str), "id_value is {}, must be str".format(type(id_value))
        self.id_value = id_value
    def serialize_xml(self):
        # Returns a list of two Elements, and a dict of parent attributes.
        attrs = {}
        if self.status is not None:
            attrs['status'] = self.status
        elements = []
        # Org ref
        if self.has_org_ref:
            org_ref_or_description_e = self.org_ref_or_description.serialize_xml()
        else:
            org_ref_or_description_e = E('description')
            org_ref_or_description_e.text = self.org_ref_or_description
        elements.append(org_ref_or_description_e)
        # <value>
        value_e = E('value')
        value_e.text = self.id_value
        elements.append(value_e)
        return elements, attrs
