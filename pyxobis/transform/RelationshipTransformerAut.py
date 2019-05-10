#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pymarc import Field

from ..builders import RelationshipBuilder, WorkRefBuilder

from . import tf_common_methods as tfcm
from .tf_constants import *

from .Indexer import Indexer
from .DateTimeParser import DateTimeParser


class RelationshipTransformerAut:
    """
    Methods for extracting and building Relationship objects from
    authority pymarc Records.
    """
    def __init__(self, rlt):
        # shared objects and methods from instantiating RelationshipTransformer
        self.get_relation_type = rlt.get_relation_type
        self.build_ref_from_field = rlt.build_ref_from_field
        self.extract_enumeration = rlt.extract_enumeration


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
        for field in record.get_fields('500','600'):
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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, BEING))

                # Notes:
                for val in field.get_subfields('j'):
                    rb.add_note(val,
                                content_lang = None,
                                role = "annotation")

                relationships.append(rb.build())

        # See Also From Reference, Organization Name (R) / Related Subject, Organization Name (Lane) (R)
        for field in record.get_fields('510','610'):
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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, ORGANIZATION))

                # Notes:
                for val in field.get_subfields('j'):
                    rb.add_note(val,
                                content_lang = None,
                                role = "annotation")

                relationships.append(rb.build())

        # See Also From Reference, Event Name (R) / Related Subject, Event Name (Lane) (R)
        for field in record.get_fields('511','611'):
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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, EVENT))

                # Notes
                for val in field.get_subfields('j'):
                    rb.add_note(val,
                                content_lang = None,
                                role = "annotation")

                relationships.append(rb.build())

        # See Also From Reference, Uniform Title (R) (Lane) / Related Subject, Uniform Title (Lane) (R)
        for field in record.get_fields('530','630'):
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
        for field in record.get_fields('550'):
            # if no ^a, field will be treated as a record-level Note instead
            if 'a' in field:
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
                    rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                    # Target
                    target_element_type = Indexer.simple_element_type_from_value(field['a'])

                    if target_element_type == TIME:
                        # ^x is the second part of a Duration
                        datetime_str, end_datetime_str = field['a'], field['x']
                        if end_datetime_str:
                            datetime_str = datetime_str.rstrip('-') + '-' + end_datetime_str
                        target_ref = DateTimeParser.parse_as_ref(datetime_str, None)
                    else:
                        if target_element_type != LANGUAGE:
                            target_element_type = CONCEPT
                        target_ref = self.build_ref_from_field(field, target_element_type)
                    rb.set_target(target_ref)

                    # Notes: n/a

                    relationships.append(rb.build())

        # See Also From Reference, Geographic Name (R)
        for field in record.get_fields('551'):
            # Relationship Name(s)
            rel_names = field.get_subfields('e') or ["Related"]
            for rel_name in rel_names:
                rb = RelationshipBuilder()

                # Name/Type
                rel_name = rel_name.rstrip(': ')
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree: n/a

                # Enumeration
                rb.set_enumeration(self.extract_enumeration(field))

                # Chronology
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, PLACE))

                # Notes
                for val in field.get_subfields('2'):
                    rb.add_note(val,
                                content_lang = None,
                                role = "annotation")

                relationships.append(rb.build())

        # See Also From Reference, Category (Form/Genre) Term (R)
        for field in record.get_fields('555'):
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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, CONCEPT))

                # Notes
                for val in field.get_subfields('2'):
                    rb.add_note(val,
                                content_lang = None,
                                role = "annotation")

                relationships.append(rb.build())

        # See Also From Reference, General Qualifier (R)
        for field in record.get_fields('580'):
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
                rb.set_target(self.build_ref_from_field(field, CONCEPT))

                # Notes: n/a

                relationships.append(rb.build())

        # See Also From Reference, Textword (Lane defined) (R)
        for field in record.get_fields('582'):
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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # convert all accidental ^a to ^y
                field.subfields = ['y' if i%2==0 and v=='a' else v for i,v in enumerate(field.subfields)]

                # Target
                rb.set_target(self.build_ref_from_field(field, STRING))

                # Notes: n/a

                relationships.append(rb.build())

        # Topical/Language/Time Entry (Lane) (R)
        for field in record.get_fields('650'):
            # Relationship Name(s)
            rel_names = field.get_subfields('e') or ["Related"]
            for rel_name in rel_names:
                rb = RelationshipBuilder()

                # Name/Type
                rel_name = rel_name.rstrip(': ')
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree
                rb.set_degree({'1': 'primary',
                               '2': 'secondary',
                               '3': 'tertiary',
                               '4': 'broad'}.get(field.indicator1))

                # Enumeration: n/a

                # Chronology
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                # determine element type
                target_element_type = {'2': CONCEPT,
                                       '3': CONCEPT,
                                       '5': TIME,
                                       '6': LANGUAGE}.get(field.indicator2)
                assert target_element_type, f"invalid I2 in field: {field}"

                if target_element_type == TIME:
                    # ^x is the second part of a Duration
                    datetime_str, end_datetime_str = field['a'] if 'a' in field else '', field['x']
                    if end_datetime_str:
                        datetime_str = datetime_str.rstrip('-') + '-' + end_datetime_str
                    target_ref = DateTimeParser.parse_as_ref(datetime_str, None)
                else:
                    target_ref = self.build_ref_from_field(field, target_element_type)
                rb.set_target(target_ref)

                # Notes
                for val in field.get_subfields('j'):
                    rb.add_note(val,
                                content_lang = None,
                                role = "annotation")

                relationships.append(rb.build())

        # Geographic Entry (Lane) (R)
        for field in record.get_fields('651'):
            # Relationship Name(s)
            rel_names = field.get_subfields('e') or ["Related"]
            for rel_name in rel_names:
                rb = RelationshipBuilder()

                # Name/Type
                rel_name = rel_name.rstrip(': ')
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree
                rb.set_degree({'1': 'primary',
                               '2': 'secondary'}.get(field.indicator1))

                # Enumeration
                rb.set_enumeration(self.extract_enumeration(field))

                # Chronology
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, PLACE))

                # Notes
                for val in field.get_subfields('j'):
                    rb.add_note(val,
                                content_lang = None,
                                role = "annotation")

                relationships.append(rb.build())

        # Category Entry (Lane) (R)
        for field in record.get_fields('655'):
            if field.indicator1 in '124':
                # Relationship Name(s)
                rel_names = field.get_subfields('e') or ["Category"]
                for rel_name in rel_names:
                    rb = RelationshipBuilder()

                    # Name/Type
                    rel_name = rel_name.rstrip(': ')
                    rb.set_name(rel_name)
                    rb.set_type(self.get_relation_type(rel_name))

                    # Degree
                    rb.set_degree({'1': 'primary',
                                   '2': 'secondary',
                                   '4': 'broad'}.get(field.indicator1))

                    # Enumeration: n/a
                    # Chronology
                    rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                    # Target
                    rb.set_target(self.build_ref_from_field(field, CONCEPT))

                    # Notes
                    for val in field.get_subfields('j'):
                        rb.add_note(val,
                                    content_lang = None,
                                    role = "annotation")

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

        # External Relationship Entry (Lane: to PubMed, e.g.) (R)
        for field in record.get_fields('789'):
            rel_names = field.get_subfields('e') or ["Related title:"]
            for rel_name in rel_names:
                rb = RelationshipBuilder()

                # Name/Type
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree: n/a

                # Enumeration: n/a
                # Chronology
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, WORK_INST))

                # Notes: n/a

                relationships.append(rb.build())

        # Electronic Location and Access (Lane: use MFHD) (R)
        for field in record.get_fields('856'):
            # only those marked as "related resource" and not the resource itself
            if field.indicator2 != '2':
                continue

            rb = RelationshipBuilder()

            # Name/Type
            rel_name = "Related"
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Notes
            for code, val in field.get_subfields('9','x', with_codes=True):
                if code == 'x':
                    val = "Date verified: " + val
                rb.add_note(val,
                            role = "annotation" if code == 'x' else "documentation")

            # Target
            wrb = WorkRefBuilder()

            # field should only have one y or z, but do all just in case.
            link_name = ' '.join(field.get_subfields('y','z'))
            wrb.add_name(link_name)
            wrb.set_link(link_name,
                         href_URI = field['u'] )

            for val in field.get_subfields('q'):
                # take a wild guess at the qualifier type
                qualifier_type = Indexer.simple_element_type_from_value(val)
                if qualifier_type is None:
                    qualifier_type = STRING
                wrb.add_qualifier(tfcm.build_simple_ref(val, qualifier_type))

            rb.set_target(wrb.build())

            relationships.append(rb.build())

        # Allowable Subheadings (Lane: MeSH only when 450 $w/3 = a) (R)
        for field in record.get_fields('925'):
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = "Allowable qualifier"
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            # dummy field for proper parsing (pretend it's a X80)
            rb.set_target(self.build_ref_from_field(Field('X80','  ',['x' if val == 'a' else val for val in field.subfields]), CONCEPT))

            # Notes
            # scheme in which the qualifier is allowable
            rb.add_note("LaSH" if field.indicator1 == '9' else "MeSH",
                        content_lang = None,
                        role = "annotation")


            relationships.append(rb.build())


        return relationships
