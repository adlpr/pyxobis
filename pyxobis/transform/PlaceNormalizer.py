#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from .tf_common import *


class PlaceNormalizer:
    def __init__(self):
        pass

    def normalize(self, placestring):
        """
        Normalize a Place string for lookup.
        """
        # Various preprocessing normalization
        # Punctuation
        ps = re.sub(r"\s*\)\s*\.+$", ')', placestring).rstrip("،,:;/ \t").strip()
        ps = re.sub(r"^[\s\(]+((?:[^\(\)]|\([^\(\)]*\))+)[\s\)]+$", r"\1", ps).strip()
        ps = re.sub(r"^[\(]((?:[^\(\)]|\([^\(\)]*\))+)$", r'\1', ps).strip()
        ps = re.sub(r"^((?:[^\(\)]|\([^\(\)]*\))+)[\)]$", r'\1', ps).strip()

        # Abbreviations
        ps = re.sub(r" +N\.?Y\.?([ ,;:/]|$)", r" New York\1", ps)
        ps = re.sub(r" +Calif\.?([ ,;:/]|$)", r" California\1", ps)
        ps = re.sub(r" +Wash\.?([ ,;:/]|$)", r" Washington\1", ps)

        # Misspellings
        ps = re.sub(r"Phillippines", r"Philippines", ps)

        # Qualifications
        ps = re.sub(r"New York, New York(?! \()", "New York, New York (State)", ps)

        if not ps:
            return None

        return ps
