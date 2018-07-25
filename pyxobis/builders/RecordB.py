#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *


class RecordBuilder:
    """
    Interface for constructing a XOBIS Record element.
    """
    def __init__(self):
        self.lang = None
        self.id_org_ref = None
        self.id_value = None
        self.id_alternates = []
        self.types = []
        self.actions = []
        self.principal_element = None
        self.relationships = []
    def set_lang(self, lang):
        self.lang = lang
    def set_id_org_ref(self, id_org_ref):
        self.id_org_ref = id_org_ref
    def set_id_value(self, id_value):
        self.id_value = id_value
    def add_id_alternate(self, id_org_ref, id_value):
        self.id_alternates.append( IDContent(id_org_ref, id_value) )
    def add_type(self, xlink_title=None, xlink_href=None, set_ref=None):
        self.types.append(
            GenericType( LinkAttributes(xlink_title, XSDAnyURI(xlink_href)  \
                                                  if xlink_href else None)  \
                      if xlink_title else None,
                  XSDAnyURI(set_ref) if set_ref else None )
        )
    def set_principal_element(self, principal_element):
        # assert isinstance(principal_element, RefElement)
        self.principal_element = principal_element
    def add_action(self, time_or_duration_ref, xlink_title=None, xlink_href=None, set_ref=None):
        self.actions.append(
            ControlDataAction(
                GenericType( LinkAttributes(xlink_title, XSDAnyURI(xlink_href)  \
                                                      if xlink_href else None)  \
                          if xlink_title else None,
                      XSDAnyURI(set_ref) if set_ref else None ),
                time_or_duration_ref
            )
        )
    def add_relationship(self, relationship):
        # assert isinstance(relationship, Relationship)
        self.relationships.append(relationship)
    def build(self):
        return Record(
                   ControlData(
                       IDContent(self.id_org_ref, self.id_value),
                       self.id_alternates,
                       self.types,
                       self.actions
                   ),
                   self.principal_element,
                   self.lang,
                   self.relationships
               )
