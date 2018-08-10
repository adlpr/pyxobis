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
    record_element_type = record.get_xobis_element_type()

    variants = []

    for field in record.get_variant_fields():

        if field.tag == '150':
            concept_variant = self.transform_variant_concept(field)
            variants.append(concept_variant)

        elif field.tag.startswith('2'):
            # WORK_INST or OBJECT
            if record_element_type == WORK_INST:
                # work_inst_variant = self.transform_variant_work_instance(field)
                # variants.append(work_inst_variant)
                ...
                ...
                ...
            else:
                # object_variant = self.transform_variant_object(field)
                # variants.append(object_variant)
                ...
                ...
                ...

        elif field.tag == '400':
            # BEING
            being_variant = self.transform_variant_being(field)
            variants.append(being_variant)

        elif field.tag == '410':
            # ORGANIZATION
            organization_variant = self.transform_variant_organization(field)
            variants.append(organization_variant)

        elif field.tag == '411':
            # EVENT
            event_variant = self.transform_variant_event(field)
            variants.append(event_variant)

        elif field.tag == '430':
            # WORK_AUT
            work_aut_variant = self.transform_variant_work_authority(field)
            variants.append(work_aut_variant)

        elif field.tag == '450':
            # CONCEPT or TIME or LANGUAGE
            # Assume variant is the same type as the heading;
            # if it doesn't match it's most likely a CONCEPT
            if record_element_type == TIME:
                time_variant = self.transform_variant_time(field)
                variants.append(time_variant)
            elif record_element_type == LANGUAGE:
                language_variant = self.transform_variant_language(field)
                variants.append(language_variant)
            else:
                concept_variant = self.transform_variant_concept(field)
                variants.append(concept_variant)

        elif field.tag == '451':
            # PLACE
            place_variant = self.transform_variant_place(field)
            variants.append(place_variant)

        elif field.tag == '455':
            # CONCEPT or RELATIONSHIP
            concept_variant = self.transform_variant_concept(field)
            variants.append(concept_variant)

        elif field.tag == '480':
            # CONCEPT
            concept_variant = self.transform_variant_concept(field)
            variants.append(concept_variant)

        elif field.tag == '482':
            # STRING
            string_variant = self.transform_variant_string(field)
            variants.append(string_variant)

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


def transform_variant_concept(self, field):
    """
    Input:  PyMARC 150[m]/450/455/480 field
    Output: ConceptVariantEntry object
    """
    cvb = ConceptVariantBuilder()

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
    if type_time_or_duration_ref is not None:
        cvb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # n/a for now

    # Name(s) & Qualifier(s)
    # ---
    variant_names, variant_qualifiers = self.np.parse_concept_name(field)
    for variant_name in variant_names:
        cvb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        cvb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note
    for note_text in field.get_subfields('2'):
        cvb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      type = "annotation",
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

    # Prequalifier(s)
    # ---
    variant_prequalifiers = self.np.parse_event_prequalifiers(field)
    for prequalifier in variant_prequalifiers:
        evb.add_prequalifier(prequalifier)

    # Name(s) & Qualifier(s)
    # ---
    variant_names, variant_qualifiers = self.np.parse_event_name(field)
    for variant_name in variant_names:
        evb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        evb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^j = Note/qualification
    field_lang, field_script = field['3'], field['4']
    for note_text in field.get_subfields('j'):
        evb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      type = "annotation",
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
    if type_time_or_duration_ref is not None:
        lvb.set_time_or_duration_ref(type_time_or_duration_ref)

    # Substitute
    # ---
    # n/a for now

    # Name(s) & Qualifier(s)
    # ---
    variant_names, variant_qualifiers = self.np.parse_language_name(field)
    for variant_name in variant_names:
        lvb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        lvb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note
    for note_text in field.get_subfields('2'):
        lvb.add_note( content_text = note_text,
                      content_lang = None,
                      type = "annotation",
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

    # Prequalifier(s)
    # ---
    variant_prequalifiers = self.np.parse_organization_prequalifiers(field)
    for prequalifier in variant_prequalifiers:
        ovb.add_prequalifier(prequalifier)

    # Name(s) & Qualifier(s)
    # ---
    variant_names, variant_qualifiers = self.np.parse_organization_name(field)
    for variant_name in variant_names:
        ovb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        ovb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^j = Note/qualification
    field_lang, field_script = field['3'], field['4']
    for note_text in field.get_subfields('j'):
        ovb.add_note( content_text = note_text,
                      content_lang = field_lang,
                      type = "annotation",
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
    variant_names, variant_qualifiers = self.np.parse_place_name(field)
    for variant_name in variant_names:
        pvb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        pvb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^2 = scope note
    for note_text in field.get_subfields('2'):
        pvb.add_note( content_text = note_text,
                      content_lang = None,
                      type = "annotation",
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
    variant_names, variant_qualifiers = self.np.parse_string_name(field)
    for variant_name in variant_names:
        svb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        svb.add_qualifier(variant_qualifier)

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
                      type = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return tvb.build()


def transform_variant_work_authority(self, field):
    """
    Input:  PyMARC 430 field
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
    variant_names, variant_qualifiers = self.np.parse_work_authority_name(field)
    for variant_name in variant_names:
        wvb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        wvb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^j = Note/qualification
    for note_text in field.get_subfields('j'):
        wvb.add_note( content_text = note_text,
                      content_lang = field['3'],
                      type = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return wvb.build()



def transform_variant_work_instance(self, field):
    """
    Input:  PyMARC 210/245/246/247/249 field
    Output: WorkVariantEntry object
    """
    wvb = WorkVariantBuilder()

    # Included
    # ---
    # n/a

    # Variant Group Attributes
    # ---
    # n/a

    # Type / Time/Duration Ref
    # ---
    # Type depends on field tag and indicators.
    type_kwargs = self.get_type_and_time_from_title_field(field)
    if type_kwargs:
        wvb.set_type(**type_kwargs)
    # Time/Duration is n/a

    # Substitute
    # ---
    # n/a for now

    # Scheme
    # ---
    # 210 _5 = NLM abbrev
    if field.tag == '210' and field.indicator2 == '5':
        wvb.set_scheme('NLM')  # ??

    # Name(s) & Qualifier(s)
    # ---
    variant_names, variant_qualifiers = self.np.parse_work_instance_variant_name(field)
    for variant_name in variant_names:
        wvb.add_name(**variant_name)
    for variant_qualifier in variant_qualifiers:
        wvb.add_qualifier(variant_qualifier)

    # Note(s)
    # ---
    # ^j = Note/qualification
    ...
    ...
    ...
    for note_text in field.get_subfields('j'):
        wvb.add_note( content_text = note_text,
                      content_lang = field['3'],
                      type = "annotation",
                      link_title = None,
                      href_URI = None,
                      set_URI  = None )

    return wvb.build()

    """
	210  Abbreviated Title (R)
		Ind1
			0  No title added entry (abbrev same as title)
			1  Title added entry
		Ind2
			0  Standard abbrev of 245 title (Lane doesn't use key title)
			5  NLM abbrev (Only when different from standard)
			9  Other abbrev
		a  Abbreviated title (NR)
		b  Qualifying information (NR)
		h  Medium (Lane) (NR)
	245  Title Statement (NR)
		Ind1
			0  No title added entry
			1  Title added entry
		Ind2
			0  nonfiling character
			1  nonfiling character
			2  nonfiling characters
			3  nonfiling characters
			4  nonfiling characters
			5  nonfiling characters
			6  nonfiling characters
			7  nonfiling characters
			8  nonfiling characters
			9  nonfiling characters
		3  Language of entry (Lane) (except English) (R)
		4  Romanization scheme (Lane) (NR)
		a  Title (NR)
		b  Remainder of title (NR)
		c  Remainder of title page transcription/statement of responsibility (NR)
		f  Inclusive dates (NR)
		g  Bulk dates (NR)
		h  Medium (NR)
		k  Form (R)
		n  Number of part/section of a work (R)
		p  Name of part/section of a work (R)
		q  Qualifier (Lane) (NR)
		s  Version (NR)
	246  Variant Title (R)
		Ind1
			0  No title added entry
			1  Title added entry
			2  No note, no title added entry
			3  No note, title added entry
		3  Language of entry (Lane) (except English) (R)
		4  Romanization scheme (Lane) (NR)
		a  Title proper/short title (NR)
		f  Designation of volume and issue number and/or date of a work (NR)
		g  Miscellaneous information (NR)
		h  Medium (NR)
		i  Display text (NR)
		n  Number of part/section of a work (R)
		p  Name of part/section of a work (R)
		q  Qualifier (Lane) (NR)
		s  Version (Lane) (NR)
	247  Former Title or Title Variations (R)
		Ind1
			0  No title added entry
			1  Title added entry
		Ind2
			0  Display note
			1  Do not display note
		3  Language of entry (Lane) (except English) (R)
		4  Romanization scheme (Lane) (NR)
		a  Title proper/short title (NR)
		b  Remainder of title (NR)
		f  Designation of volume and issue number and/or date of a work (NR)
		g  Miscellaneous information (NR)
		h  Medium (NR)
		n  Number of part/section of a work (R)
		p  Name of part/section of a work (R)
		q  Qualifier (Lane) (NR)
		s  Version (Lane) (NR)
	249  Added Title for Website (Lane) (R)
		a  Added title for website (Lane) (NR)
    """


def transform_variant_object(self, field):
    """
    Input:  PyMARC 245/246 field
    Output: ObjectVariantEntry object
    """
    ...
    ...
    ...
