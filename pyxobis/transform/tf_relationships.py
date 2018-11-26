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

    # for field in record.get_fields(*RELATIONSHIP_FIELDS_BIB):
    # Doing this as one large query then using a switch conditional
    # is a way to retain original order.

    # Language Code (NR)
    for field in record.get_fields('041'):
        for code, val in field.get_subfields('a','b','d','e','f','g', with_codes=True):
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = { 'a': "Language",
                         'b': "Language of abstract/summary",
                         'd': "Language of sung or spoken text",
                         'e': "Language of librettos",
                         'f': "Language of table of contents",
                         'g': "Language of accompanying material" }.get(code)
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            # get main entry subfields of language based on codes
            lang_main_entry_fields = self.ix.reverse_lookup(self.ix.simple_lookup(val, LANGUAGE))
            if not lang_main_entry_fields:
                continue
            rb.set_target(self.build_ref_from_field(Field('   ','  ',lang_main_entry_fields), LANGUAGE))

            # Notes: n/a

            relationships.append(rb.build())

    # Personal Name, Main Entry (NR)
    for field in record.get_fields('100'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e')
        if not rel_names:
            # Determine default relator:
            #   if record is a monograph and "edit" not in 245 ^c, use Author:
            #   else, use Related:
            if record.is_monographic() and not ('c' in record['245'] and re.search(r"(^|\s)edit", record['245']['c'], flags=re.I)):
                rel_names = ["Author"]
            else:
                rel_names = ["Related"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            rb.set_enumeration(self.extract_enumeration(field))

            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, BEING))

            # Notes
            for code, val in field.get_subfields('u','v','z', with_codes=True):
                rb.add_note(val,
                            content_lang = None,
                            role = "transcription")

            relationships.append(rb.build())

    # Organization Name, Main Entry (NR)
    for field in record.get_fields('110'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Related"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree
            rb.set_degree('primary')

            # Enumeration
            rb.set_enumeration(self.extract_enumeration(field))

            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, ORGANIZATION))

            # Notes
            for code, val in field.get_subfields('j','u','v','z', with_codes=True):
                rb.add_note(val,
                            content_lang = None,
                            role = "transcription" if code != 'j' else "annotation")

            relationships.append(rb.build())

    # Event Name, Main Entry (NR) / Added Entry (R)
    for field in record.get_fields('111','711'):
        # Relationship Name(s)
        rel_names = field.get_subfields('j') or ["Related"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree
            rb.set_degree('primary' if field.tag.startswith('1') else 'secondary')

            # Enumeration
            rb.set_enumeration(self.extract_enumeration(field))

            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, EVENT))

            # Notes: n/a

            relationships.append(rb.build())

    # Uniform Title, Main Entry (NR)
    for field in record.get_fields('130'):
        if 'w' in field:  # if not, these are only treated as variants
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = "Realization of"
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, WORK_AUT))

            # Notes: n/a

            relationships.append(rb.build())

    # Projected Publication Date (NR)
    for val in record.get_subfields('263','a'):
        if not val.isdigit():
            continue

        val_normalized = None
        if len(val) == 4:  # YYMM
            yy, mm = val[:2], val[2:]
            val_normalized = "19{}-{}".format(yy, mm) if int(yy) >= 80 else "20{}-{}".format(yy, mm)
        elif len(val) == 6:  # YYYYMM
            val_normalized = "{}-{}".format(val[:4], val[4:])
        elif len(val) == 8:  # YYYYMMDD
            val_normalized = "{}-{}-{}".format(val[:4], val[4:6], val[6:])
        if not val_normalized:
            continue

        rb = RelationshipBuilder()

        # Relationship Name
        rel_name = "Projected publication date"

        # Name/Type
        rb.set_name(rel_name)
        rb.set_type(self.get_relation_type(rel_name))

        # Degree: n/a
        # Enumeration: n/a
        # Chronology: n/a

        # Target
        rb.set_target(self.dp.parse_as_ref(val_normalized))

        # Notes: n/a

        relationships.append(rb.build())

    ...
    ...
    ...

    # Personal Name as Subject (R)
    for field in record.get_fields('600'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject"]
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

    # Organization Name as Subject (R)
    for field in record.get_fields('610'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject"]
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

    # Event Name as Subject (R)
    for field in record.get_fields('611'):
        # Relationship Name(s)
        rel_names = field.get_subfields('j') or ["Subject"]
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
            rb.set_target(self.build_ref_from_field(field, EVENT))

            # Notes: n/a

            relationships.append(rb.build())

    # Title as Subject (R)
    for field in record.get_fields('630'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject"]
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

            # Notes: n/a

            relationships.append(rb.build())

    # Topical Subject (R)
    for field in record.get_fields('650'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Topic"] if field.indicator2 in '23' else ["Subject"]
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
                target_ref = self.dp.parse_as_ref(datetime_subject, element_type=None)
            else:
                target_ref = self.build_ref_from_field(field, target_element_type)
            rb.set_target(target_ref)

            # Notes: n/a

            relationships.append(rb.build())

    # Geographic Subject (R)
    for field in record.get_fields('651'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Subject"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree
            rb.set_degree({'1': 'primary',
                           '2': 'secondary'}.get(field.indicator1))

            # Enumeration: n/a
            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(field, PLACE))

            # Notes:
            for val in field.get_subfields('j'):
                rb.add_note(val,
                            content_lang = None,
                            role = "annotation")

            relationships.append(rb.build())

    # Keyword not otherwise in Record (Lane: separate $a for each word/phrase) (R)
    for field in record.get_fields('653'):
        # Relationship Name(s)
        rel_names = field.get_subfields('e') or ["Keyword"]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = rel_name.rstrip(': ')
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Notes:
            for val in field.get_subfields('c'):
                rb.add_note(val,
                            content_lang = None,
                            role = "documentation")

            # Target(s)
            for keyword_val in field.get_subfields('a'):
                rb.set_target(self.build_simple_ref(keyword_val, STRING))

                relationships.append(rb.build())

    # Category Term (Form/Genre/Format/Subset) (R)
    for field in record.get_fields('655'):
        # ignore subsets and categories imported from MHFD
        if field.indicator1 in '78' or field.indicator2 == '9':
            continue

        rb = RelationshipBuilder()

        # Name/Type
        rel_name = "Category"
        rb.set_name(rel_name)
        rb.set_type(self.get_relation_type(rel_name))

        # Degree
        rb.set_degree({'1': 'primary',
                       '2': 'secondary',
                       '4': 'broad'}.get(field.indicator1))

        # Enumeration: n/a
        # Chronology: n/a

        # Target
        rb.set_target(self.build_ref_from_field(field, CONCEPT))

        # Notes: n/a

        relationships.append(rb.build())

    # Personal / Organization Name, Added Entry (R)
    for field in record.get_fields('700','710'):
        # from MFHD
        if field.indicator2 == '8':
            continue
        rel_names = field.get_subfields('e') or (["Related/analytical title"] if 't' in field else ["Related"])
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            rb.set_enumeration(self.extract_enumeration(field))

            # Chronology
            rb.set_time_or_duration_ref(self.get_field_chronology(field))

            # Notes
            for code, val in field.get_subfields('u','v','z', with_codes=True):
                rb.add_note(val,
                            content_lang = None,
                            role = "transcription")

            if 't' in field:
                # two relationships: one for title, one for author
                rb.set_target(self.build_ref_from_field(field, WORK_INST))
                relationships.append(rb.build())
                # set relator for being/org
                rb.set_name("Author (analytic)")
                rb.set_type(self.get_relation_type("Author (analytic)"))

            rb.set_target(self.build_ref_from_field(field, BEING if field.tag == '700' else ORGANIZATION))
            relationships.append(rb.build())

    # Uniform Title, Added Entry (R)
    for field in record.get_fields('730'):
        # from MFHD
        if field.indicator2 == '8':
            continue

        rb = RelationshipBuilder()

        # Name/Type
        rel_name = "Related uniform title"
        rb.set_name(rel_name)
        rb.set_type(self.get_relation_type(rel_name))

        # Degree: n/a
        # Enumeration: n/a
        # Chronology: n/a
        # Notes: n/a

        rb.set_target(self.build_ref_from_field(field, WORK_AUT))

        relationships.append(rb.build())

    # Variant Title, Added Entry (R)
    for field in record.get_fields('740'):
        # only those marked as analytical titles
        if field.indicator2 != '2':
            continue

        rb = RelationshipBuilder()

        # Name/Type
        rel_name = "Analytical title"
        rb.set_name(rel_name)
        rb.set_type(self.get_relation_type(rel_name))

        # Degree: n/a
        # Enumeration: n/a
        # Chronology: n/a
        # Notes: n/a

        rb.set_target(self.build_ref_from_field(field, WORK_INST))

        relationships.append(rb.build())

    # 76x-78x Linking Entry Fields
    for field in record.get_fields('760','762','765','767','770','772','773','775','776','777','780','785','787','789'):
        rel_names = field.get_subfields('e') or [self.get_linking_entry_field_default_relator(field)]
        for rel_name in rel_names:
            rb = RelationshipBuilder()

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration / Chronology

            # before enum/chron, strip "not owned" out of all ^g AND ^d and move to notes
            for i, code in enumerate(field.subfields[::2]):
                if code in 'dg':
                    not_owned_re = re.search(r'(\(?not *owned\)?)', field.subfields[i*2+1], flags=re.I)
                    if not_owned_re:
                        # remove not owned note from that subfield
                        field.subfields[i*2+1] = re.sub(r'\s\s+', ' ', re.sub(r'(\(?not *owned\)?)', '', field.subfields[i*2+1], flags=re.I), flags=re.I).strip()
                        # and add to relationship as note
                        rb.add_note(not_owned_re.group(1),
                                    content_lang = 'eng',
                                    role = "annotation")

            # ^g is chronology of the relationship (force all to time) EXCEPT 773 and 787
            if field.tag in ('773','787'):
                # ^9 may also occur in 787 [only two though]
                # for 773 and 787:
                #     if ^d or ^9, ^d/^9 is chronology and ^m or ^g is enumeration
                #     if not but ^m, ^m is enumeration, ^g is chronology
                #     if not, check whether ^g is a chronology
                #               if not, treat as an enumeration
                #               [issue: year+season dates?]
                if 'd' in field or '9' in field:
                    rb.set_time_or_duration_ref(self.dp.parse_as_ref(field['d'] or field['9'], WORK_INST))
                    if 'm' in field or 'g' in field:
                        rb.set_enumeration(self.build_simple_ref(field['m'] or field['g'], STRING))
                elif 'm' in field:
                    if 'g' in field:
                        rb.set_time_or_duration_ref(self.dp.parse_as_ref(field['g'], WORK_INST))
                    rb.set_enumeration(self.build_simple_ref(field['m'], STRING))
                elif 'g' in field:
                    # ^g is ambiguous...
                    # for now, if there's a 4-digit year somewhere in there, treat as a chron,
                    # otherwise enum
                    if re.search(r'\d{4}', field['g']):
                        rb.set_time_or_duration_ref(self.dp.parse_as_ref(field['g'], WORK_INST))
                    else:
                        rb.set_enumeration(self.build_simple_ref(field['g'], STRING))
                    ...
                    ...
                    ...
            else:
                # ^m = enumeration; ^d/g = chronology
                if 'm' in field:
                    rb.set_enumeration(self.build_simple_ref(field['m'], STRING))
                if 'd' in field or 'g' in field:
                    rb.set_time_or_duration_ref(self.dp.parse_as_ref(field['d'] or field['g'], WORK_INST))


            # If the field is only a linked control number
            if 't' not in field and ('w' in field or '0' in field):
                # parse the 149 at the link as the name
                target_ctrlno = ("(CStL)" + field['w'].rstrip('. ')) if 'w' in field else field['0'].rstrip('. ')
                target_identity = self.ix.reverse_lookup(target_ctrlno)
                # if invalid control number, print warning, use dummy name
                if not target_identity:
                    print("WARNING: Invalid href: bid {}, field: {}; default title to 'Unknown work'".format(record['001'].data, str(field)))
                    target_ref = self.build_simple_ref("Unknown work", WORK_INST)
                else:
                    target_ref = self.build_ref_from_field(Field('149','  ',target_identity), WORK_INST)
            else:
                target_ref = self.build_ref_from_field(field, WORK_INST)
            rb.set_target(target_ref)

            # Notes
            for code, val in field.get_subfields('k','n','p','s','z', with_codes=True):
                if code == 'p' and 't' not in field:
                    # only include abbr titles if not already being used as main title
                    continue
                note_type = { 'p': 'Abbreviated title',
                              's': 'Uniform title' }.get(code, None)
                rb.add_note(val,
                            content_lang = None,
                            role = "documentation" if code == 'n' and field.indicator1 != '0' else "annotation",
                            type_link_title = note_type,
                            type_href_URI = self.ix.simple_lookup(note_type, RELATIONSHIP) if note_type else None,
                            type_set_URI = self.ix.simple_lookup("Note Types", CONCEPT) if note_type else None)  # what should this set be??

            relationships.append(rb.build())

    ...
    ...
    ...

    return relationships
