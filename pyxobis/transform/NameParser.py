#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pyxobis.builders import *
from .Indexer import Indexer
from .DateTimeParser import DateTimeParser
from .tf_common import *


class NameParser:
    def __init__(self):
        """
        Assorted functions related to parsing MARC fields out into names + qualifiers.
        """
        self.ix = Indexer()
        self.dp = DateTimeParser()

        # Build regex for method __strip_being_ending_punctuation
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
                name_text = self.__strip_being_ending_punctuation(val)
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
                    being_name_parts = [(self.__strip_being_ending_punctuation(val), "generic")]

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
                being_name_expansion_text = self.__strip_being_ending_punctuation(val)
                being_name_expansion_text = self.strip_parens(being_name_expansion_text)
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
            val_norm = self.__strip_being_ending_punctuation(val)
            srb.set_link(val_norm,
                         href_URI = self.ix.quick_lookup(val_norm, STRING))
            srb.add_name(val_norm,
                         lang     = field_lang,
                         script   = field_script,
                         nonfiling = 0)
            being_qualifiers.append(srb.build())
        # ^d : Qualifying dates  --> Time/DurationRef
        for val in field.get_subfields('d'):
            being_qualifiers.append(self.dp.parse(val, BEING))

        return being_names_kwargs, being_qualifiers

    def __parse_being_surname_entry(self, namestring):
        """
        100 1# ^a
        Parse a name string into a list of (name_part, type) tuples.
        """
        # Punctuation
        ns = self.__strip_being_ending_punctuation(namestring)
        # Arabic
        ns = ns.replace('،', ',')

        ns_split = ns.split(',', 1)

        # Assume the first is the surname and the rest are given names
        # (too complex to bother trying to determine other types during mapping)
        ns_parsed = [ (name_part.strip(), 'surname' if i==0 else 'given') for i,name_part in enumerate(ns_split) ]

        return ns_parsed

    def __strip_being_ending_punctuation(self, namestring):
        """
        Strip punctuation, based on the particular consideration of personal names.
        """
        ns = namestring.rstrip("،,:/ \t").strip()
        ns = self.name_abbr_pattern.sub("", ns).strip()
        return ns


    def parse_concept_name(self, field):
        """
        Parse a X50/X55/X80 field containing a Concept name into:
        - a list of names as kwarg dicts, and
        - a list of qualifiers as RefElement objects
        to pass into a Builder.
        """
        field_lang, field_script = field['3'], field['4']

        # If this is a 150/155, ^a is name (+ hypothetical ^x is Concept qualifier).
        # If this is a X80, ^x is name.
        # Otherwise, ^a is name, ^x is subdivision.
        #     (don't deal with subdivisions here, delegate to
        #      whatever method is handling the ref builder)

        if field.tag in ['150','155']:
            name_code, qualifier_code = 'a', 'x'
        elif field.tag[1:] == '80':
            name_code, qualifier_code = 'x', ''
        else:
            name_code, qualifier_code = 'a', ''

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
                crb.set_link(val,
                             href_URI = self.ix.quick_lookup(val, CONCEPT))
                crb.add_name(val,
                             lang   = field_lang,
                             script = field_script,
                             nonfiling = 0)
                concept_qualifiers.append(crb.build())

        return concept_names_kwargs, concept_qualifiers



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
        #     + ^l Language?? / ^3 Language of entry??  [LanguageRef]
        string_qualifiers = []
        ...
        ...
        ...

        return string_names_kwargs, string_pos_kwargs, string_qualifiers


    """
    182  Textword (TWA) (Lane defined) (NR)
        0  Authority record control number (RIM) (R)
        3  Language of entry (Lane) (except English; replaces $l) (R)
        4  Romanization scheme (Lane, cf. language authority) (R)
        g  Grammatical type (cf. abbrev. list) (R)
        l  Language (obsolete 3 digit abbrev.) (R)
        q  Qualifier (to distinguish otherwise identical words/phrases) (R)
        y  Word/phrase entry (preferred term, favoring singular nouns) (R)
    482  See From Reference, Textword (Lane defined) (R)
        3  Language of entry (Lane) (except English) (R)
        4  Romanization scheme or Script (Lane) (R)
        7  ID for included variants, L1, L2, etc. (Lane) (R)
        e  Relator term (Lane: 1st subfield) (R)
        g  Grammatical type (cf. abbrev. list) (R)
        l  Language (3 digit abbrev; obsolete, change to $4) (R)
        y  Word/phrase see from reference (R)
    """


    def strip_parens(self, namestring):
        """
        Strip enclosing parentheses.
        """
        ns = re.sub(r"(^[\s\(]+|[\s\)]+$)", "", namestring).strip()
        return ns
