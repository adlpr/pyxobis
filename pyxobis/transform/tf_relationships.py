#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pymarc import Field
from pyxobis.builders import *
from .tf_common import *

def transform_relationships_aut(self, record):
    """
    For each field describing a relationship in record, build a Relationship.
    Returns a list of zero or more Relationship objects.
    """
    ...
    ...
    ...
    ...
    ...
    ...
    return []

def transform_relationships_bib(self, record):
    """
    For each field describing a relationship in record, build a Relationship.
    Returns a list of zero or more Relationship objects.
    """
    ...
    ...
    ...

    relationships = []

    # Personal Name, Main Entry
    for field in record.get_fields('100'):
        rb = RelationshipBuilder()

        # Build ref for target
        brb = BeingRefBuilder()
        ref_names, ref_qualifiers = self.np.parse_being_name(field)
        for ref_name in ref_names:
            brb.add_name(**ref_name)
        for ref_qualifier in ref_qualifiers:
            brb.add_qualifier(ref_qualifier)
        brb.set_link(*self.get_linking_info(field, BEING))
        # Set target
        rb.set_target(brb.build())

        relationships.append(rb.build())

    ...
    ...
    ...
    return relationships
