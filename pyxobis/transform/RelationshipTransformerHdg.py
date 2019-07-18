#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pymarc import Field

from lmldb.xobis_constants import *

from ..builders import RelationshipBuilder, WorkRefBuilder

from . import tf_common_methods as tfcm

from .Indexer import Indexer
from .DateTimeParser import DateTimeParser


class RelationshipTransformerHdg:
    """
    Methods for extracting and building Relationship objects from
    holdings pymarc Records.
    """
    def __init__(self, rlt):
        # shared objects and methods from instantiating RelationshipTransformer
        self.get_relation_type = rlt.get_relation_type
        self.build_ref_from_field = rlt.build_ref_from_field
        # self.extract_enumeration = rlt.extract_enumeration


    def transform_relationships(self, record):
        """
        For each field describing a relationship
        in authority LaneMARCRecord record,
        build a Relationship.

        Returns a list of zero or more Relationship objects.
        """

        relationships = []

        ...
        ...
        ...
        ...
        ...
        ...
        ...
        ...
        ...

        # See Also From Reference, Personal Name (R) / Related Subject, Personal Name (Lane) (R)
        # for field in record.get_fields('500','600'):
        #     # Relationship Name(s)
        #     rel_names = field.get_subfields('e') or ["Related"]
        #     for rel_name in rel_names:
        #         rb = RelationshipBuilder()
        #
        #         # Name/Type
        #         rel_name = rel_name.rstrip(': ')
        #         rb.set_name(rel_name)
        #         rb.set_type(self.get_relation_type(rel_name))
        #
        #         # Degree: n/a
        #         # Enumeration: n/a
        #
        #         # Chronology
        #         rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))
        #
        #         # Target
        #         rb.set_target(self.build_ref_from_field(field, BEING))
        #
        #         # Notes:
        #         for val in field.get_subfields('j'):
        #             rb.add_note(val,
        #                         content_lang = None,
        #                         role = "annotation")
        #
        #         relationships.append(rb.build())

        # Category Entry (Lane) (R)
        for field in record.get_fields('655'):
            if field.indicator1 in '12':
                rb = RelationshipBuilder()

                # Name/Type
                rel_name = "Category"
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree
                rb.set_degree({'1': 'primary',
                               '2': 'secondary'}.get(field.indicator1))

                # Enumeration: n/a
                # Chronology: n/a

                # Target
                rb.set_target(self.build_ref_from_field(field, CONCEPT))

                # Notes: n/a

                relationships.append(rb.build())

        ...
        ...
        ...
        ...
        ...
        ...
        ...
        ...
        ...


        # Electronic Location and Access (Lane: use MFHD) (R)
        # for field in record.get_fields('856'):
        #     # only those marked as "related resource" and not the resource itself
        #     if field.indicator2 != '2':
        #         continue
        #
        #     rb = RelationshipBuilder()
        #
        #     # Name/Type
        #     rel_name = "Related"
        #     rb.set_name(rel_name)
        #     rb.set_type(self.get_relation_type(rel_name))
        #
        #     # Degree: n/a
        #     # Enumeration: n/a
        #     # Chronology: n/a
        #
        #     # Notes
        #     for code, val in field.get_subfields('9','x', with_codes=True):
        #         if code == 'x':
        #             val = "Date verified: " + val
        #         rb.add_note(val,
        #                     role = "annotation" if code == 'x' else "documentation")
        #
        #     # Target
        #     wrb = WorkRefBuilder()
        #
        #     # field should only have one y or z, but do all just in case.
        #     link_name = ' '.join(field.get_subfields('y','z'))
        #     wrb.add_name(link_name)
        #     wrb.set_link(link_name,
        #                  href_URI = field['u'] )
        #
        #     for val in field.get_subfields('q'):
        #         # take a wild guess at the qualifier type
        #         qualifier_type = Indexer.simple_element_type_from_value(val)
        #         if qualifier_type is None:
        #             qualifier_type = STRING
        #         wrb.add_qualifier(tfcm.build_simple_ref(val, qualifier_type))
        #
        #     rb.set_target(wrb.build())
        #
        #     relationships.append(rb.build())


        return relationships
