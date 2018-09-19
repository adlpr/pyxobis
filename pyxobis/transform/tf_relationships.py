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

    relationships = []

    # Personal Name, Main Entry
    for field in record.get_fields('100'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e')
        if not rel_names:
            # Determine default relator:
            #   if record is a monograph and "edit" not in 245 ^c, use Author:
            #   else, use Related:
            if record.is_monographic() and not ('c' in record['245'] and re.search(r"(^|\s)edit", record['245']['c'], flags=re.I)):
                rel_names = ["Author:"]
            else:
                rel_names = ["Related:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            if '1' in field:
                enum = str(int(''.join(d for d in field['1'] if d.isdigit())))
            else:
                enum = '1'
            rb.set_enumeration(self.build_simple_ref(enum, STRING))

            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, BEING))

            # Notes
            for code, val in field.get_subfields('u','v','z', with_codes=True):
                rb.add_note(val,
                            content_lang = None,
                            type = "transcription")

            relationships.append(rb.build())

    # Organization Name, Main Entry
    for field in record.get_fields('110'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e')
        if not rel_names:
            # Determine default relator
            ...
            ...
            ...
            rel_names = ["Editor:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            if '1' in field:
                enum = str(int(''.join(d for d in field['1'] if d.isdigit())))
            else:
                enum = '1'
            rb.set_enumeration(self.build_simple_ref(enum, STRING))

            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, ORGANIZATION))

            # Notes
            for code, val in field.get_subfields('j','u','v','z', with_codes=True):
                rb.add_note(val,
                            content_lang = None,
                            type = "transcription" if code != 'j' else "annotation")

            relationships.append(rb.build())

    # Event Name, Main Entry / Added Entry
    for field in record.get_fields('111','711'):
        # Relationship Name(s)
        rel_names = field.get_subfields('j')
        if not rel_names:
            # Determine default relator
            ...
            ...
            ...
            rel_names = ["Author:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            if '1' in field:
                enum = str(int(''.join(d for d in field['1'] if d.isdigit())))
                rb.set_enumeration(self.build_simple_ref(enum, STRING))
            elif field.tag == '111':
                enum = '1'
                rb.set_enumeration(self.build_simple_ref(enum, STRING))

            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, EVENT))

            # Notes: n/a

            relationships.append(rb.build())

    # Uniform Title, Main Entry
    for field in record.get_fields('130'):
        rb = RelationshipBuilder()

        # relator?
        ...
        ...
        rel_name = "Related"
        ...
        ...

        # Name/Type
        rb.set_name(rel_name)
        rb.set_type(self.get_relation_type(rel_name))

        # Degree: n/a
        # Enumeration: n/a
        # Chronology: n/a

        # Target
        rb.set_target(self.build_ref_from_field(field, WORK_AUT))

        # Notes: n/a

        relationships.append(rb.build())

    ...
    ...
    ...

    # Personal Name as Subject (R)
    for field in record.get_fields('600'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, BEING))

            # Notes:
            for val in field.get_subfields('j'):
                rb.add_note(val,
                            content_lang = None,
                            type = "annotation")

            relationships.append(rb.build())

    # Organization Name as Subject (R)
    for field in record.get_fields('610'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
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
                            type = "annotation")

            relationships.append(rb.build())

    # Event Name as Subject (R)
    for field in record.get_fields('611'):
        # Relationship Name(s)
        rel_names = field.get_subfields('j') or ["Subject:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, EVENT))

            # Notes: n/a

            relationships.append(rb.build())

    # Title as Subject (R)
    for field in record.get_fields('630'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, WORK_AUT))

            # Notes: n/a

            relationships.append(rb.build())

    # Topical Subject (R)
    for field in record.get_fields('650'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree
            rb.set_degree({'1': 'primary',
                           '2': 'secondary',
                           '3': 'tertiary',
                           '4': 'broad'}.get(field.indicator1))

            # Enumeration: n/a
            # Chronology: n/a

            # Target
            # determine element type
            target_element_type = {'2': CONCEPT,
                                   '3': CONCEPT,
                                   '5': TIME,
                                   '6': LANGUAGE}.get(field.indicator2)
            assert target_element_type, "invalid I2 in field: {}".format(field) 

            if target_element_type == TIME:
                # ^x is the second part of a Duration
                datetime_subject, end_datetime_subject = field['a'] if 'a' in field else '', field['x']
                if end_datetime_subject:
                    datetime_subject = datetime_subject.rstrip('-') + '-' + end_datetime_subject
                rb.set_target(self.dp.parse_as_ref(datetime_subject, element_type=None))
            else:
                rb.set_target(self.build_ref_from_field(field, target_element_type))

            # Notes: n/a

            relationships.append(rb.build())
    ...
    ...
    ...

    return relationships
