#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pymarc import Field
from pyxobis.builders import *
from .tf_common import *


def transform_variants(self, record):
    """
    For each field describing a variant in record, build a Variant.
    Returns a list of zero or more VariantEntry objects.

    246 : WORK_INST or OBJECT
    400 : BEING
    410 : ORGANIZATION
    411 : EVENT
    430 : WORK_AUT
    450 : CONCEPT or TIME or LANGUAGE
    451 : PLACE
    455 : CONCEPT or RELATIONSHIP
    [480 : CONCEPT]
    482 : STRING
    """
    record_element_type = record.get_xobis_element_type()

    variants = []

    for field in record.get_fields('150','246','400','410','411','430','450','451','455','480','482'):
        # Doing this as one large query then using a switch conditional
        # is a way to retain original order.

        if field.tag == '150' and 'm' in field:
            # add MeSH "as Topic" version as a variant
            ...
            ...
            ...

        elif field.tag == '246':
            # WORK_INST or OBJECT
            ...
            ...
            ...

        elif field.tag == '400':
            # BEING
            being_variant = self.transform_variant_being(field)
            variants.append(being_variant)

        elif field.tag == '410':
            # ORGANIZATION
            # organization_variant = self.transform_variant_organization(field)
            # variants.append(organization_variant)
            ...
            ...
            ...

        elif field.tag == '411':
            # EVENT
            ...
            ...
            ...

        elif field.tag == '430':
            # WORK_AUT
            ...
            ...
            ...

        elif field.tag == '450':
            # CONCEPT or TIME or LANGUAGE
            # Assume variant is the same type as the heading;
            # if it doesn't match it's almost certainly a CONCEPT
            if record_element_type == TIME:
                # time_variant = self.transform_variant_time(field)
                # variants.append(time_variant)
                ...
                ...
                ...
            elif record_element_type == LANGUAGE:
                # language_variant = self.transform_variant_language(field)
                # variants.append(language_variant)
                ...
                ...
                ...
            else:
                # concept_variant = self.transform_variant_concept(field)
                # variants.append(concept_variant)
                # NOTE THAT ^m IS ANOTHER VARIANT
                ...
                ...
                ...

        elif field.tag == '451':
            # PLACE
            ...
            ...
            ...

        elif field.tag == '455':
            # CONCEPT or RELATIONSHIP
            ...
            ...
            ...

        elif field.tag == '480':
            # CONCEPT
            ...
            ...
            ...

        elif field.tag == '482':
            # STRING
            # string_variant = self.transform_variant_string(field)
            # variants.append(string_variant)
            ...
            ...
            ...

    return variants


def transform_variant_being(self, field):
    """
    Input:  PyMARC 400 field
    Output: BeingVariantEntry object
    """
    bvb = BeingVariantBuilder()

    # Variant Group Attributes
    # ---
    bvb.set_variant_group(id        = field['7'],
                          group     = field['6'],
                          preferred = bool(field['5']))

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        bvb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        bvb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # n/a for now

    # Name(s) & Qualifier(s)
    # ---
    variant_names, variant_qualifiers = self.np.parse_being_name(field)
    for variant_name in variant_names:
        bvb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        bvb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note ; ^j = ?? (in tables but not used)
    field_lang, field_script = field['3'], field['4']
    for note_text in field.get_subfields('2','j'):
        bvb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      type = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return bvb.build()


def transform_variant_organization(self, field):
    """
    Input:  PyMARC 410 field
    Output: OrgVariantEntry object
    """
    ovb = OrganizationVariantBuilder()

    ...
    ...
    ...
    ...
    ...
    ...

    return ovb.build()


"""
410  See From Reference, Organization Name (R)
    1  Filler (--) for subsumed name xref (Lane: for indention) (R)
    3  Language of entry (Lane) (except English) (R)
    4  Romanization scheme or Script (Lane, cf. language authority) (R)
    5  Preferred form by language (P1 only value; equivalent to 1XX; sorts first) (Lane) (R)
    6  Romanized cluster ID (value R1 must match 1XX; files first; R2 ... sort alpha by first in cluster) (Lane) (R)
    7  ID for included names, L1, L2, etc. (R)
    8  Beginning/earliest date of relationship (Lane) (R)
    9  Single or ending/latest date of relationship (Lane) (R)
    a  Corporate name or jurisdiction name as entry element (R)
    b  Subordinate unit (R)
    d  Date of meeting (R)
    e  Relator term (Lane: 1st subfield) (R)
    j  Note/qualification (Lane) (R)
    n  Number of part/section/meeting (R)
"""


def transform_variant_concept(self, field):
    """
    Input:  PyMARC 450/455/480 field
    Output: ConceptVariantEntry object
    """

    ...
    ...
    ...
    ...
    ...
    ...

    return None


def transform_variant_string(self, field):
    """
    Input:  PyMARC 482 field
    Output: StringVariantEntry object
    """
    svb = StringVariantBuilder()

    # Variant Group Attributes
    # ---
    svb.set_variant_group(id        = field['7'],
                          group     = field['6'],
                          preferred = bool(field['5']))

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        svb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        svb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    ...
    ...
    ...

    # Name(s) & Qualifier(s)
    # ---
    ...
    ...
    ...

    # Note(s)
    # ---
    # n/a?

    return svb.build()
