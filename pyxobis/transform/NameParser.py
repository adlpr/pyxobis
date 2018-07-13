#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pyxobis.builders import *
from .Indexer import Indexer
from .tf_common import *


class NameParser:
    def __init__(self):
        """
        Assorted functions related to name processing.
        """
        pass

    ix = Indexer()

    def parse_surname_entry(self, namestring):
        """
        100 1# ^a
        Attempt to parse into a list of form (name_part, type).
        """
        # Punctuation
        ns = self.strip_ending_punctuation(namestring)
        # Arabic
        ns = ns.replace("،", ",")
        ...
        ...
        return ns

    # def parse_forename_entry(self, namestring):
    #     """
    #     100 0# ^a
    #     """
    #     # Punctuation
    #     ns = self.strip_ending_punctuation(namestring)
    #     ...
    #     ...
    #     return ns

    def strip_ending_punctuation(self, namestring):
        """
        Strip punctuation, based on the special needs of names.
        """
        ns = namestring.rstrip("،,:/ ").strip()

        # Strip ending periods only when not part of a recognized abbreviation or initialism.
        name_abbrs = [ r"\p{L}", r"\p{L}\p{M}", r"\p{L}\p{M}\p{M}",
            r"[DdFJMS]r", "Mrs", "Ms", "Mme", "Mons", "Esq", "Capt", "Col",
            r"[LS]t", "Rev", "Bp", "Hrn", r"[Jj]unr", r"[Jj]un",
            r"[Pp]rof", "Dn", "[CS]en", "cit", "med", "phil", "nat", "pseud",
            "Pharm" ]
        pattern = re.compile(''.join(r"(?<!^{0})(?<![ \.]{0})".format(nlb) for nlb in name_abbrs) + r"\.$")
        ns = pattern.sub("", ns).strip()

        return ns
