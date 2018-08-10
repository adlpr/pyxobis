#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pymarc import Field
from pyxobis.builders import *
from .Indexer import Indexer, UNVERIFIED
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
        being_names_kwargs = []
        for code, val in field.get_subfields('a','q', with_codes=True):

            # Exception for anomalous "author of" entries: call these generic
            if "author of" in val.lower():
                name_text = self.__strip_ending_punctuation(val)
                being_names_kwargs = [{ 'name_text': name_text,
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

                    being_names_kwargs.append({ 'name_text': being_name_part_text,
                                                'type_'    : being_name_part_type,
                                                'lang'     : field_lang,
                                                'script'   : field_script,
                                                'nonfiling' : 0 })
            # 100 ^q : Fuller form of name  (type "expansion")
            else:
                being_name_expansion_text = self.__strip_ending_punctuation(val)
                being_name_expansion_text = self.__strip_parens(being_name_expansion_text)
                being_names_kwargs.append({ 'name_text': being_name_expansion_text,
                                            'type_'    : "expansion",
                                            'lang'     : field_lang,
                                            'script'   : field_script,
                                            'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # ^b Numeration + ^c Titles and other qualifying words  --> StringRef
        being_qualifiers = []
        for val in field.get_subfields('b','c'):
            srb = StringRefBuilder()
            val_norm = self.__strip_ending_punctuation(val)
            srb.set_link(val_norm,
                         href_URI = self.ix.simple_lookup(val_norm, STRING))
            srb.add_name(val_norm,
                         lang     = field_lang,
                         script   = field_script,
                         nonfiling = 0)
            being_qualifiers.append(srb.build())
        # ^d : Qualifying dates  --> Time/DurationRef
        for val in field.get_subfields('d'):
            being_qualifiers.append(self.dp.parse_as_ref(val, BEING))

        return being_names_kwargs, being_qualifiers

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
        Parse a X50/X55/X80 field containing a Concept name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects
        to pass into a Builder.
        """
        if field.tag[1:] == "55":
            field_lang, field_script = field['3'], field['4']
        else:
            # ^3/^4 are taken up in X50/X80 fields by MeSH UIs
            field_lang, field_script = None, None

        # If this is a 150/155, ^a is name (+ hypothetical ^x is Concept qualifier).
        # If this is a X80, ^x is name.
        # Otherwise, ^a is name, ^x is subdivision.
        #     (don't deal with subdivisions here, delegate to
        #      whatever method is handling the ref builder)

        if field.tag in ['150','155','450','455']:
            name_code, qualifier_code = 'a', 'x'
        elif field.tag.endswith('80'):
            name_code, qualifier_code = 'x', ''
        else:
            name_code, qualifier_code = 'a', ''

        if any("Tree number" in rel for rel in field.get_subfields('e')):
            # ignore ^x on MeSH tree number variants
            qualifier_code = ''

        # NAME(S)
        # ---
        concept_names_kwargs = []
        for val in field.get_subfields(name_code):
            concept_names_kwargs.append({ 'name_text': val,
                                          'lang'     : field_lang,
                                          'script'   : field_script,
                                          'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        concept_qualifiers = []
        if qualifier_code:
            for val in field.get_subfields(qualifier_code):
                crb = ConceptRefBuilder()
                crb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, CONCEPT) )
                crb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                concept_qualifiers.append(crb.build())

        return concept_names_kwargs, concept_qualifiers


    # known Org rather than Place names used in Event ^c
    event_subfc_orgs = ["Istituto superiore", "Ciba Foundation"]

    def parse_event_name(self, field):
        """
        Parse a X11 field containing a Event name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        # ^a Meeting name/jurisdiction name as entry element
        # UNLESS ^e Subordinate unit, in which case ^a is prequalifier
        event_names_kwargs = []
        name_code = 'e' if 'e' in field else 'a'
        for val in field.get_subfields(name_code):
            val = self.__strip_ending_punctuation(val)
            event_names_kwargs.append({ 'name_text': val,
                                        'lang'     : field_lang,
                                        'script'   : field_script,
                                        'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        event_qualifiers = []
        for code, val in field.get_subfields('c','d','n', with_codes=True):
            # ^c Location of meeting  --> usually PlaceRef, sometimes OrgRef!
            if code == 'c':
                if any(val.startswith(org) for org in self.event_subfc_orgs):
                    qualifier_element, rb = ORGANIZATION, OrganizationRefBuilder()
                else:
                    qualifier_element, rb = PLACE, PlaceRefBuilder()
                val = self.__strip_ending_punctuation(val)
                rb.set_link( val,
                             href_URI = self.ix.simple_lookup(val, qualifier_element) )
                rb.add_name( val,
                             lang   = field_lang,
                             script = field_script,
                             nonfiling = 0 )
                event_qualifiers.append(rb.build())
            # ^d Date of meeting  --> Time/DurationRef
            elif code == 'd':
                event_qualifiers.append(self.dp.parse_as_ref(val, EVENT))
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
                event_qualifiers.append(srb.build())

        return event_names_kwargs, event_qualifiers

    def parse_event_prequalifiers(self, field):
        """
        Parse a X11 field for
        - a list of prequalifiers as RefElement objects,
        to pass into a Builder.
        """
        event_prequalifiers = []
        # if ^e, then ^a is a prequalifier.
        if 'e' in field:
            # may be an event, org, or place.
            # there aren't many if any of these. so just assume Event
            for val in field.get_subfields('a'):
                val = self.__strip_ending_punctuation(val)
                erb = EventRefBuilder()
                erb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, EVENT) )
                erb.add_name( val,
                              lang   = field['3'],
                              script = field['4'],
                              nonfiling = 0 )
                event_prequalifiers.append(erb.build())
        return event_prequalifiers


    def parse_language_name(self, field):
        """
        Parse a X50 field containing a Language name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        language_names_kwargs = []
        for val in field.get_subfields('a'):
            language_names_kwargs.append({ 'name_text': val,
                                           'lang'     : field_lang,
                                           'script'   : field_script,
                                           'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # Language X50 fields have no qualifiers.
        language_qualifiers = []

        return language_names_kwargs, language_qualifiers


    def parse_organization_name(self, field):
        """
        Parse a X10 field containing an Organization name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        # ^a Corporate name or jurisdiction name as entry element
        # UNLESS ^b Subordinate unit, in which case ^a is prequalifier
        #   (as well as any ^b except the last).
        org_names_kwargs = []
        subordinates = field.get_subfields('b')
        val = subordinates[-1] if subordinates else field['a']
        val = self.__strip_ending_punctuation(val)
        org_names_kwargs.append({ 'name_text': val,
                                  'lang'     : field_lang,
                                  'script'   : field_script,
                                  'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        org_qualifiers = []
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
                org_qualifiers.append(prb.build())
            # ^d Date of meeting  --> Time/DurationRef
            elif code == 'd':
                org_qualifiers.append(self.dp.parse_as_ref(val, ORGANIZATION))
            # ^n Number of part/section/meeting  --> StringRef?
            elif code == 'n':
                val = self.__strip_ending_punctuation(val).rstrip('.').lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                org_qualifiers.append(srb.build())

        return org_names_kwargs, org_qualifiers

    def parse_organization_prequalifiers(self, field):
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
        Parse a X51 field containing a Place name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        # ^a Geographic descriptor
        place_names_kwargs = []
        for val in field.get_subfields('a'):
            place_names_kwargs.append({ 'name_text': val,
                                        'lang'     : field_lang,
                                        'script'   : field_script,
                                        'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # none
        place_qualifiers = []

        return place_names_kwargs, place_qualifiers


    def parse_string_name(self, field):
        """
        Parse a X82 field containing a String name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # NAME(S)
        # ---
        # ^y Word/phrase entry
        string_names_kwargs = []
        for val in field.get_subfields('y'):
            string_names_kwargs.append({ 'name_text': val,
                                         'lang'     : field_lang,
                                         'script'   : field_script,
                                         'nonfiling' : 0 })

        # QUALIFIER(S)
        # ---
        # ^q Qualifier  [StringRef?]
        string_qualifiers = []
        for val in field.get_subfields('q'):
            val = self.__strip_parens(val)
            srb = StringRefBuilder()
            srb.set_link( val,
                          href_URI = self.ix.simple_lookup(val, STRING) )
            srb.add_name( val,
                          lang   = field_lang,
                          script = field_script,
                          nonfiling = 0 )
            string_qualifiers.append(srb.build())
        # ^l Language?? / ^3 Language of entry??  [LanguageRef]
        for val in field.get_subfields('l','3'):
            val = self.__strip_ending_punctuation(val)
            lrb = LanguageRefBuilder()
            lrb.set_link( val,
                          href_URI = self.ix.simple_lookup(val, LANGUAGE) )
            lrb.add_name( val,
                          lang   = field_lang,
                          script = field_script,
                          nonfiling = 0 )
            string_qualifiers.append(lrb.build())

        return string_names_kwargs, string_qualifiers


    def parse_work_authority_name(self, field):
        """
        Parse a X30 field containing a Work aut name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']
        nonfiling = int(field.indicator2) if field.indicator2.isdigit() else 0

        # NAME(S)
        # ---
        # ^a  Uniform title                     --> `generic` title
        # ^n  Number of part/section of a work  --> `section` title
        # ^p  Name of part/section of a work    --> `section` title
        work_aut_names_kwargs = []
        for code, val in field.get_subfields('a','n','p', with_codes=True):
            val = self.__strip_ending_punctuation(val)
            work_aut_names_kwargs.append({ 'name_text': val,
                                           'type_'    : 'generic' if code == 'a' else 'section',
                                           'lang'     : field_lang,
                                           'script'   : field_script,
                                           'nonfiling' : nonfiling if code == 'a' else 0 })

        # QUALIFIER(S)
        # ---
        work_aut_qualifiers = []
        for code, val in field.get_subfields('d','f','l','g','h','k','q','s', with_codes=True):
            # ^d  Date of treaty signing  --> TimeRef
            # ^f  Date of a work          --> TimeRef
            if code in ('d','f'):
                work_aut_qualifiers.append(self.dp.parse_as_ref(val, WORK_AUT))
            # ^l  Language of a work      --> LanguageRef
            elif code == 'l':
                val = self.__strip_ending_punctuation(val)
                lrb = LanguageRefBuilder()
                lrb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, LANGUAGE) )
                lrb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_aut_qualifiers.append(lrb.build())
            # ^q  Qualifier (Lane)  --> variety of refs
            elif code == 'q':
                # naive attempt to separate these out
                # print(val)
                # 1. clean punctuation
                val = self.__strip_parens(self.__strip_ending_punctuation(val))
                # 2. separate on ' : '
                for val_part in val.split(' : '):
                    # 3. if \d{4}, parse as date
                    if re.search(r'\d{4}', val_part):
                        # print("is a parsable time")
                        work_aut_qualifiers.append(self.dp.parse_as_ref(val_part, WORK_AUT))
                        continue
                    # 4. if '. ', separate into ^a/^b+ and try to lookup as org; if found parse as such
                    if '. ' in val_part:
                        bespoke_subfields = [sf_part for i,val_subpart in enumerate(val_part.split('. ')) for sf_part in ('a' if i==0 else 'b', val_subpart)]
                        bespoke_field = Field('   ','  ',bespoke_subfields)
                        lookup_as_org = self.ix.lookup(bespoke_field, ORGANIZATION)
                        if lookup_as_org != UNVERIFIED:
                            # print("is an org with subdivisions")
                            orb = OrganizationRefBuilder()
                            orb.set_link( val_part,
                                          href_URI = lookup_as_org )
                            for prequalifier in self.parse_organization_prequalifiers(bespoke_field):
                                orb.add_prequalifier ( prequalifier )
                            orb.add_name( bespoke_subfields[-1],
                                          lang   = field_lang,
                                          script = field_script,
                                          nonfiling = 0 )
                            work_aut_qualifiers.append(orb.build())
                            continue
                    # 5. otherwise attempt to look up element type with indexer
                    val_part = re.sub(r"^\s*U\.?\s*S\.?\s*$", "United States", val_part)
                    element_type = self.ix.simple_element_type_from_value(val_part)
                    # 6. finally, if all else fails, treat as string
                    if element_type == TIME: element_type = STRING
                    element_type = element_type or STRING
                    # build the ref
                    rb_class = { BEING    : BeingRefBuilder,
                                 CONCEPT  : ConceptRefBuilder,
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
                                        'lang'      : field_lang,
                                        'script'    : field_script,
                                        'nonfiling'  : 0 }
                    if element_type in [BEING, WORK_INST, WORK_AUT]:
                        ref_name_kwargs['type_'] = 'generic'
                    rb.add_name(**ref_name_kwargs)
                    work_aut_qualifiers.append(rb.build())
            # ^g  Miscellaneous information  --> StringRef?  [unused]
            # ^h  Medium                     --> StringRef?
            # ^k  Form subheading            --> StringRef?
            # ^s  Version                    --> StringRef?  [unused]
            else:
                val = self.__strip_ending_punctuation(val).rstrip('.').lstrip('( ')
                srb = StringRefBuilder()
                srb.set_link( val,
                              href_URI = self.ix.simple_lookup(val, STRING) )
                srb.add_name( val,
                              lang   = field_lang,
                              script = field_script,
                              nonfiling = 0 )
                work_aut_qualifiers.append(srb.build())

        return work_aut_names_kwargs, work_aut_qualifiers


    # work instance
    def parse_work_instance_main_name(self, field):
        """
        Parse a 149 field containing a Work inst main entry name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        ...
        ...
        ...
        """
        149  Uniform Entry (Lane-Experimental) (NR)
            1  Nonfiling characters (articles, punct., etc. excluded from filing) (NR)
            3  Language of entry (except English) (R)
            4  Romanization scheme (NR)
            a  Uniform title (NR)
            d  Date of a work (NR)
            h  Medium (NR)
            k  Form subheading (R)
            l  Language of a work (NR)
            n  Number of part/section of a work (R)
            p  Name of part/section of a work (R)
            q  Qualifier (NR)
            s  Version/edition (NR)
            w  Lane control no. (autocopied here) (NR)
        """

    def parse_work_instance_variant_name(self, field):
        """
        Parse a 2XX field containing a Work inst variant entry name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects,
        to pass into a Builder.
        """
        ...
        ...
        ...

    # object [149? 245/6?]
    ...
    ...
    ...


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
