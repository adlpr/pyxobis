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
    # is it LC for the 100 when 010? not really, just ignore this for now


    # ENTRY TYPE
    # ---
    # Generic "entry type" is specific to Beings: birth name, pseudonym, etc.

    being_entry_type = record['100']['e']
    if being_entry_type:
        being_entry_type = being_entry_type.rstrip(':').strip()
        bb.set_entry_type( link_title = being_entry_type,
                           role_URI   = self.ix.quick_lookup("Variant Type", CONCEPT),
                           href_URI   = self.ix.quick_lookup(being_entry_type, CONCEPT) )

    # ENTRY NAME(S)
    # ---

    being_entry_lang, being_entry_script = record['100']['3'], record['100']['4']

    # 100 ^a : Personal name +
    # 100 ^q : Fuller form of name
    for code, val in record['100'].get_subfields('a','q', with_codes=True):
        if code == 'a':
            if record['100'].indicator1 == '1':
                # If surname entry, attempt to parse into typed parts
                being_name_parts = self.np.parse_surname_entry(val)
            else:
                # Forename, family, and named peoples entries get type "generic"
                being_name_parts = [(self.np.strip_ending_punctuation(val), "generic")]

            for name_part in being_name_parts:
                being_name_part_text, being_name_part_type = being_name_part

                # if there is any ^q in the field, the rest of the name
                # cannot be type "generic". just assume it's a "given" name.
                if 'q' in record['100'] and being_name_part_type == "generic":
                    being_name_part_type = "given"

                bb.add_name( being_name_part_text,
                             type_  = being_name_part_type,
                             lang   = being_entry_lang,
                             script = being_entry_script,
                             nonfiling = 0 )
        else:
            # Expansion
            being_name_text = self.np.strip_ending_punctuation(val)
            bb.add_name( being_name_text,
                         type_  = "expansion",
                         lang   = being_entry_lang,
                         script = being_entry_script,
                         nonfiling = 0 )


    # ENTRY TIME/DURATION REF
    # ---
    # Specifically refers to the ENTRY TYPE (^e) : 100 ^8/^9 !
    start_type_datetime, end_type_datetime = record['100']['8'], record['100']['9']
    type_datetime = start_type_datetime + end_type_datetime  \
                    if start_type_datetime and end_type_datetime  \
                    else end_type_datetime or start_type_datetime
    if type_datetime:
        bb.set_time_or_duration_ref(self.dp.parse(type_datetime, None))


    # ENTRY QUALIFIERS
    # ---
    # 100 ^b : Numeration +
    # 100 ^c : Titles and other qualifying words  (StringRef)
    for val in record.get_subfields('100','b') + record.get_subfields('100','c'):
        srb = StringRefBuilder()
        val_norm = self.np.strip_ending_punctuation(val)
        print(val_norm)
        srb.set_link(val_norm,
                     href_URI = self.ix.quick_lookup(val_norm, STRING))
        srb.add_name(val_norm,
                     lang = being_entry_lang,
                     script = being_entry_script,
                     nonfiling = 0)
        bb.add_qualifier(srb.build())
    # 100 ^d : Qualifying dates  (Time/DurationRef)
    for val in record.get_subfields('100','d'):
        bb.add_qualifier(self.dp.parse(val, BEING))


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


    return BEING
    return bb.build()
