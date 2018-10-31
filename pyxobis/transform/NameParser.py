#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pymarc import Field
from pyxobis.builders import *
from .Indexer import Indexer
from .DateTimeParser import DateTimeParser
from .PlaceNormalizer import PlaceNormalizer
from .tf_common import *


class NameParser:
    def __init__(self):
        """
        Methods for parsing MARC fields out into names + qualifiers
        based on principal element.
        """
        self.ix = Indexer()
        self.dp = DateTimeParser()
        self.pn = PlaceNormalizer()

        # Build regex for method __strip_ending_punctuation
        # Strip ending periods only when not part of a recognized abbreviation or initialism.
        name_abbrs = [ r"\p{L}", r"-\p{L}", r"\p{L}\p{M}", r"\p{L}\p{M}\p{M}",
            r"[DdFJMS]r", "Mrs", "Ms", "Mme", "Mons", "Esq", "Capt", "Col",
            r"[LS]t", "Rev", "Bp", "Hrn", r"[Jj]unr", r"[Jj]un",
            r"[Pp]rof", "Dn", r"[CS]en", "cit", "med", "phil", "nat", "pseud",
            "Pharm" ]
        self.name_abbr_pattern = re.compile(''.join(r"(?<!^{0})(?<![\s\.]{0})".format(nlb) for nlb in name_abbrs) + r"\.$")


    def parse_being_name(self, field):
        """
        Parse a X00 field containing a Being name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """

        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        # ^a Personal name + ^q Fuller form of name
        being_names_and_qualifiers = []
        for code, val in field.get_subfields('a','q', with_codes=True):

            # Exception for anomalous "author of" entries: call these generic
            if "author of" in val.lower():
                name_text = self.__strip_ending_punctuation(val)
                being_names_and_qualifiers = [{ 'name_text': name_text,
                                               'type_'    : "generic",
                                               'lang'     : field_lang,
                                               'script'   : field_script,
                                               'nonfiling' : 0 }]
                break

            # 100 ^a : Personal name
            if code == 'a':
                if field.indicator1 == '1':
                    # If surname entry, attempt to parse into typed parts
                    being_name_parts = self.__parse_being_surname_entry(val)
                else:
                    # Forename, family, and named peoples entries get type "generic"
                    being_name_parts = [(self.__strip_ending_punctuation(val), "generic")]

                for i, being_name_part in enumerate(being_name_parts):
                    being_name_part_text, being_name_part_type = being_name_part

                    # if there is any ^q in the field, the rest of the name
                    # cannot be type "generic". just assume it's a "given" name.
                    if 'q' in field and being_name_part_type == "generic":
                        being_name_part_type = "given"

                    # if there is more than one ^a in the field,
                    # these also can't be "generic". assume "given"
                    if field.count('a') > 1 and being_name_part_type == "generic":
                        being_name_part_type = "given"

                    being_names_and_qualifiers.append({ 'name_text': being_name_part_text,
                                                'type_'    : being_name_part_type,
                                                'lang'     : field_lang,
                                                'script'   : field_script,
                                                'nonfiling' : 0 })
            # 100 ^q : Fuller form of name  (type "expansion")
            else:
                being_name_expansion_text = self.__strip_ending_punctuation(val)
                being_name_expansion_text = self.__strip_parens(being_name_expansion_text)
                being_names_and_qualifiers.append({ 'name_text': being_name_expansion_text,
                                            'type_'    : "expansion",
                                            'lang'     : field_lang,
                                            'script'   : field_script,
                                            'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # ^b Numeration + ^c Titles and other qualifying words  --> StringRef
        for val in field.get_subfields('b','c'):
            srb = StringRefBuilder()
            val_norm = self.__strip_ending_punctuation(val)
            srb.set_link(val_norm,
                         href_URI = self.ix.simple_lookup(val_norm, STRING))
            srb.add_name(val_norm,
                         lang     = field_lang,
                         script   = field_script,
                         nonfiling = 0)
            being_names_and_qualifiers.append(srb.build())
        # ^d : Qualifying dates  --> Time/DurationRef
        for val in field.get_subfields('d'):
            being_names_and_qualifiers.append(self.dp.parse_as_ref(val, BEING))

        return being_names_and_qualifiers

    def __parse_being_surname_entry(self, namestring):
        """
        100 1# ^a
        Parse a name string into a list of (name_part, type) tuples.
        """
        # Punctuation
        ns = self.__strip_ending_punctuation(namestring)
        # Arabic
        ns = ns.replace('،', ',')

        ns_split = ns.split(',', 1)

        # Assume the first is the surname and the rest are given names
        # (too complex to bother trying to determine other types during mapping)
        ns_parsed = [ (name_part.strip(), 'surname' if i==0 else 'given') for i,name_part in enumerate(ns_split) ]

        return ns_parsed



    def parse_concept_name(self, field):
        """
        Parse a X50/X55/X80 field containing a Concept name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a Builder.
        """
        if field.tag[1:] == "55":
            field_lang, field_script = field['3'], field['4']
        else:
            # ^3/^4 are taken up in X50/X80 fields by MeSH UIs
            field_lang, field_script = None, None

        # If this is a 150/155, ^a is name
        #     (hypothetical ^x is Concept qualifier / precomposed concept
        #      w/ subdivision).
        # If this is a X80, ^x is name.
        # Otherwise, ^a is name, ^x is subdivision.
        #     (don't deal with subdivisions here, delegate to
        #      whatever method is handling the builder)

        if any("Tree number" in rel for rel in field.get_subfields('e')):
            # Tree number is always ^a (even on X80s)
            # and the ^x should be ignored
            name_code, qualifier_code = 'a', ''
        elif field.tag in ['150','155','450','455']:
            name_code, qualifier_code = 'a', 'x'
        elif field.tag.endswith('80'):
            name_code, qualifier_code = 'x', ''
        else:
            name_code, qualifier_code = 'a', ''

        # NAME(S)
        # ---
        concept_names_and_qualifiers = []
        for val in field.get_subfields(name_code):
            concept_names_and_qualifiers.append({ 'name_text': val,
                                          'lang'     : field_lang,
                                          'script'   : field_script,
                                          'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        if qualifier_code:
            for val in field.get_subfields(qualifier_code):
                crb = ConceptRefBuilder()
                crb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, CONCEPT) )
                crb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                concept_names_and_qualifiers.append(crb.build())

        return concept_names_and_qualifiers


    # known Org rather than Place names used in Event ^c
    event_subfc_orgs = ["Istituto superiore", "Ciba Foundation"]

    def parse_event_name(self, field):
        """
        Parse a X11 field containing a Event name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # PREQUALIFIER(S)
        # ---
        event_names_and_qualifiers = self.__parse_event_prequalifiers(field)

        # NAME(S)
        # ---
        # ^a Meeting name/jurisdiction name as entry element
        # UNLESS ^e Subordinate unit, in which case ^a is prequalifier
        name_code = 'e' if 'e' in field else 'a'
        for val in field.get_subfields(name_code):
            val = self.__strip_ending_punctuation(val)
            event_names_and_qualifiers.append({ 'name_text': val,
                                        'lang'     : field_lang,
                                        'script'   : field_script,
                                        'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        for code, val in field.get_subfields('c','d','n', with_codes=True):
            # ^c Location of meeting  --> usually PlaceRef, sometimes OrgRef!
            if code == 'c':
                val = self.__strip_ending_punctuation(val)
                if any(val.startswith(org) for org in self.event_subfc_orgs):
                    qualifier_element, rb = ORGANIZATION, OrganizationRefBuilder()
                else:
                    qualifier_element, rb = PLACE, PlaceRefBuilder()
                    val = self.pn.normalize(val)
                rb.set_link( val,
                             href_URI = self.ix.simple_lookup(val, qualifier_element) )
                rb.add_name( val,
                             lang   = field_lang,
                             script = field_script,
                             nonfiling = 0 )
                event_names_and_qualifiers.append(rb.build())
            # ^d Date of meeting  --> Time/DurationRef
            elif code == 'd':
                event_names_and_qualifiers.append(self.dp.parse_as_ref(val, EVENT))
            # ^n Number of part/section/meeting  --> StringRef?
            elif code == 'n':
                val = self.__strip_ending_punctuation(val).lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                event_names_and_qualifiers.append(srb.build())

        return event_names_and_qualifiers

    def __parse_event_prequalifiers(self, field):
        """
        Parse a X11 field for a list of prequalifiers (RefElements),
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        event_prequalifiers = []
        # if ^e, then ^a is a prequalifier.
        if 'e' in field:
            # is ^a Org or Place? ^b are always going to be orgs
            if field.indicator1 == '1':
                prequalifier_element, rb = PLACE, PlaceRefBuilder()
            else:
                prequalifier_element, rb = EVENT, EventRefBuilder()
            # ^a
            for val in field.get_subfields('a'):
                val = self.__strip_ending_punctuation(val)
                if prequalifier_element == PLACE:
                    val = self.pn.normalize(val)
                rb.set_link( val,
                             href_URI = self.ix.simple_lookup(val, prequalifier_element) )
                rb.add_name( val,
                             lang   = field_lang,
                             script = field_script,
                             nonfiling = 0 )
                event_prequalifiers.append(rb.build())
            # there aren't many if any of these. so just assume Event
            for val in field.get_subfields('e')[:-1]:
                val = self.__strip_ending_punctuation(val)
                erb = EventRefBuilder()
                erb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, EVENT) )
                erb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                event_prequalifiers.append(erb.build())
        return event_prequalifiers


    def parse_language_name(self, field):
        """
        Parse a X50 field containing a Language name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        language_names_and_qualifiers = []
        for val in field.get_subfields('a'):
            language_names_and_qualifiers.append({ 'name_text': val,
                                                  'lang'     : field_lang,
                                                  'script'   : field_script,
                                                  'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # n/a

        return language_names_and_qualifiers


    def parse_organization_name(self, field):
        """
        Parse a X10 field containing an Organization name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # PREQUALIFIER(S)
        # ---
        organization_names_and_qualifiers = self.__parse_organization_prequalifiers(field)

        # NAME(S)
        # ---
        # ^a Corporate name or jurisdiction name as entry element
        # UNLESS ^b Subordinate unit, in which case ^a is prequalifier
        #   (as well as any ^b except the last).
        subordinates = field.get_subfields('b')
        val = subordinates[-1] if subordinates else field['a']
        val = self.__strip_ending_punctuation(val)
        organization_names_and_qualifiers.append({ 'name_text': val,
                                                  'lang'     : field_lang,
                                                  'script'   : field_script,
                                                  'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        for code, val in field.get_subfields('c','d','n', with_codes=True):
            # ^c Location of meeting  --> PlaceRef
            if code == 'c':
                val = self.pn.normalize(val)
                prb = PlaceRefBuilder()
                prb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, PLACE) )
                prb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                organization_names_and_qualifiers.append(prb.build())
            # ^d Date of meeting  --> Time/DurationRef
            elif code == 'd':
                organization_names_and_qualifiers.append(self.dp.parse_as_ref(val, ORGANIZATION))
            # ^n Number of part/section/meeting  --> StringRef
            elif code == 'n' and field.tag != '710':
                val = self.__strip_ending_punctuation(val).rstrip('.').lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                organization_names_and_qualifiers.append(srb.build())

        return organization_names_and_qualifiers

    def __parse_organization_prequalifiers(self, field):
        """
        Parse a X10 field for
        - a list of prequalifiers as RefElement objects,
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        org_prequalifiers = []

        # if ^b, then ^a and any ^b except the last is a prequalifier.
        if 'b' in field:
            # is ^a Org or Place? ^b are always going to be orgs
            if field.indicator1 == '1':
                prequalifier_element, rb = PLACE, PlaceRefBuilder()
            else:
                prequalifier_element, rb = ORGANIZATION, OrganizationRefBuilder()
            # ^a
            for val in field.get_subfields('a'):
                if prequalifier_element == PLACE:
                    val = self.pn.normalize(val)
                val = self.__strip_ending_punctuation(val)
                rb.set_link( val,
                             href_URI = self.ix.simple_lookup(val, prequalifier_element) )
                rb.add_name( val,
                             lang   = field_lang,
                             script = field_script,
                             nonfiling = 0 )
                org_prequalifiers.append(rb.build())
            # ^b
            for val in field.get_subfields('b')[:-1]:
                val = self.__strip_ending_punctuation(val)
                orb = OrganizationRefBuilder()
                orb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, ORGANIZATION) )
                orb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                org_prequalifiers.append(orb.build())

        return org_prequalifiers


    def parse_place_name(self, field):
        """
        Parse a X51 field containing a Place name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        # ^a Geographic descriptor
        place_names_and_qualifiers = []
        for val in field.get_subfields('a'):
            place_names_and_qualifiers.append({ 'name_text': val,
                                               'lang'     : field_lang,
                                               'script'   : field_script,
                                               'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # 651 ^z ? [not used]

        return place_names_and_qualifiers


    def parse_string_name(self, field):
        """
        Parse a X82 field containing a String name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        # ^y Word/phrase entry
        string_names_and_qualifiers = []
        for val in field.get_subfields('y'):
            string_names_and_qualifiers.append({ 'name_text': val,
                                                'lang'     : field_lang,
                                                'script'   : field_script,
                                                'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # ^q Qualifier  [StringRef]
        for val in field.get_subfields('q'):
            val = self.__strip_parens(val)
            srb = StringRefBuilder()
            srb.set_link( val,
                          href_URI = self.ix.simple_lookup(val, STRING) )
            srb.add_name( val,
                          lang   = field_lang,
                          script = field_script,
                          nonfiling = 0 )
            string_names_and_qualifiers.append(srb.build())
        # ^l Language [defunct] / ^3 Language of entry  [LanguageRef]
        for val in field.get_subfields('l','3'):
            val = self.__strip_ending_punctuation(val)
            lrb = LanguageRefBuilder()
            lrb.set_link( val,
                          href_URI = self.ix.simple_lookup(val, LANGUAGE) )
            lrb.add_name( val,
                          lang   = field_lang,
                          script = field_script,
                          nonfiling = 0 )
            string_names_and_qualifiers.append(lrb.build())

        return string_names_and_qualifiers


    def parse_work_authority_name(self, field):
        """
        Parse a X30 field containing a Work aut name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a WorkBuilder.
        """
        field_lang, field_script = field['3'], field['4']
        # for some reason nonfiling is I1 on bibs, I2 on auts
        nonfiling = 0
        if field.indicator1.isdigit():
            nonfiling = int(field.indicator1)
        elif field.tag != '630' and field.indicator2.isdigit():
            nonfiling = int(field.indicator2)

        # NAME(S) & QUALIFIER(S)
        # ---
        work_aut_names_and_qualifiers = []
        for code, val in field.get_subfields('a','p','d','f','g','k','l','q','n','s', with_codes=True):
            if code in 'ap':
                # ^a  Uniform title                     --> `generic` title
                # ^p  Name of part/section of a work    --> `section` title
                val = self.__strip_ending_punctuation(val)
                work_aut_names_and_qualifiers.append(
                    { 'name_text': val,
                      'type_'    : 'generic' if code == 'a' else 'section',
                      'lang'     : field_lang,
                      'script'   : field_script,
                      'nonfiling' : nonfiling if code == 'a' else 0 } )
            elif code in 'df':
                # ^d  Date of treaty signing  --> TimeRef
                # ^f  Date of a work          --> TimeRef
                work_aut_names_and_qualifiers.append(self.dp.parse_as_ref(val, WORK_AUT))
            elif code == 'k':
                # ^k  Form subheading            --> ConceptRef
                val = self.__strip_ending_punctuation(val)
                crb = ConceptRefBuilder()
                crb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, CONCEPT) )
                crb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_aut_names_and_qualifiers.append(crb.build())
            elif code == 'l':
                # ^l  Language of a work      --> LanguageRef
                val = self.__strip_ending_punctuation(val)
                lrb = LanguageRefBuilder()
                lrb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, LANGUAGE) )
                lrb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_aut_names_and_qualifiers.append(lrb.build())
            elif code in 'gq':
                # ^q  Qualifier (Lane)  --> parse
                # ^g  Miscellaneous information  --> parse
                work_aut_names_and_qualifiers.extend(self.parse_generic_qualifier(val, field_lang, field_script))
            else:
                # ^n  Number of part/section of a work  --> StringRef
                # ^s  Version                    --> StringRef
                val = self.__strip_ending_punctuation(val).rstrip('.').lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_aut_names_and_qualifiers.append(srb.build())

        # ^h  Medium                     --> SHOULD GO TO HOLDINGS

        return work_aut_names_and_qualifiers


    def __parse_work_instance_or_object_main_name(self, field, element_type):
        """
        Parse a 149/730/740 field containing a Work inst/Object main entry name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a WorkBuilder.
        """
        field_lang, field_script = field['3'], field['4']
        # ^1  Nonfiling characters (articles, punct., etc. excluded from filing) (NR)
        nonfiling = 0
        if '1' in field:
            nonfiling = len(field['1'])
            field['a'] = field['1'] + field['a']
        elif field.tag in ('730','740'):
            try:
                nonfiling = int(field.indicator1)
            except:
                pass

        # NAME(S) & QUALIFIER(S)
        # ---
        work_inst_or_object_main_names_and_qualifiers = []
        for code, val in field.get_subfields('a','p','d','f','g','l','q','n','k','s', with_codes=True):
            if code in 'ap':
                # ^a  Uniform title (NR)                    --> `generic` title
                # ^p  Name of part/section of a work (R)    --> `section` title
                val = self.__strip_ending_punctuation(val)
                name_kwargs = { 'name_text': val,
                                'lang'     : field_lang,
                                'script'   : field_script,
                                'nonfiling' : nonfiling if code == 'a' else 0 }
                if element_type == WORK_INST:
                    name_kwargs['type_'] = 'generic' if code == 'a' else 'section'
                work_inst_or_object_main_names_and_qualifiers.append(name_kwargs)
            elif code in 'df':
                # ^d  Date of a work (NR)        --> Time/DurationRef
                work_inst_or_object_main_names_and_qualifiers.append(self.dp.parse_as_ref(val, WORK_INST))
            elif code == 'k':
                # ^k  Form subheading (R)        --> ConceptRef
                val = self.__strip_ending_punctuation(val)
                crb = ConceptRefBuilder()
                crb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, CONCEPT) )
                crb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_inst_or_object_main_names_and_qualifiers.append(crb.build())
            elif code == 'l':
                # ^l  Language of a work (NR)    --> LanguageRef
                val = self.__strip_ending_punctuation(val)
                lrb = LanguageRefBuilder()
                lrb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, LANGUAGE) )
                lrb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_inst_or_object_main_names_and_qualifiers.append(lrb.build())
            elif code in 'gq':
                # ^q  Qualifier (NR)   --> parse
                parsed = self.parse_generic_qualifier(val, field_lang, field_script)
                work_inst_or_object_main_names_and_qualifiers.extend(parsed)
            else:
                # ^n  Number of part/section of a work (R)  --> StringRef
                # ^s  Version/edition (NR)                  --> StringRef
                val = self.__strip_ending_punctuation(val).rstrip('.').lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_inst_or_object_main_names_and_qualifiers.append(srb.build())

        # ^h  Medium (NR)  --> SHOULD GO TO HOLDINGS

        return work_inst_or_object_main_names_and_qualifiers

    def __parse_work_instance_or_object_variant_name(self, field, element_type):
        """
        Parse a 210/245/246/247/249 field containing a
        Work inst/Object variant entry name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']
        if field.tag == '245' and field.indicator2.isdigit():
            nonfiling = int(field.indicator2)
        else:
            nonfiling = 0

        # NAME(S) & QUALIFIER(S)
        # ---
        # other ^b  Remainder of title (NR)     --> Main Note
        # ^c  Remainder of title page transcription/statement of responsibility (NR)  --> Main Note
        work_inst_or_object_variant_names_and_qualifiers = []
        for code, val in field.get_subfields('a','p','b','f','g','k','q','n','s', with_codes=True):
            if code in 'ap':
                # ^a  * title (NR)                        --> `generic` title
                # ^p  Name of part/section of a work (R)  --> `section` title
                val = self.__strip_ending_punctuation(val)
                name_kwargs = { 'name_text': val,
                                'lang'     : field_lang,
                                'script'   : field_script,
                                'nonfiling' : nonfiling if code == 'a' else 0 }
                if element_type == WORK_INST:
                    name_kwargs['type_'] = 'generic' if code == 'a' else 'section'
                work_inst_or_object_variant_names_and_qualifiers.append(name_kwargs)
            elif code == 'b':
                if field.tag == '210':
                    # 210 ^b    Qualifying information (NR) --> parse
                    parsed = self.parse_generic_qualifier(val, field_lang, field_script)
                    work_inst_or_object_variant_names_and_qualifiers.extend(parsed)
            elif code in 'fg':
                if field.tag == '245':
                    # 245 ^f    Inclusive dates (NR)        --> Time/DurationRef
                    # 245 ^g    Bulk dates (NR)             --> Time/DurationRef
                    work_inst_or_object_variant_names_and_qualifiers.append(self.dp.parse_as_ref(val, WORK_INST))
            elif code == 'k':
                # ^k  Form (R)             --> ConceptRef
                val = self.__strip_ending_punctuation(val)
                crb = ConceptRefBuilder()
                crb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, CONCEPT) )
                crb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_inst_or_object_variant_names_and_qualifiers.append(crb.build())
            elif code == 'q':
                # ^q  Qualifier (Lane) (NR)  --> parse
                parsed = self.parse_generic_qualifier(val, field_lang, field_script)
                work_inst_or_object_variant_names_and_qualifiers.extend(parsed)
            else:
                # ^n  Number of part/section of a work (R)   --> StringRef
                # ^s  Version (Lane) (NR)   --> StringRef
                val = self.__strip_ending_punctuation(val).rstrip('.').lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_inst_or_object_variant_names_and_qualifiers.append(srb.build())

        return work_inst_or_object_variant_names_and_qualifiers

    def __parse_author_title_work_name(self, field):
        """
        Parse a 700/710 field containing a Work inst name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a WorkRefBuilder.
        """
        # 700 uses f h k l n p q s t; 710 only uses n p t
        field_codes = 'fhklnpqst' if field.tag == '700' else 'npt'

        # NAME(S) & QUALIFIER(S)
        # ---
        author_title_work_names_and_qualifiers = []
        for code, val in field.get_subfields(*field_codes, with_codes=True):
            if code in 'tp':
                # ^t  Title of work (NR)                    --> `generic` title
                # ^p  Name of part/section of a work (R)    --> `section` title
                val = self.__strip_ending_punctuation(val)
                name_kwargs = { 'name_text': val,
                                'type_': 'generic' if code == 't' else 'section' }
                author_title_work_names_and_qualifiers.append(name_kwargs)
            elif code == 'f':
                # ^f  Date of work (NR)          --> Time/DurationRef
                author_title_work_names_and_qualifiers.append(self.dp.parse_as_ref(val, WORK_INST))
            elif code == 'k':
                # ^k  Form subheading (R)        --> ConceptRef
                val = self.__strip_ending_punctuation(val)
                crb = ConceptRefBuilder()
                crb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, CONCEPT) )
                crb.add_name( val )
                author_title_work_names_and_qualifiers.append(crb.build())
            elif code == 'l':
                # ^l  Language of a work (NR)    --> LanguageRef
                val = self.__strip_ending_punctuation(val)
                lrb = LanguageRefBuilder()
                lrb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, LANGUAGE) )
                lrb.add_name( val )
                author_title_work_names_and_qualifiers.append(lrb.build())
            else:
                # ^n  Number of part/section of a work (R)  --> StringRef
                # ^s  Version/edition (NR)                  --> StringRef
                val = self.__strip_ending_punctuation(val).rstrip('.').lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val )
                author_title_work_names_and_qualifiers.append(srb.build())

        return author_title_work_names_and_qualifiers

    def __parse_linking_entry_work_name(self, field):
        """
        Parse a 76X~78X field containing a Work inst main entry name
        into a list of either names (kwarg dicts) or qualifiers (RefElements),
        to pass into a WorkRefBuilder.
        """
        field_lang, field_script = field['3'], field['4']

        ...
        ...
        ...


    def parse_work_instance_main_name(self, field):
        if field.tag in ('700','710'):
            return self.__parse_author_title_work_name(field)
        elif field.tag[:2] in ('76','77','78'):
            return self.__parse_linking_entry_work_name(field)
        return self.__parse_work_instance_or_object_main_name(field, WORK_INST)

    def parse_object_main_name(self, field):
        return self.__parse_work_instance_or_object_main_name(field, OBJECT)

    def parse_work_instance_variant_name(self, field):
        return self.__parse_work_instance_or_object_variant_name(field, WORK_INST)

    def parse_object_variant_name(self, field):
        return self.__parse_work_instance_or_object_variant_name(field, OBJECT)


    def parse_generic_qualifier(self, val, lang=None, script=None):
        """
        Use regex and Indexer to try to determine what type of reference to build
        from an unspecified qualifying element.

        Defaults to String if better guess unable to be determined.

        Returns list of RefElements.
        """
        ref_elements = []
        # 1. clean punctuation
        val = self.__strip_parens(self.__strip_ending_punctuation(val))
        # 2. separate on ' : '
        for val_part in val.split(' : '):
            # 3. if \d{4} in part, attempt parse as date
            if re.search(r'\d{4}', val_part):
                try:
                    ref_elements.append(self.dp.parse_as_ref(val_part, None))
                    continue
                except ValueError:
                    pass
            # 4. if '. ', separate into ^a/^b+ and attempt lookup as org; if found parse as such
            if '. ' in val_part:
                bespoke_subfields = [sf_part for i,val_subpart in enumerate(val_part.split('. ')) for sf_part in ('a' if i==0 else 'b', val_subpart)]
                bespoke_field = Field('   ','  ',bespoke_subfields)
                lookup_as_org = self.ix.lookup(bespoke_field, ORGANIZATION)
                if lookup_as_org != Indexer.UNVERIFIED:
                    # yes, this is a subdivided org
                    orb = OrganizationRefBuilder()
                    orb.set_link( val_part,
                                  href_URI = lookup_as_org )
                    for prequalifier in self.__parse_organization_prequalifiers(bespoke_field):
                        orb.add_qualifier(prequalifier)
                    orb.add_name( bespoke_subfields[-1],
                                  lang   = lang,
                                  script = script,
                                  nonfiling = 0 )
                    ref_elements.append(orb.build())
                    continue
            # 5. otherwise attempt to look up element type with indexer
            val_part = re.sub(r"(^|[\s\(])U\.?\s*S\.?([\s\)]|$)", r"\1United States\2", val_part, flags=re.I)
            val_part = re.sub(r"(^|[\s\(])N\.?\s*Y\.?([\s\)]|$)", r"\1New York (State)\2", val_part, flags=re.I)
            val_part = re.sub(r"(^|[\s\(])N\.?\s*J\.?([\s\)]|$)", r"\1New Jersey\2", val_part, flags=re.I)
            val_part = re.sub(r"(^|[\s\(])Calif\.?([\s\)]|$)", r"\1California\2", val_part, flags=re.I)
            val_part = re.sub(r"(^|[\s\(])Md\.([\s\)]|$)", r"\1Maryland\2", val_part, flags=re.I)
            val_part = re.sub(r"(^|[\s\(])Mass\.([\s\)]|$)", r"\1Massachusetts\2", val_part, flags=re.I)
            val_part = re.sub(r"(^|[\s\(])Dept\.?([\s\)]|$)", r"\1Department\2", val_part, flags=re.I)
            element_type = self.ix.simple_element_type_from_value(val_part)
            # 6. finally, if all else fails, treat as string
            if element_type == TIME: element_type = STRING
            element_type = element_type or STRING
            # build the ref
            rb_class = { BEING    : BeingRefBuilder,
                         CONCEPT  : ConceptRefBuilder,
                         RELATIONSHIP : ConceptRefBuilder,
                         EVENT    : EventRefBuilder,
                         LANGUAGE : LanguageRefBuilder,
                         OBJECT   : ObjectRefBuilder,
                         ORGANIZATION : OrganizationRefBuilder,
                         PLACE    : PlaceRefBuilder,
                         STRING   : StringRefBuilder,
                         # TIME : TimeRefBuilder,  # not allowed
                         WORK_AUT : WorkRefBuilder,
                         WORK_INST: WorkRefBuilder
                       }.get(element_type)
            rb = rb_class()
            rb.set_link( val_part,
                         href_URI = self.ix.simple_lookup(val_part, element_type) )
            ref_name_kwargs = { 'name_text' : val_part,
                                'lang'      : lang,
                                'script'    : script,
                                'nonfiling'  : 0 }
            if element_type in [BEING, WORK_INST, WORK_AUT]:
                ref_name_kwargs['type_'] = 'generic'
            rb.add_name(**ref_name_kwargs)
            ref_elements.append(rb.build())
        return ref_elements


    def __strip_ending_punctuation(self, namestring):
        """
        Strip punctuation, based on the particular considerations of personal names.
        """
        ns = self.name_abbr_pattern.sub("", namestring.rstrip("،,:;/ \t").strip()).strip()
        return ns

    def __strip_parens(self, namestring):
        """
        Strip enclosing parentheses.
        """
        ns = re.sub(r"^[\s\(]+((?:[^\(\)]|\([^\(\)]*\))+)[\s\)]+$", r"\1", namestring).strip()
        ns = re.sub(r"^[\(]((?:[^\(\)]|\([^\(\)]*\))+)$", r'\1', ns).strip()
        ns = re.sub(r"^((?:[^\(\)]|\([^\(\)]*\))+)[\)]$", r'\1', ns).strip()
        return ns
