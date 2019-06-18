#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Enables lookup between record IDs and identities.
"""

import json
from pathlib import Path

from tqdm import tqdm

from pymarc import MARCReader, Field

from lmldb import LaneMARCRecord, LMLDB
from lmldb.xobis_constants import *


class Indexer:
    # index file paths
    INDEX_DIR = Path("../lib/lmldb")
    INDEX_FILE = INDEX_DIR / "index.json"
    INDEX_REVERSE_FILE = INDEX_DIR / "index_reverse.json"
    INDEX_REL_TYPE_FILE = INDEX_DIR / "index_rel_type.json"

    # constants for lookups unable to be resolved,
    # either due to conflict or having no match
    CONFLICT   = "conflict"
    UNVERIFIED = "unverified"

    @classmethod
    def lookup(cls, field, element_type):
        """
        Given a pymarc field interpreted as a particular XOBIS element type,
        look up its associated control number.
        Identities with multiple ctrl nos will return CONFLICT;
        with none, will return UNVERIFIED
        """
        assert element_type in cls.index, f"element type {element_type} not indexed"
        identity = LaneMARCRecord.get_identity_from_field(field, element_type)
        value = cls.index[element_type].get(identity)
        return cls.UNVERIFIED if value is None else value


    @classmethod
    def simple_lookup(cls, text, element_type=None):
        """
        Given just a single string of text, assume it is the value of the
        primary subfield of an identity, and look up its associated control number.

        Useful for Builders to look up Types for set control.
        (could Type control numbers maybe live in some separate cache?)

        If element type is unspecified, only returns a matching value if there is
        an unambigous match to one element type.
        """
        element_type = element_type or cls.simple_element_type_from_value(text)
        if element_type is None:
            return cls.UNVERIFIED
        assert element_type in cls.index, f"element type {element_type} not indexed"
        subf = LaneMARCRecord.IDENTITY_SUBFIELD_MAP[element_type][0]
        return cls.lookup(Field('   ','  ',[subf, text]), element_type)


    @classmethod
    def reverse_lookup(cls, ctrlno):
        """
        Given a control number, return identity subfield list of the main entry
        of the associated record,
        or None if not found.
        """
        if not ctrlno.startswith('('):
            ctrlno = "(CStL)" + ctrlno
        main_entry = cls.index_reverse.get(ctrlno)
        if main_entry is None:
            return None
        return main_entry.split(LaneMARCRecord.UNNORMALIZED_SEP)


    @classmethod
    def lookup_rel_types(cls, rel_name):
        """
        Given a relationship name string, return a list of its relationship types.
        For use with the RelationshipBuilder set_type method.
        """
        rel_types = cls.index_rel_type.get(rel_name)
        if rel_types is None:
            return []
        # get rid of Equivalence (only used for Variant Types, not Relationships)
        return sorted(list(set(rel_types) - set(["Equivalence"])))


    @classmethod
    def element_type_from_value(cls, field):
        """
        If there is a match to a field identity in only one element type,
        return that element type.
        """
        results = []
        for element_type, identities in cls.index.items():
            field_identity = LaneMARCRecord.get_identity_from_field(field, element_type)
            if field_identity in identities.keys():
                results.append(element_type)
        return results[0] if len(results) == 1 else None


    @classmethod
    def simple_element_type_from_value(cls, text):
        """
        If there is a match to a primary-field-string (simplified) identity
        in only one element type,
        return that element type.
        """
        primary_subfs = set([subfs[0] for subfs in LaneMARCRecord.IDENTITY_SUBFIELD_MAP.values()])
        bespoke_fields = [Field('   ','  ',[subf, text]) for subf in primary_subfs]
        results = list(filter(None, [cls.element_type_from_value(bespoke_field) for bespoke_field in bespoke_fields]))
        return results[0] if len(results) == 1 else None


    @classmethod
    def list_conflicts(cls):
        """
        Returns a dict by element type listing identities with conflicts in the main index.
        """
        return { element_type : [identity for identity, value in index.items() if value == cls.CONFLICT] for element_type, index in cls.index.items() }


    index, index_reverse, index_rel_type = None, None, None

    @classmethod
    def init_index(cls):
        # Store index as json (for now, maybe change to pickle later?)
        if not all((cls.index, cls.index_reverse, cls.index_rel_type)):
            # read index from file, or generate it
            try:
                with cls.INDEX_FILE.open('r') as inf:
                    cls.index = json.load(inf)
                with cls.INDEX_REVERSE_FILE.open('r') as inf:
                    cls.index_reverse = json.load(inf)
                with cls.INDEX_REL_TYPE_FILE.open('r') as inf:
                    cls.index_rel_type = json.load(inf)
            except:
                cls.__generate_index()
                with cls.INDEX_FILE.open('w') as outf:
                    json.dump(cls.index, outf)
                with cls.INDEX_REVERSE_FILE.open('w') as outf:
                    json.dump(cls.index_reverse, outf)
                with cls.INDEX_REL_TYPE_FILE.open('w') as outf:
                    json.dump(cls.index_rel_type, outf)

    @classmethod
    def __generate_index(cls):
        # Generate index from given input MARC files.
        print("generating indices")

        # forward index (main or variant identity string --> ctrl number/conflict)
        index, index_variants = {}, {}
        conflicts, conflicts_variants = set(), set()
        # reverse index (ctrl number --> authorized form string)
        index_reverse = { cls.UNVERIFIED: None, cls.CONFLICT: None }
        # relationship type index (relationship name --> list of types)
        index_rel_type = {}
        all_rel_types = set(("Subordinate", "Superordinate", "Preordinate",
            "Postordinate", "Associative", "Dissociative", "Equivalence"))

        with LMLDB() as db:
            for record_type, db_query in (('bib',db.get_bibs),('auth',db.get_auts)):
                print(f"  reading {record_type}s...")
                for _, record in tqdm(db_query()):
                    # if relationship, add to rel type index
                    if record.get_broad_category() == 'Relationships':
                        rel_types = sorted(list(all_rel_types & set(record.get_all_categories())))
                        rel_name = record['155']['a'].rstrip(': ')
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
                        # for Organization and Event subdivisions, add variant fields with concatenated divisions as a single ^a
                        if element_type in (ORGANIZATION, EVENT):
                            for field in record.get_fields('110','410'):
                                if 'b' in field:
                                    record.add_field(Field('410','2 ',('a',' '.join(field.get_subfields('a','b')))))
                            for field in record.get_fields('111','411'):
                                if 'e' in field:
                                    record.add_field(Field('411','2 ',('a',' '.join(field.get_subfields('a','e')))))
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
            index[element_type][conflict] = cls.CONFLICT
        # Conflicts within variant identities
        for element_type, conflict in conflicts_variants:
            index_variants[element_type][conflict] = cls.CONFLICT
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

        cls.index, cls.index_reverse = index, index_reverse
        cls.index_rel_type = index_rel_type
