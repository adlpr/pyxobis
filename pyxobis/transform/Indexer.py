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

# @@@@@@ TEMPORARY, ONLY WORKS FROM DIR WITH THESE FILES,
#        DO SOMETHING BETTER WITH INPUT FILENAMES
BIB_INF_NAME = "bibmfhd.20180716.1009"
AUT_INF_NAME = "aut.20180730.0924"

# constants for lookups unable to be resolved,
# either due to conflict or having no match
CONFLICT   = "conflict"
UNVERIFIED = "unverified"

class Indexer:
    def __init__(self, inf_names=(BIB_INF_NAME, AUT_INF_NAME)):
        # Store index as json
        global INDEX
        self.index = INDEX
        if INDEX is None:
            # pull index from given file, or generate it
            import json
            try:
                with open("index.json",'r') as inf:
                    # self.index = {tuple(map(tuple, v)):k for k,v in json.load(inf).items()}
                    self.index = json.load(inf)
            except:
                self.__generate_index(inf_names)
                with open("index.json",'w') as outf:
                    # json.dump({v:k for k,v in self.index.items()}, outf)
                    json.dump(self.index, outf)
            INDEX = self.index

    def __generate_index(self, inf_names):
        # Generate index from given input MARC files.
        print("generating index in {}...".format(os.getcwd()))
        index = {}
        conflicts = set()
        for inf_name in inf_names:
            with open(inf_name,'rb') as inf:
                reader = MARCReader(inf)
                for record in tqdm(reader):
                    record.__class__ = LaneMARCRecord  # adds extra methods
                    ctrlno, element_type, id_string = record.get_identity()
                    if element_type and id_string:
                        if element_type not in index:
                            index[element_type] = {}
                        if id_string in index[element_type]:
                            # Multiple records with same identity tuple.
                            conflicts.add((element_type, id_string))
                        else:
                            index[element_type][id_string] = ctrlno
        # Mark conflicts
        for element_type, conflict in conflicts:
            # print("CONFLICTED IDENTITY:", str(conflict))
            index[element_type][conflict] = CONFLICT
        self.index = index

    def lookup(self, field, element_type):
        """
        Given a pymarc field interpreted as a particular XOBIS element type,
        look up its associated control number.
        Identities with multiple ctrl nos will return CONFLICT;
        with none, will return UNVERIFIED
        """
        assert element_type in self.index, "element type {} not indexed".format(element_type)
        identity = LaneMARCRecord.get_field_identity(field, element_type)
        value = self.index[element_type].get(identity)
        return value if value is not None else UNVERIFIED

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
            return UNVERIFIED
        assert element_type in self.index, "element type {} not indexed".format(element_type)
        subf = LaneMARCRecord.IDENTITY_SUBFIELD_MAP[element_type][0]
        return self.lookup(Field('   ','  ',[subf, text]), element_type)

    def element_type_from_value(self, field):
        """
        If there is a match to a field identity in only one element type,
        return that element type.
        """
        results = []
        for element_type, identities in self.index.items():
            field_identity = LaneMARCRecord.get_field_identity(field, element_type)
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
        return { element_type : [identity for identity, value in index.items() if value == CONFLICT] for element_type, index in self.index.items() }
