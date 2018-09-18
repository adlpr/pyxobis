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

            rb.set_name(rel_name)

            # Type
            rel_types = self.ix.lookup_rel_types(rel_name)
            if len(rel_types) == 1:
                rb.set_type(rel_types.pop().lower())
            # what to do with multiple types?

            # Degree: n/a

            # Enumeration
            if '1' in field:
                enum = str(int(''.join(d for d in field['1'] if d.isdigit())))
            else:
                enum = '1'
            rb.set_enumeration(self.build_simple_ref(enum, STRING))

            # Chronology: n/a

            # Target
            rb.set_target(build_ref_from_field(field, BEING))
            # brb = BeingRefBuilder()
            # ref_names_and_qualifiers = self.np.parse_being_name(field)
            # for ref_name_or_qualifier in ref_names_and_qualifiers:
            #     if isinstance(ref_name_or_qualifier, dict):
            #         brb.add_name(**ref_name_or_qualifier)
            #     else:
            #         brb.add_qualifier(ref_name_or_qualifier)
            # brb.set_link(*self.get_linking_info(field, BEING))
            # rb.set_target(brb.build())

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

            rb.set_name(rel_name)

            # Type
            rel_types = self.ix.lookup_rel_types(rel_name)
            if len(rel_types) == 1:
                rb.set_type(rel_types.pop().lower())

            # Degree: n/a

            # Enumeration
            if '1' in field:
                enum = str(int(''.join(d for d in field['1'] if d.isdigit())))
            else:
                enum = '1'
            rb.set_enumeration(self.build_simple_ref(enum, STRING))

            # Chronology: n/a

            # Target
            rb.set_target(build_ref_from_field(field, ORGANIZATION))
            # orb = OrganizationRefBuilder()
            # ref_names_and_qualifiers = self.np.parse_organization_name(field)
            # for ref_name_or_qualifier in ref_names_and_qualifiers:
            #     if isinstance(ref_name_or_qualifier, dict):
            #         orb.add_name(**ref_name_or_qualifier)
            #     else:
            #         orb.add_qualifier(ref_name_or_qualifier)
            # orb.set_link(*self.get_linking_info(field, ORGANIZATION))
            # rb.set_target(orb.build())

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

            rb.set_name(rel_name)

            # Type
            rel_types = self.ix.lookup_rel_types(rel_name)
            if len(rel_types) == 1:
                rb.set_type(rel_types.pop().lower())

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
            rb.set_target(build_ref_from_field(field, EVENT))
            # erb = EventRefBuilder()
            # ref_names_and_qualifiers = self.np.parse_event_name(field)
            # for ref_name_or_qualifier in ref_names_and_qualifiers:
            #     if isinstance(ref_name_or_qualifier, dict):
            #         erb.add_name(**ref_name_or_qualifier)
            #     else:
            #         erb.add_qualifier(ref_name_or_qualifier)
            # erb.set_link(*self.get_linking_info(field, EVENT))
            # rb.set_target(erb.build())

            # Notes: n/a

            relationships.append(rb.build())

    # Uniform Title, Main Entry
    for field in record.get_fields('130'):
        rb = RelationshipBuilder()

        # @@@@@@@@@@@@@@@
        ...
        ...
        rel_name = "Related"
        ...
        ...

        rb.set_name(rel_name)

        # Type
        rel_types = self.ix.lookup_rel_types(rel_name)
        if len(rel_types) == 1:
            rb.set_type(rel_types.pop().lower())

        # Degree: n/a

        # Enumeration: n/a

        # Chronology: n/a

        # Target
        rb.set_target(build_ref_from_field(field, WORK_AUT))
        # wrb = WorkRefBuilder()
        # ref_names_and_qualifiers = self.np.parse_work_authority_name(field)
        # for ref_name_or_qualifier in ref_names_and_qualifiers:
        #     if isinstance(ref_name_or_qualifier, dict):
        #         wrb.add_name(**ref_name_or_qualifier)
        #     else:
        #         wrb.add_qualifier(ref_name_or_qualifier)
        # wrb.set_link(*self.get_linking_info(field, WORK_AUT))
        # rb.set_target(wrb.build())

        # Notes: n/a

        relationships.append(rb.build())

    ...
    ...
    ...

    # Personal Name as Subject (R)
    for field in record.get_fields('600'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e')
        if not rel_names:
            # Default relator
            rel_names = ["Subject:"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            rb.set_name(rel_name)

            # Type
            rel_types = self.ix.lookup_rel_types(rel_name)
            if len(rel_types) == 1:
                rb.set_type(rel_types.pop().lower())

            # Degree: n/a

            # Enumeration: n/a

            # Chronology: n/a

            # Target
            rb.set_target(build_ref_from_field(field, BEING))
            # brb = BeingRefBuilder()
            # ref_names_and_qualifiers = self.np.parse_being_name(field)
            # for ref_name_or_qualifier in ref_names_and_qualifiers:
            #     if isinstance(ref_name_or_qualifier, dict):
            #         brb.add_name(**ref_name_or_qualifier)
            #     else:
            #         brb.add_qualifier(ref_name_or_qualifier)
            # brb.set_link(*self.get_linking_info(field, BEING))
            # rb.set_target(brb.build())

            # Notes:
            for val in field.get_subfields('j'):
                rb.add_note(val,
                            content_lang = None,
                            type = "annotation")

            relationships.append(rb.build())

    return relationships
