#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Enables quick lookup of a record ID by identity tuple.
"""

import os
from pymarc import MARCReader, Field
from .LaneMARCRecord import LaneMARCRecord
from .tf_common import *

from tqdm import tqdm

INDEX = None
INDEX_REVERSE = None
INDEX_REL_TYPE = None

# @@@@@@ TEMPORARY, ONLY WORKS FROM DIR WITH THESE FILES,
#        DO SOMETHING BETTER WITH INPUT FILENAMES
BIB_INF_NAME = "bibmfhd.20181004"
AUT_INF_NAME = "aut.20181004"


class Indexer:
    # constants for lookups unable to be resolved,
    # either due to conflict or having no match
    CONFLICT   = "conflict"
    UNVERIFIED = "unverified"

    def __init__(self, inf_names=(BIB_INF_NAME, AUT_INF_NAME)):
        # Store index as json (for now, maybe change to pickle later?)
        global INDEX, INDEX_REVERSE, INDEX_REL_TYPE
        self.index, self.index_reverse = INDEX, INDEX_REVERSE
        self.index_rel_type = INDEX_REL_TYPE
        if not all((INDEX, INDEX_REVERSE, INDEX_REL_TYPE)):
            # read index from file, or generate it
            import json
            try:
                with open("index.json",'r') as inf:
                    self.index = json.load(inf)
                with open("index_reverse.json",'r') as inf:
                    self.index_reverse = json.load(inf)
                with open("index_rel_type.json",'r') as inf:
                    self.index_rel_type = json.load(inf)
            except:
                self.__generate_index(inf_names)
                with open("index.json",'w') as outf:
                    json.dump(self.index, outf)
                with open("index_reverse.json",'w') as outf:
                    json.dump(self.index_reverse, outf)
                with open("index_rel_type.json",'w') as outf:
                    json.dump(self.index_rel_type, outf)
            INDEX, INDEX_REVERSE = self.index, self.index_reverse
            INDEX_REL_TYPE = self.index_rel_type

    def __generate_index(self, inf_names):
        # Generate index from given input MARC files.
        print("generating index in {}...".format(os.getcwd()))

        # forward index (main or variant identity string --> ctrl number/conflict)
        index, index_variants = {}, {}
        conflicts, conflicts_variants = set(), set()
        # reverse index (ctrl number --> authorized form string)
        index_reverse = { self.UNVERIFIED: None, self.CONFLICT: None }
        # relationship type index (relationship name --> list of types)
        index_rel_type = {}
        all_rel_types = set(["Subordinate", "Superordinate", "Preordinate",
            "Postordinate", "Associative", "Dissociative", "Equivalence"])

        for inf_name in inf_names:
            with open(inf_name,'rb') as inf:
                reader = MARCReader(inf)
                for record in tqdm(reader):
                # for record in reader:
                    record.__class__ = LaneMARCRecord

                    # if relationship, add to rel type index
                    if record.get_broad_category() == 'Relationships':
                        rel_types = sorted(list(all_rel_types & set(record.get_all_categories())))
                        rel_name = record['155']['a']
                        index_rel_type[rel_name] = rel_types

                    # main indices
                    ctrlno, element_type, id_string, auth_form = record.get_identity_information()
                    if element_type and id_string:
                        # Record has a valid identity, add to indices
                        # Reverse
                        index_reverse[ctrlno] = auth_form
                        # Forward
                        # Main entry:
                        if element_type not in index:
                            index[element_type] = {}
                        if id_string in index[element_type]:
                            # Multiple main entries have this same identity tuple
                            conflicts.add((element_type, id_string))
                        else:
                            index[element_type][id_string] = ctrlno
                        # Variant entries:
                        for variant_element_type, variant_id_string in record.get_variant_types_and_ids():
                            if variant_element_type not in index_variants:
                                index_variants[variant_element_type] = {}
                            if variant_id_string in index_variants[variant_element_type]:
                                # Multiple variants have this same identity tuple
                                conflicts_variants.add((variant_element_type, variant_id_string))
                            else:
                                index_variants[variant_element_type][variant_id_string] = ctrlno

        # Go back and mark conflicts:
        # Conflicts within main identities
        for element_type, conflict in conflicts:
            index[element_type][conflict] = self.CONFLICT
        # Conflicts within variant identities
        for element_type, conflict in conflicts_variants:
            index_variants[element_type][conflict] = self.CONFLICT
        # If a variant identity is the same as a main identity,
        # the main one wins out
        for element_type, id_map in index.items():
            if element_type in index_variants:
                main_id_strings = set(id_map.keys())
                variant_id_strings = set(index_variants[element_type].keys())
                colliding_id_strings = main_id_strings & variant_id_strings
                for id_string in colliding_id_strings:
                    index_variants[element_type].pop(id_string)

        # Finally merge main and variant together
        for element_type, id_map in index.items():
            if element_type in index_variants:
                index[element_type].update(index_variants[element_type])

        self.index, self.index_reverse = index, index_reverse
        self.index_rel_type = index_rel_type

    def lookup(self, field, element_type):
        """
        Given a pymarc field interpreted as a particular XOBIS element type,
        look up its associated control number.
        Identities with multiple ctrl nos will return CONFLICT;
        with none, will return UNVERIFIED
        """
        assert element_type in self.index, "element type {} not indexed".format(element_type)
        identity = LaneMARCRecord.get_identity_from_field(field, element_type)
        value = self.index[element_type].get(identity)
        return self.UNVERIFIED if value is None else value

    def simple_lookup(self, text, element_type=None):
        """
        Given just a single string of text, assume it is the value of the
        primary subfield of an identity, and look up its associated control number.

        Useful for Builders to look up Types for set control.
        (could Type control numbers maybe live in some separate cache?)

        If element type is unspecified, only returns a matching value if there is
        an unambigous match to one element type.
        """
        element_type = element_type or self.element_type_from_value(text)
        if element_type is None:
            return self.UNVERIFIED
        assert element_type in self.index, "element type {} not indexed".format(element_type)
        subf = LaneMARCRecord.IDENTITY_SUBFIELD_MAP[element_type][0]
        return self.lookup(Field('   ','  ',[subf, text]), element_type)

    def reverse_lookup(self, ctrlno):
        """
        Given a control number, return identity subfield list of the main entry
        of the associated record,
        or None if not found.
        """
        main_entry = self.index_reverse.get(ctrlno)
        if main_entry is None:
            return None
        return main_entry.split(LaneMARCRecord.UNNORMALIZED_SEP)

    def lookup_rel_types(self, rel_name):
        # get rid of Equivalence (only used for Variant Types, not Relationships)
        rel_types = self.index_rel_type.get(rel_name)
        if rel_types is None:
            return []
        return sorted(list(set(rel_types) - set(["Equivalence"])))

    def element_type_from_value(self, field):
        """
        If there is a match to a field identity in only one element type,
        return that element type.
        """
        results = []
        for element_type, identities in self.index.items():
            field_identity = LaneMARCRecord.get_identity_from_field(field, element_type)
            if field_identity in identities.keys():
                results.append(element_type)
        return results[0] if len(results) == 1 else None

    def simple_element_type_from_value(self, text):
        """
        If there is a match to a (simplified) identity in only one element type,
        return that element type.
        """
        primary_subfs = set([subfs[0] for subfs in LaneMARCRecord.IDENTITY_SUBFIELD_MAP.values()])
        bespoke_fields = [Field('   ','  ',[subf, text]) for subf in primary_subfs]
        results = list(filter(None, [self.element_type_from_value(bespoke_field) for bespoke_field in bespoke_fields]))
        return results[0] if len(results) == 1 else None

    def list_conflicts(self):
        return { element_type : [identity for identity, value in index.items() if value == self.CONFLICT] for element_type, index in self.index.items() }
