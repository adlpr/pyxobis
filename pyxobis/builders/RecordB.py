#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *


class RecordBuilder:
    """
    Interface for constructing a XOBIS Record element.
    """
    def __init__(self):
        self.id_org_ref = None
        self.id_value = None
        self.types = []
        self.actions = []
        self.principal_element = None
        self.relationships = []
    def set_id_org_ref(self, id_org_ref):
        self.id_org_ref = id_org_ref
    def set_id_value(self, id_value):
        self.id_value = id_value
    def add_type(self, xlink_title=None, xlink_href=None, xlink_role=None):
        self.types.append(
            Type( LinkAttributes(xlink_title, xlink_href)  \
                      if link_attributes else None,
                  XSDAnyURI(xlink_role) if xlink_role else None )
        )
    def set_principal_element(self, principal_element):
        # assert isinstance(principal_element, RefElement)
        self.principal_element = principal_element
    def add_action(self, time_or_duration_ref, xlink_title=None, xlink_href=None, xlink_role=None):
        self.actions.append(
            ControlDataAction(
                Type( LinkAttributes(xlink_title, xlink_href)  \
                          if link_attributes else None,
                      XSDAnyURI(xlink_role)  \
                          if xlink_role else None ),
                time_or_duration_ref
            )
        )
    def add_relationship(self, relationship):
        # assert isinstance(relationship, Relationship)
        self.relationships.append(relationship)
    def build(self):
        return Record(
                   ControlData(
                       self.id_org_ref,
                       self.id_value,
                       self.types,
                       self.actions
                   ),
                   self.principal_element,
                   self.relationships
               )
