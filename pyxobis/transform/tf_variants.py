#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
# from pymarc import Field
from pyxobis.builders import *
from .tf_common import *


def transform_variants(self, record):
    """
    For each field describing a variant in record, build a Variant.
    Returns a list of zero or more VariantEntry objects.

    150 ^m : CONCEPT (MeSH "as Topic")
    210/245/246/247/249 : WORK_INST or OBJECT
    400 : BEING
    410 : ORGANIZATION
    411 : EVENT
    430 : WORK_AUT
    450 : CONCEPT or TIME or LANGUAGE
    451 : PLACE
    455 : CONCEPT or RELATIONSHIP
    480 : CONCEPT (subdivision)
    482 : STRING
    """
    variants = []

    for field, variant_element_type in record.get_variant_fields_and_types():

        transform_variant = {
            WORK_INST    : self.transform_variant_work_instance,
            OBJECT       : self.transform_variant_object,
            WORK_AUT     : self.transform_variant_work_authority,
            BEING        : self.transform_variant_being,
            CONCEPT      : self.transform_variant_concept,
            RELATIONSHIP : self.transform_variant_concept,
            EVENT        : self.transform_variant_event,
            LANGUAGE     : self.transform_variant_language,
            ORGANIZATION : self.transform_variant_organization,
            PLACE        : self.transform_variant_place,
            STRING       : self.transform_variant_string,
            TIME         : self.transform_variant_time
        }.get(variant_element_type)

        if transform_variant:
            variant = transform_variant(field)
            variants.append(variant)

    return variants



def transform_variant_being(self, field):
    """
    Input:  PyMARC 400 field
    Output: BeingVariantEntry object
    """
    bvb = BeingVariantBuilder()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    bvb.set_included(included)

    # Variant Group Attributes
    # ---
    bvb.set_entry_group_attributes(id        = None,
                                   group     = field['6'] or field['7'],
                                   preferred = bool(field['5']) if field['6'] else None)

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
    variant_names_and_qualifiers = self.np.parse_being_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            bvb.add_name(**variant_name_or_qualifier)
        else:
            bvb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note ; ^j = ?? (in tables but not used)
    field_lang, field_script = field['3'], field['4']
    for note_text in field.get_subfields('2','j'):
        bvb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None,
                      type_link_title = None,
                      type_href_URI = None,
                      type_set_URI = None )

    return bvb.build()


def transform_variant_concept(self, field):
    """
    Input:  PyMARC 072/150[m]/450/455/480 field
    Output: ConceptVariantEntry object
    """
    cvb = ConceptVariantBuilder()

    if field.tag == '072':
        # MeSH tree top nodes
        entry_type = "Tree number"
        cvb.set_type(entry_type,
                     self.ix.simple_lookup("Equivalence", CONCEPT),
                     self.ix.simple_lookup(entry_type, RELATIONSHIP))
        cvb.add_name(field['a'])
        return cvb.build()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    cvb.set_included(included)

    # Variant Group Attributes
    # ---
    if field.tag.endswith('55'):  # X55s use ^3/^4 for language/script
        indiv_id = None
        group_id = field['7']
        field_lang = field['3']
        field_script = field['4']
    else:
        indiv_id = field['4']
        group_id = field['3'] or field['7']
        field_lang = None
        field_script = None
    cvb.set_entry_group_attributes(id        = indiv_id,
                                   group     = group_id,
                                   preferred = None)  # no field for this for Concepts

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        cvb.set_type(**type_kwargs)
    if field.tag not in ('450','480'):
        if type_time_or_duration_ref is not None:
            cvb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # I1 8 = MeSH Topical Variant
    #    9 = Local Topical Variant / ^h  Designation as local MeSH xref
    if field.indicator1 == '9' or 'h' in field:
        cvb.set_scheme('LaSH')
    elif field.indicator1 == '8':
        cvb.set_scheme('MeSH')

    # Name(s) & Qualifier(s)
    # ---
    variant_names_and_qualifiers = self.np.parse_concept_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            cvb.add_name(**variant_name_or_qualifier)
        else:
            cvb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note
    for note_text in field.get_subfields('2'):
        cvb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return cvb.build()


def transform_variant_event(self, field):
    """
    Input:  PyMARC 411 field
    Output: EventVariantEntry object
    """
    evb = EventVariantBuilder()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    evb.set_included(included)

    # Variant Group Attributes
    # ---
    evb.set_entry_group_attributes(id        = None,
                                   group     = field['6'] or field['7'],
                                   preferred = bool(field['5']) if field['6'] else None)

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        evb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        evb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # n/a for now

    # Name(s) & (Pre)Qualifier(s)
    # ---
    variant_names_and_qualifiers = self.np.parse_event_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            evb.add_name(**variant_name_or_qualifier)
        else:
            evb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # ^j = Note/qualification
    field_lang, field_script = field['3'], field['4']
    for note_text in field.get_subfields('j'):
        evb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return evb.build()


def transform_variant_language(self, field):
    """
    Input:  PyMARC 450/480 field
    Output: LanguageVariantEntry object
    """
    lvb = LanguageVariantBuilder()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    lvb.set_included(included)

    # Variant Group Attributes
    # ---
    lvb.set_entry_group_attributes(id        = field['4'],
                                   group     = field['3'] or field['7'],
                                   preferred = None)  # no field for this for X50/X80s

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        lvb.set_type(**type_kwargs)
    # if type_time_or_duration_ref is not None:
    #     lvb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Name(s) & Qualifier(s)
    # ---
    variant_names_and_qualifiers = self.np.parse_language_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            lvb.add_name(**variant_name_or_qualifier)
        else:
            lvb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note
    for note_text in field.get_subfields('2','6'):
        lvb.add_note( content_text = note_text,
                      content_lang = None,
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return lvb.build()


def transform_variant_organization(self, field):
    """
    Input:  PyMARC 410 field
    Output: OrgVariantEntry object
    """
    ovb = OrganizationVariantBuilder()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    ovb.set_included(included)

    # Variant Group Attributes
    # ---
    ovb.set_entry_group_attributes(id        = None,
                                   group     = field['6'] or field['7'],
                                   preferred = bool(field['5']) if field['6'] else None)

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        ovb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        ovb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # n/a for now

    # Name(s) & (Pre)Qualifier(s)
    # ---
    variant_names_and_qualifiers = self.np.parse_organization_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            ovb.add_name(**variant_name_or_qualifier)
        else:
            ovb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # ^j = Note/qualification
    field_lang, field_script = field['3'], field['4']
    for note_text in field.get_subfields('j'):
        ovb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return ovb.build()


def transform_variant_place(self, field):
    """
    Input:  PyMARC 451 field
    Output: PlaceVariantEntry object
    """
    pvb = PlaceVariantBuilder()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    pvb.set_included(included)

    # Variant Group Attributes
    # ---
    pvb.set_entry_group_attributes(id        = None,
                                   group     = field['6'] or field['7'],
                                   preferred = bool(field['5']) if field['6'] else None)

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        pvb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        pvb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # n/a for now

    # Name(s) & Qualifier(s)
    # ---
    variant_names_and_qualifiers = self.np.parse_place_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            pvb.add_name(**variant_name_or_qualifier)
        else:
            pvb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note
    for note_text in field.get_subfields('2'):
        pvb.add_note( content_text = note_text,
                      content_lang = None,
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return pvb.build()


def transform_variant_string(self, field):
    """
    Input:  PyMARC 482 field
    Output: StringVariantEntry object
    """
    svb = StringVariantBuilder()

    # insert indicators into fields as appropriate subfields
    if 'e' not in field:
        # if no relator subfield, add one with mapping from indicator 1
        variant_type = { '1' : "Combining form",
                         '2' : "Abbreviation",
                         '3' : "Acronym/initialism",
                         '4' : "Archaic",
                         '6' : "Nonstandard",
                         '9' : "Error" }.get(field.indicator1)
        if variant_type:
            field.add_subfield('e', variant_type)
    # add "British English" as language subfield for ind1==5
    if field.indicator1 == '5' and '3' not in field:
        field.add_subfield('3', "British English")

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    svb.set_included(included)

    # Variant Group Attributes
    # ---
    svb.set_entry_group_attributes(id        = None,
                                   group     = field['6'] or field['7'],
                                   preferred = bool(field['5']) if field['6'] else None)

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if type_kwargs:
        svb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        svb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Name(s) & Qualifier(s)
    # ---
    variant_names_and_qualifiers = self.np.parse_string_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            svb.add_name(**variant_name_or_qualifier)
        else:
            svb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # n/a?

    return svb.build()


def transform_variant_time(self, field):
    """
    Input:  PyMARC 450[/480?] field
    Output: TimeVariantEntry object
    """
    # If ^x, this is a Duration variant
    variant_is_duration = 'x' in field

    tvb = DurationVariantBuilder() if variant_is_duration else TimeVariantBuilder()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    tvb.set_included(included)

    # Variant Group Attributes
    # ---
    tvb.set_entry_group_attributes(id        = field['4'],
                                   group     = field['3'] or field['7'],
                                   preferred = None)  # no field for this for X50/X80s

    # Scheme
    # ---
    # n/a for now

    if variant_is_duration:
        # Calendar (Duration)
        # ---
        # this isn't used but do it anyway
        start_datestring, end_datestring = field['a'], field['x']
        calendar1_kwargs, start_datestring = self.dp.extract_calendar(start_datestring)
        if calendar1_kwargs:
            tvb.set_calendar1(**calendar1_kwargs)
        calendar2_kwargs, end_datestring = self.dp.extract_calendar(end_datestring)
        if calendar2_kwargs:
            tvb.set_calendar2(**calendar2_kwargs)

        # Content (Duration)
        # ---
        # @@@@ this assumes no dual/slash-dates!
        start_time_content_single = self.dp.parse_simple(start_datestring)
        tvb.set_time_content1(start_time_content_single)
        end_time_content_single = self.dp.parse_simple(end_datestring)
        tvb.set_time_content2(end_time_content_single)
    else:
        # Calendar (Time)
        # ---
        datestring = field['a']
        calendar_kwargs, datestring = self.dp.extract_calendar(datestring)
        if calendar_kwargs:
            tvb.set_calendar(**calendar_kwargs)

        # Content (Time)
        # ---
        time_content_single = self.dp.parse_simple(datestring)
        tvb.set_time_content_single(time_content_single)

    # Note(s)
    # ---
    # ^2 = scope note
    for note_text in field.get_subfields('2'):
        tvb.add_note( content_text = note_text,
                      content_lang = None,
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return tvb.build()


def transform_variant_work_authority(self, field):
    """
    Input:  PyMARC 130/430 field
    Output: WorkVariantEntry object
    """
    wvb = WorkVariantBuilder()

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    wvb.set_included(included)

    # Variant Group Attributes
    # ---
    wvb.set_entry_group_attributes(id        = None,
                                   group     = field['6'] or field['7'],
                                   preferred = bool(field['5']) if field['6'] else None)

    # Type / Time/Duration Ref
    # ---
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_relator(field)
    if field.tag == '130':
        type_kwargs = type_kwargs or { 'link_title' : "Uniform title",
                    'set_URI'    : self.ix.simple_lookup("Equivalence", CONCEPT),
                    'href_URI'   : self.ix.simple_lookup("Uniform title", RELATIONSHIP) }
    if type_kwargs:
        wvb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        wvb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # n/a for now

    # Name(s) & Qualifier(s)
    # ---
    variant_names_and_qualifiers = self.np.parse_work_authority_name(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            wvb.add_name(**variant_name_or_qualifier)
        else:
            wvb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # ^j = Note/qualification
    for note_text in field.get_subfields('j'):
        wvb.add_note( content_text = note_text,
                      content_lang = field['3'],
                      role = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return wvb.build()


def transform_variant_work_instance(self, field):
    """
    Input:  PyMARC 210/245/246/247/249 field
    Output: WorkVariantEntry object
    """
    return self.transform_variant_work_instance_or_object(field, WORK_INST)


def transform_variant_object(self, field):
    """
    Input:  PyMARC 210/245/246/247/249 field
    Output: ObjectVariantEntry object
    """
    return self.transform_variant_work_instance_or_object(field, OBJECT)


def transform_variant_work_instance_or_object(self, field, element_type):
    """
    Shared code since they're the same field structure
    """
    if element_type == WORK_INST:
        vb = WorkVariantBuilder()
        name_parser = self.np.parse_work_instance_variant_name
    else:
        vb = ObjectVariantBuilder()
        name_parser = self.np.parse_object_variant_name

    # Included
    # ---
    field, included = self.extract_included_relation(field)
    vb.set_included(included)

    # Variant Group Attributes
    # ---
    # n/a

    # Type / Time/Duration Ref
    # ---
    # Type depends on field tag and indicators.
    type_kwargs, type_time_or_duration_ref = self.get_type_and_time_from_title_field(field)
    if type_kwargs:
        vb.set_type(**type_kwargs)
    if type_time_or_duration_ref is not None:
        vb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # 210 abbreviation schemes
    if field.tag == '210':
        if field.indicator2 == '0':
            vb.set_scheme('ISSN')
        elif field.indicator2 == '5':
            vb.set_scheme('NLM')  # ??

    # Name(s) & Qualifier(s)
    # ---
    variant_names_and_qualifiers = name_parser(field)
    for variant_name_or_qualifier in variant_names_and_qualifiers:
        if isinstance(variant_name_or_qualifier, dict):
            vb.add_name(**variant_name_or_qualifier)
        else:
            vb.add_qualifier(variant_name_or_qualifier)

    # Note(s)
    # ---
    # 247 ^b = Remainder of title
    if field.tag == '247':
        for note_text in field.get_subfields('b'):
            vb.add_note( content_text = note_text,
                         content_lang = field['3'],
                         role = "transcription",
                         link_title = None,
                         href_URI = None,
                         set_URI  = None )
    # 246/7 ^f = Designation of volume and issue number and/or date of a work
    #       ^g = Miscellaneous information
    #         (^f/^g may be pre-parsed out as Entry Type Time/DurationRefs by
    #            parse_work_instance_or_object_variant_name)
    #       ^@ = CUSTOM NOTE SUBFIELD from preprocessing transform of 904 into 246
    if field.tag in ('246','247'):
        for code, note_text in field.get_subfields('f','g','@', with_codes=True):
            vb.add_note( content_text = note_text,
                         content_lang = field['3'],
                         role = "documentation" if code=='@' else "transcription",
                         link_title = None,
                         href_URI = None,
                         set_URI  = None )

    return vb.build()
