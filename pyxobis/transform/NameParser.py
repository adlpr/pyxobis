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
        Assorted functions related to name processing.
        """
        self.ix = Indexer()
        self.dp = DateTimeParser()

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

            # Exception for anomalous "author of" entries
            if "author of" in val.lower():
                name_text = self.strip_ending_punctuation(val)
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
                    being_name_parts = self.parse_surname_entry(val)
                else:
                    # Forename, family, and named peoples entries get type "generic"
                    being_name_parts = [(self.strip_ending_punctuation(val), "generic")]

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
                being_name_expansion_text = self.strip_ending_punctuation(val)
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
            val_norm = self.strip_ending_punctuation(val)
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

    def parse_surname_entry(self, namestring):
        """
        100 1# ^a
        Parse a name string into a list of (name_part, type) tuples.
        """
        # Punctuation
        ns = self.strip_ending_punctuation(namestring)
        # Arabic
        ns = ns.replace('،', ',')

        ns_split = ns.split(',', 1)

        # Assume the first is the surname and the rest are given names
        # (too complex to bother trying to determine other types during mapping)
        ns_parsed = [ (name_part.strip(), 'surname' if i==0 else 'given') for i,name_part in enumerate(ns_split) ]

        return ns_parsed

    # Strip ending periods only when not part of a recognized abbreviation or initialism.
    name_abbrs = [ r"\p{L}", r"-\p{L}", r"\p{L}\p{M}", r"\p{L}\p{M}\p{M}",
        r"[DdFJMS]r", "Mrs", "Ms", "Mme", "Mons", "Esq", "Capt", "Col",
        r"[LS]t", "Rev", "Bp", "Hrn", r"[Jj]unr", r"[Jj]un",
        r"[Pp]rof", "Dn", "[CS]en", "cit", "med", "phil", "nat", "pseud",
        "Pharm" ]
    name_abbr_pattern = re.compile(''.join(r"(?<!^{0})(?<![\s\.]{0})".format(nlb) for nlb in name_abbrs) + r"\.$")

    def strip_ending_punctuation(self, namestring):
        """
        Strip punctuation, based on the particular consideration of personal names.
        """
        ns = namestring.rstrip("،,:/ \t").strip()
        ns = self.name_abbr_pattern.sub("", ns).strip()
        return ns

    def strip_parens(self, namestring):
        """
        Strip enclosing parentheses.
        """
        ns = re.sub(r"(^[\s\(]+|[\s\)]+$)", "", namestring).strip()
        return ns
