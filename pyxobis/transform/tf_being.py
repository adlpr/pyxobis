#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re  # import regex as re
from pymarc import Field
from pyxobis.builders import *
from .tf_common import *


def transform_being(self, record):
    bb = BeingBuilder()

    broad_category = record.get_broad_category()
    categories = record.get_all_categories()
    subsets = record.get_subsets()


    # ROLE
    # ---
    # authority / instance / authority instance

    # all authorities (?)
    bb.set_role("authority")


    # TYPE
    # ---
    # human / nonhuman / special

    # 655 29 Beings, Special
    if 'Beings, Special' in categories:
        being_type = 'special'
    # 655 47 Beings, Nonhuman  Z402334
    elif 'Beings, Nonhuman' in categories:
        being_type = 'nonhuman'
    else:
        being_type = 'human'

    bb.set_type(being_type)


    # CLASS
    # ---
    # individual / familial / collective / undifferentiated / referential

    # individual: ind1 = 0 / 1
    # familial:   ind1 = 3 ; 655 47 ^a Persons, Families or Groups
    # collective: ind1 = 9 ; 655 47 ^a Peoples
    # undifferentiated: 655 77 ^a Persons, Undifferentiated
    # referential: things like Mc/Mac, St.: 008/09 = 'b' or 'c'

    if 'Persons, Undifferentiated' in subsets:
        being_class = 'undifferentiated'
    elif record['008'].data[9] in 'bc':
        being_class = 'referential'
    elif broad_category == 'Peoples':
        if record['100'].indicator1 != '9':
            print("PROBLEM", record['001'].data)
        being_class = 'collective'
    elif broad_category == 'Persons, Families or Groups':
        if record['100'].indicator1 != '3':
            print("PROBLEM", record['001'].data)
        being_class = 'familial'
    else:
        if record['100'].indicator1 not in '01':
            print("PROBLEM", record['001'].data)
        being_class = 'individual'

    bb.set_class(being_class)


    # SCHEME
    # ---
    # is it LC for the 100? not really, just ignore this for now...


    # ENTRY TYPE
    # ---
    # Generic type is specific to Being main entries. Birth name, pseudonym, etc.
    # = 100 ^e ?

    being_entry_type = record['100']['e']
    if being_entry_type:
        being_entry_type = being_entry_type.rstrip(':').strip()
        bb.set_entry_type(link_title = being_entry_type,
                          role_URI   = self.ix.quick_lookup("Variant Type", CONCEPT),  # Z48659
                          href_URI   = self.ix.quick_lookup(being_entry_type, CONCEPT))

    # ENTRY NAME(S)
    # ---
    # 100 ^a, ^q (expansion)

    # entry_name_expansion = record['100']['q']
    # if entry_name_expansion:
    #     entry_name_expansion = entry_name_expansion.rstrip('.,')
    # return entry_name_expansion


    # ENTRY TIME/DURATION REF
    # ---
    # This qualifier is specifically for the ENTRY TYPE (^e) : 100 ^8/9 !
    # if record['100']['9']:
    #     self.parse_date(record['100']['9'])


    # ENTRY QUALIFIERS
    # ---
    # 100 ^b (numeration), ^c (titles and other words) as StringRefs,
    # 100 ^d as DurationRef
    if record['100']['d']:
        self.parse_date(record['100']['d'])


    # VARIANTS
    # ---
    # 400
    # variants = []


    # NOTES
    # ---
    #
    # notes = []


    # RELATIONSHIPS
    # ---
    #
    # relationships = []


    return "being"
    return bb.build()
