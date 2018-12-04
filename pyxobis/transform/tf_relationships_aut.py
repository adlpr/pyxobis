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

    relationships = []

    # See Also From Reference, Personal Name (R)
    for field in record.get_fields('500'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Related"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a

            # Chronology
            rb.set_time_or_duration_ref(self.get_field_chronology(field))

            # Target
            rb.set_target(self.build_ref_from_field(field, BEING))

            # Notes:
            for val in field.get_subfields('j'):
                rb.add_note(val,
                            content_lang = None,
                            role = "annotation")

            relationships.append(rb.build())

    # See Also From Reference, Organization Name (R)
    for field in record.get_fields('510'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Related"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a

            # Chronology
            rb.set_time_or_duration_ref(self.get_field_chronology(field))

            # Target
            rb.set_target(self.build_ref_from_field(field, ORGANIZATION))

            # Notes:
            for val in field.get_subfields('j'):
                rb.add_note(val,
                            content_lang = None,
                            role = "annotation")

            relationships.append(rb.build())

    # See Also From Reference, Event Name (R)
    for field in record.get_fields('511'):
        # Relationship Name(s)
        rel_names = field.get_subfields('i') or ["Related"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a

            # Chronology
            rb.set_time_or_duration_ref(self.get_field_chronology(field))

            # Target
            rb.set_target(self.build_ref_from_field(field, EVENT))

            # Notes:
            for val in field.get_subfields('j'):
                rb.add_note(val,
                            content_lang = None,
                            role = "annotation")

            relationships.append(rb.build())

    # See Also From Reference, Uniform Title (R) (Lane)
    for field in record.get_fields('530'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Related"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, WORK_AUT))

            # Notes:
            for val in field.get_subfields('j'):
                rb.add_note(val,
                            content_lang = None,
                            role = "annotation")

            relationships.append(rb.build())

    # See Also From Reference, Topical/Language/Time Term (R)
    # for field in record.get_fields('550'):
    #     # Relationship Name(s)
    #     rel_names = field.get_subfields('e') or ["Topic"] if field.indicator2 in '23' else ["Subject"]
    #     for rel_name in rel_names:
    #         rb = RelationshipBuilder()
    #
    #         # Name/Type
    #         rel_name = rel_name.rstrip(': ')
    #         rb.set_name(rel_name)
    #         rb.set_type(self.get_relation_type(rel_name))
    #
    #         # Degree
    #         rb.set_degree({'1': 'primary',
    #                        '2': 'secondary',
    #                        '3': 'tertiary',
    #                        '4': 'broad'}.get(field.indicator1))
    #
    #         # Enumeration: n/a
    #         # Chronology: n/a
    #
    #         # Target
    #         # determine element type
    #         target_element_type = {'2': CONCEPT,
    #                                '3': CONCEPT,
    #                                '5': TIME,
    #                                '6': LANGUAGE}.get(field.indicator2)
    #         assert target_element_type, "invalid I2 in field: {}".format(field)
    #
    #         if target_element_type == TIME:
    #             # ^x is the second part of a Duration
    #             datetime_subject, end_datetime_subject = field['a'] if 'a' in field else '', field['x']
    #             if end_datetime_subject:
    #                 datetime_subject = datetime_subject.rstrip('-') + '-' + end_datetime_subject
    #             target_ref = self.dp.parse_as_ref(datetime_subject, element_type=None)
    #         else:
    #             target_ref = self.build_ref_from_field(field, target_element_type)
    #         rb.set_target(target_ref)
    #
    #         # Notes: n/a
    #
    #         relationships.append(rb.build())

    # See Also From Reference, Geographic Name (R)
    # for field in record.get_fields('551'):
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
    #         # Degree
    #         rb.set_degree({'1': 'primary',
    #                        '2': 'secondary'}.get(field.indicator1))
    #
    #         # Enumeration: n/a
    #         # Chronology: n/a
    #
    #         # Target
    #         rb.set_target(self.build_ref_from_field(field, PLACE))
    #
    #         # Notes:
    #         for val in field.get_subfields('j'):
    #             rb.add_note(val,
    #                         content_lang = None,
    #                         role = "annotation")
    #
    #         relationships.append(rb.build())

    ...
    ...
    ...
    ...
    ...
    ...
    ...
    ...
    ...

    return relationships
