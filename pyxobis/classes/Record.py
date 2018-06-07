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
    <record>
      <controlData>
        <id>
          {organization ref}
          <value>   str
        </id>
        <types>
          <type> (Type) *
        <actions>
          <action> *
            <type> (Type)
            {time/dur ref}
      {PrincipalElement}
      <relationships>
        <relationship> (Relationship) *
    """

    def __init__(self, control_data, principal_element, relationships=[]):
        assert isinstance(control_data, ControlData)
        self.control_data = control_data
        assert isinstance(principal_element, PrincipalElement), "Record must contain valid PrincipalElement"
        self.principal_element = principal_element
        assert all(isinstance(relationship, Relationship) for relationship in relationships)
        self.relationships = relationships
    def serialize_xml(self):
        # Returns an Element.
        record_e = E('record')
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
    Information, such as date
    created and maintained, record type, and its status history, is included
    within ControlData's three container elements: ID, Types, and Actions.
    """
    def __init__(self, id_org_ref, id_value, types=[], actions=[]):
        assert isinstance(id_org_ref, OrganizationRef)
        self.id_org_ref = id_org_ref
        assert isinstance(id_value, str), "id_value is {}, must be str".format(type(id_value))
        self.id_value = id_value
        assert all(isinstance(type, Type) for type in types)
        self.types = types
        assert all(isinstance(action, ControlDataAction) for action in actions)
        self.actions = actions
    def serialize_xml(self):
        # Returns an Element.
        control_data_e = E('controlData')
        # <id>
        id_e = E('id')
        id_org_ref_e = self.id_org_ref.serialize_xml()
        id_e.append(id_org_ref_e)
        value_e = E('value')
        value_e.text = self.id_value
        id_e.append(value_e)
        control_data_e.append(id_e)
        # <types>
        types_e = E('types')
        type_elements = list(filter(None, [type.serialize_xml() for type in self.types]))
        types_e.extend(type_elements)
        control_data_e.append(types_e)
        # <actions>
        actions_e = E('actions')
        action_elements = [action.serialize_xml() for action in self.actions]
        actions_e.extend(action_elements)
        control_data_e.append(actions_e)
        return control_data_e


class ControlDataAction(Component):
    def __init__(self, type, time_or_duration_ref):
        assert isinstance(type, Type)
        self.type = type
        assert isinstance(time_or_duration_ref, TimeRef) or isinstance(time_or_duration_ref, DurationRef)
        self.time_or_duration_ref = time_or_duration_ref
    def serialize_xml(self):
        # Returns an Element.
        control_data_e = E('controlData')
        # <id>
        id_e = E('id')
        id_org_ref_e = self.id_org_ref.serialize_xml()
        id_e.append(id_org_ref_e)
        value_e = E('value')
        value_e.text = self.id_value
        id_e.append(value_e)
        control_data_e.append(id_e)
        # <types>
        types_e = E('types')
        type_elements = list(filter(None, [type.serialize_xml() for type in self.types]))
        types_e.extend(type_elements)
        control_data_e.append(types_e)
        # <actions>
        actions_e = E('actions')
        action_elements = [action.serialize_xml() for action in self.actions]
        actions_e.extend(action_elements)
        control_data_e.append(actions_e)
        return control_data_e
