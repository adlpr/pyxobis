#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
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

    if 'Beings, Special' in categories:
        # 655 29 Beings, Special
        being_type = 'special'
    elif 'Beings, Nonhuman' in categories:
        # 655 47 Beings, Nonhuman
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

    being_class = None
    if 'Persons, Undifferentiated' in subsets:
        being_class = 'undifferentiated'
    elif record['008'].data[9] in 'bc':
        being_class = 'referential'
    elif broad_category == 'Peoples':
        if record['100'].indicator1 != '9':
            print("PROBLEM: Peoples without ind 9#: {}".format(record['001'].data))
        else:
            being_class = 'collective'
    elif broad_category == 'Persons, Families or Groups':
        if record['100'].indicator1 != '3':
            print("PROBLEM: Family/Group without ind 3#: {}".format(record['001'].data))
        being_class = 'familial'
    else:
        if record['100'].indicator1 not in '01':
            print("PROBLEM: Individual without ind [01]#: {}".format(record['001'].data))
        being_class = 'individual'

    bb.set_class(being_class)


    # SCHEME
    # ---
    # is it LC for the 100 when 010? not really, consider this n/a for now


    # ENTRY TYPE
    # ---
    # Generic "entry type" is specific to Beings: birth name, pseudonym, etc.
    entry_type_kwargs, entry_type_time_or_duration_ref = self.get_type_and_time_from_relator(record['100'])
    if entry_type_kwargs:
        bb.set_entry_type(**entry_type_kwargs)

    # ENTRY NAME(S) AND QUALIFIERS
    # ---
    entry_names, entry_qualifiers = self.np.parse_being_name(record['100'])
    for entry_name in entry_names:
        bb.add_name(**entry_name)
    for entry_qualifier in entry_qualifiers:
        bb.add_qualifier(entry_qualifier)


    # VARIANTS
    # ---
    # 400 / 410 / 411 / 430 / 450 / 451 / 455 / 482

    for variant in self.transform_variants(record):
        bb.add_variant(variant)

    # ctrlno = record.get_control_number()
    # for field in record.get_fields('410','450','482'):
    #     print(ctrlno, field)


    # NOTES
    # ---
    #
    # notes = []

    return bb.build()
