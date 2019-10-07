#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re

from pymarc import Field

from pylmldb.xobis_constants import *

from ..builders import RelationshipBuilder

from . import tf_common_methods as tfcm

from .Indexer import Indexer
from .DateTimeParser import DateTimeParser as dp


class RelationshipTransformerBib:
    """
    Methods for extracting and building Relationship objects from
    bibliographic pymarc Records.
    """
    def __init__(self, rlt):
        # shared objects and methods from instantiating RelationshipTransformer
        self.get_relation_type = rlt.get_relation_type
        self.build_ref_from_field = rlt.build_ref_from_field
        self.extract_enumeration = rlt.extract_enumeration

    def transform_relationships(self, record):
        """
        For each field describing a relationship
        in bibliographic LaneMARCRecord record,
        build a Relationship.

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

                bib_type = record.leader[6:8]

                # Name/Type
                rel_name = { 'a': "Language of text" if bib_type in ('aa','ab','am','as') or bib_type[0] in 'ef' else "Language",
                             'b': "Language of abstract/summary",
                             'd': "Language of voice",
                             'e': "Language",
                             'f': "Language of table of contents",
                             'g': "Language of accompanying material" }.get(code)
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree: n/a
                # Enumeration: n/a
                # Chronology: n/a

                # Target
                # get main entry subfields of language based on codes
                lang_main_entry_fields = Indexer.reverse_lookup(Indexer.simple_lookup(val, LANGUAGE))
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

                # Notes
                # linked alternate script field(s)
                self.__add_linked_880s_as_notes(record, field.tag, rb)

                relationships.append(rb.build())

        # Projected Publication Date (NR)
        for val in record.get_subfields('263','a'):
            if not val.isdigit():
                continue

            val_normalized = None
            if len(val) == 4:  # YYMM
                yy, mm = val[:2], val[2:]
                val_normalized = f"19{yy}-{mm}" if int(yy) >= 80 else f"20{yy}-{mm}"
            elif len(val) == 6:  # YYYYMM
                val_normalized = f"{val[:4]}-{val[4:]}"
            elif len(val) == 8:  # YYYYMMDD
                val_normalized = f"{val[:4]}-{val[4:6]}-{val[6:]}"
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
            rb.set_target(dp.parse_as_ref(val_normalized))

            # Notes: n/a

            relationships.append(rb.build())

        # Production, Publication, Distribution, Manufacture, and Copyright Notice (R) (R)
        for field in record.get_fields('264'):
            if not (field.indicator2 == '4' and 'c' in field):
                continue

            # remove copyright symbol
            val = field['c'].replace('©','').replace('Ⓒ','').strip()

            rb = RelationshipBuilder()

            # Relationship Name
            rel_name = "Copyright"

            # Name/Type
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Target
            rb.set_target(dp.parse_as_ref(val))

            # Notes: n/a

            relationships.append(rb.build())

        # Citation/References Note (R)
        for field in record.get_fields('510'):
            if 'w' not in field:
                continue

            rb = RelationshipBuilder()

            # Name/Type
            rel_name = "Cited in"
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            if 'c' in field:
                rb.set_enumeration(tfcm.build_simple_ref(field['c'].rstrip(' .'), STRING))

            # Chronology
            if 'b' in field:
                rb.set_time_or_duration_ref(dp.parse_as_ref(field['b'], WORK_INST))

            # Target
            # special case for Garrison & Morton bibliography
            # (commented out 2019-01-09, should be added to data already)
            # 1.1: L133535 ; 1.2 : Q166460 ; 1.3: L81874
            # 2: L92960 ; 3: L1547 ; 4: L11524 ; 5: L74878
            # 6+: L327007
            # if 'a' in field and field['a'] == "Garrison-Morton":
            #     if 'c' in field and not re.search(r'( ed|ed\.)', field['c']):
            #         field.add_subfield('w', 'L327007')
            rb.set_target(self.build_ref_from_field(field, WORK_INST))

            # Notes: n/a

            relationships.append(rb.build())


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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, BEING))

                # Notes:
                for val in field.get_subfields('j'):
                    rb.add_note(val,
                                role = "annotation")

                relationships.append(rb.build())

        # Organization Name as Subject (R) / Organization/Jurisdiction Name, undisplayed/unindexed as phrase (R)
        for field in record.get_fields('610','987'):
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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Target
                rb.set_target(self.build_ref_from_field(field, ORGANIZATION))

                # Notes:
                for val in field.get_subfields('j'):
                    rb.add_note(val,
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

                # Notes
                # linked alternate script field(s)
                self.__add_linked_880s_as_notes(record, field.tag, rb)

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
                assert target_element_type, f"invalid I2 in field: {field}"

                if target_element_type == TIME:
                    # ^x is the second part of a Duration
                    datetime_subject, end_datetime_subject = field['a'] if 'a' in field else '', field['x']
                    if end_datetime_subject:
                        datetime_subject = datetime_subject.rstrip('-') + '-' + end_datetime_subject
                    target_ref = dp.parse_as_ref(datetime_subject, element_type=None)
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
                                role = "documentation")

                # Target(s)
                for keyword_val in field.get_subfields('a'):
                    rb.set_target(tfcm.build_simple_ref(keyword_val, STRING))

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

        # LC Topical Subject (Lane) (R)
        for field in record.get_fields('660'):
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = "Topic"
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree
            rb.set_degree({'1': 'primary',
                           '2': 'secondary'}.get(field.indicator1))

            # Enumeration: n/a
            # Chronology: n/a

            # Target
            # use $a only as target String
            assert 'a' in field, f"{record.get_control_number()}: 660 without $a: {field}"
            for val in field.get_subfields('a'):
                rb.set_target(tfcm.build_simple_ref(val, STRING))

            # Notes
            # preserve full subfielding as Note on Relationship
            rb.add_note(tfcm.concat_subfs(field),
                        role = "description")

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
                rb.set_time_or_duration_ref(tfcm.get_field_chronology(field))

                # Notes
                for code, val in field.get_subfields('u','v','z', with_codes=True):
                    rb.add_note(val,
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

        # Uniform Title, [Series] Added Entry (R)
        for field in record.get_fields('730','830'):
            # from MFHD
            if field.indicator2 == '8':
                continue

            rb = RelationshipBuilder()

            # Name/Type
            rel_name = "Related uniform title" if field.tag == '730' else "Part of series"
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            if 'v' in field:
                rb.set_enumeration(tfcm.build_simple_ref(field['v'], STRING))

            # Chronology
            if 'd' in field:
                rb.set_time_or_duration_ref(dp.parse_as_ref(field['d'], WORK_INST))

            # Notes
            # linked alternate script field(s)
            self.__add_linked_880s_as_notes(record, field.tag, rb)
            # ad hoc subfields for series notes
            for val in field.get_subfields('@'):
                rb.add_note(val,
                            role = "transcription",
                            type_link_title = "Series Note",
                            type_href_URI = Indexer.simple_lookup("Series Note", CONCEPT),
                            type_set_URI = Indexer.simple_lookup("Note Types", CONCEPT))

            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # L22192: 830 should link to WORK_AUT
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            rb.set_target(self.build_ref_from_field(field, WORK_AUT if field.tag == '730' else WORK_INST))

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

            # Notes
            # linked alternate script field(s)
            self.__add_linked_880s_as_notes(record, field.tag, rb)

            rb.set_target(self.build_ref_from_field(field, WORK_INST))

            relationships.append(rb.build())

        # 76x-78x Linking Entry Fields
        for field in record.get_fields('760','762','765','767','770','772','773','775','776','777','780','785','787','789'):
            rel_names = field.get_subfields('e') or [self.__get_linking_entry_field_default_relator(field)]
            for rel_name in rel_names:
                rb = RelationshipBuilder()

                # Name/Type
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree: n/a

                # Enumeration / Chronology

                # before enum/chron, strip "not owned" out of all ^g and ^d and move to notes
                for i, code in enumerate(field.subfields[::2]):
                    if code in 'dg':
                        not_owned_re = re.search(r'(\(?not *owned\)?)', field.subfields[i*2+1], flags=re.I)
                        if not_owned_re:
                            # remove not owned note from that subfield
                            field.subfields[i*2+1] = re.sub(r'\s\s+', ' ', re.sub(r'(\(?not *owned\)?)', '', field.subfields[i*2+1], flags=re.I)).strip()
                            # and add to relationship as note
                            rb.add_note(not_owned_re.group(1),
                                        content_lang = 'eng',
                                        role = "annotation")

                # remove empty subfields
                field.subfields = [e for code, val in zip(field.subfields[::2], field.subfields[1::2]) for e in (code, val) if val.strip()]

                # address 787 ^g inconsistency
                if field.tag == '787' and 'g' in field:
                    # should be ^b = edition, ^d = date of work; ^g = chronology; ^m = enumeration
                    # but these are historically messy, so ^g is often what should be in ^d; try this:
                    # if field has ^b OR (field has ^w AND (^w not indexed OR date from id of ^w matches)), treat ^g as ^d.
                    treat_g_as_d = 'b' in field
                    if not treat_g_as_d and 'w' in field:
                        w_identity = Indexer.reverse_lookup(field['w'])
                        treat_g_as_d = (w_identity is None) or (field['g'] in [val for code, val in zip(w_identity[::2], w_identity[1::2]) if code=='d'])
                    if treat_g_as_d:
                        field.subfields = [e for code, val in zip(field.subfields[::2], field.subfields[1::2]) for e in ('d' if code=='g' else code, val)]

                # figure out enum/chron of relationship
                if field.tag == '773':
                    # ^d = rel chronology; ^g/^m = rel enumeration
                    if 'd' in field:
                        rb.set_time_or_duration_ref(dp.parse_as_ref(field['d'], WORK_INST))
                    if 'm' in field or 'g' in field:
                        rb.set_enumeration(tfcm.build_simple_ref(field['m'] or field['g'], STRING))
                else:
                    # ^b = edition (enum of work); ^d = date (chron) of work; ^g = rel chronology; ^m = rel enumeration
                    if 'g' in field:
                        rb.set_time_or_duration_ref(dp.parse_as_ref(field['g'], WORK_INST))
                    if 'm' in field:
                        rb.set_enumeration(tfcm.build_simple_ref(field['m'], STRING))

                # If the field is only a linked control number
                if not any(code in field for code in 'tpa') and ('w' in field or '0' in field):
                    # parse the 149 at the link as the name
                    target_ctrlno = ("(CStL)" + field['w'].rstrip('. ')) if 'w' in field else field['0'].rstrip('. ')
                    target_identity = Indexer.reverse_lookup(target_ctrlno)
                    # if invalid control number, print warning, use dummy name
                    if not target_identity:
                        print(f"WARNING: {record.get_control_number()}: {field}: invalid href, default title to 'Unknown work'")
                        target_ref = tfcm.build_simple_ref("Unknown work", WORK_INST)
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
                                role = "documentation" if code == 'n' and field.indicator1 != '0' else "annotation",
                                type_link_title = note_type,
                                type_href_URI = Indexer.simple_lookup(note_type, CONCEPT) if note_type else None,
                                type_set_URI = Indexer.simple_lookup("Note Types", CONCEPT) if note_type else None)  # what should this set be??

                relationships.append(rb.build())


        return relationships


    def __add_linked_880s_as_notes(self, record, tag, rb):
        # ^6 130, 630, 730, 740, 830 --> note on relationship
        for field_880 in record.get_fields('880'):
            if '6' in field_880 and field_880['6'][:3] == tag:
                rb.add_note(tfcm.concat_subfs(field_880),
                            role = "transcription")


    # def __preprocess_w_only_linking_fields(self, record):
    #     """
    #     If a 7XX linking field links only a control number,
    #     pull title info into the field itself.
    #     """
    #     for field in record.get_fields():
    #         if field.tag.startswith('7'):
    #             if len(field.subfields) == 2 and 'w' in field:
    #                 linking_ctrlno = "(CStL)" + field['w'].rstrip('. ')
    #                 linking_work_subfields = Indexer.reverse_lookup(linking_ctrlno)
    #                 if not linking_work_subfields:
    #                     # add dummy title
    #                     field.subfields.extend(['t', "Unknown title"])
    #                 else:
    #                     # convert subfield codes
    #                     # linking_work_subfields = []
    #                     print(record['001'].data, linking_ctrlno, linking_work_subfields)
    #     return record


    def __get_linking_entry_field_default_relator(self, field):
        if field.tag in ('780','785'):
            return {'780': {'0': "Continues",
                            '1': "Continues in part",
                            '2': "Supersedes",
                            '3': "Supersedes in part",
                            '4': "Merger of",
                            '5': "Absorbed",
                            '6': "Absorbed in part",
                            '7': "Separated from"},
                    '785': {'0': "Continued by",
                            '1': "Offshoot",
                            '2': "Superseded by",
                            '3': "Superseded in part by",
                            '4': "Absorbed by",
                            '5': "Absorbed in part by",
                            '6': "Split into",
                            '7': "Merged with", # @@@@@@!!!!!
                            '8': "Continued by"}}.get(field.tag).get(field.indicator2, "Related title")
        return {'760': "Main series",
                '762': "Subseries",
                '765': "Translation of",
                '767': "Translated as",
                '770': "Supplement",
                '772': "Supplement to",
                '773': "Component of",
                '775': "Related edition",
                '776': "Also issued as",
                '777': "Issued with",
                '787': "Related title",
                '789': "Related title"}.get(field.tag)
