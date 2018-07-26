#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pyxobis.builders import *
from .LaneMARCRecord import LaneMARCRecord
from .Indexer import Indexer
from .DateTimeParser import DateTimeParser
from .NameParser import NameParser
from .tf_variants import *
from .tf_common import *
from .tf_notes import *
from .tf_relationships import *


class Transformer:
    def __init__(self):
        self.ix = Indexer()
        self.dp = DateTimeParser()
        self.np = NameParser()
        self.lane_org_ref = self.__build_simple_org_ref("Lane Medical Library")
        self.lc_org_ref   = self.__build_simple_org_ref("Library of Congress")
        self.nlm_org_ref  = self.__build_simple_org_ref("National Library of Medicine (U.S.)")

    def transform(self, record):
        record.__class__ = LaneMARCRecord

        # Ignore record if suppressed.
        if 'Suppressed' in record.get_subsets():
            return None

        rb = RecordBuilder()

        # -------------
        # CONTROLDATA
        # -------------

        # -------
        # LANGUAGE OF RECORD
        # -------

        # Technically this should come from the 040 ^b I guess? But let's just assume eng
        rb.set_lang('eng')

        # -------
        # ID
        # -------

        # Record organization is Lane
        rb.set_id_org_ref(self.lane_org_ref)

        # Record control number (001 plus prefix letter; generated by RIM in 035 ^9)
        record_control_no = record.get_control_number()
        # @@@@@ TEMPORARY @@@@@@
        if record_control_no is None:
            return None
        rb.set_id_value(record_control_no)

        # Additional identifiers
        # 010 = LCCN
        # (how to treat ^z???)
        for val in record.get_subfields('010','a'):
            rb.add_id_alternate(self.lc_org_ref, val.strip())
        # 015   National Bibliography Number (NR)
        ...
        ...
        ...
        # 035 8# = NLM control number
        for field in record.get_fields('035'):
            if field.indicator1 == '8':
                for val in field.get_subfields('a'):
                    rb.add_id_alternate(self.nlm_org_ref, val.strip())

        # what to do with all these?? notes???:
            # 017   Copyright Registration Number (R)
            # 020   International Standard Book Number (R)
            # 022   International Standard Serial Number (R)
            # 024   Other Standard Identifier (incl ISBN 13) (R)
            # 027   Standard Technical Report Number (R)
            # 028   [NON-LANE] Publisher or Distributor Number (R)
            # 030   CODEN Designation (R)
            # 032   Postal Registration Number (R)
            # 034   [NON-LANE] Coded Cartographic Mathematical Data (R)
            # 040   Cataloging Source (NR)
            # 041   Language Code (NR)
            # 042   Authentication Code (NR)
            # 043   Geographic Area Code (NR)
            # 044   [NON-LANE] ??????????
            # 045   Time Period of Content (NR)
            # 046   [NON-LANE] Special Coded Dates (R)
            # 050   Library of Congress Call Number (R)
            # 055   [NON-LANE] Classification Numbers Assigned in Canada (R)
            # 060   National Library of Medicine Call Number (R)
            # 066   [NON-LANE] Character Sets Present (NR)
            # 072   Subject Category Code (Lane: MeSH tree no.) (R)
            # 074   GPO Item Number (R)
            # 075   Qualifiers Allowed with Descriptor (Lane: cf. new 925) (R)
            # 086   Government Document Classification Number (R)
            # 088   Report Number (R)
            # 090   [NON-LANE] [local call number]
            # 092   [NON-LANE] [local call number]
        ...
        ...
        ...
        ...
        ...
        ...

        # -------
        # TYPES
        # -------
        # = Subsets = 655 77 fields.
        # NB: "Record Type" (Z47381) actually refers to which PE a record is
        for field in record.get_fields('655'):
            if field.indicator1 == '7':
                title = field['a']
                href  = field['0'] or self.ix.quick_lookup(title, CONCEPT)
                set_ref = self.ix.quick_lookup("Subset", CONCEPT)
                rb.add_type(title, href, set_ref)

        # -------
        # ACTIONS
        # -------
        # Administrative metadata (get these from? 007.. oracle???)
        # Action Types
        # created; modified..
        ...
        ...
        ...
        ...
        ...
        ...

        # -------------
        # PRINCIPAL ELEMENT
        # -------------
        # Determine which function to delegate PE building based on record type

        element_type = record.get_xobis_element_type()
        # @@@@@ TEMPORARY @@@@@
        if not element_type:
            # don't transform
            return None
        assert element_type, "could not determine type of record {}".format(record['001'].data)

        if element_type not in [TIME, RELATIONSHIP, HOLDINGS]:

            init_builder, parse_name = {
                WORK_INST    : (self.init_work_instance_builder, None),
                WORK_AUT     : (self.init_work_authority_builder, None),
                BEING        : (self.init_being_builder, self.np.parse_being_name),
                CONCEPT      : (self.init_concept_builder, self.np.parse_concept_name),
                EVENT        : (self.init_event_builder, None),
                LANGUAGE     : (self.init_language_builder, None),
                OBJECT       : (self.init_object_builder, None),
                ORGANIZATION : (self.init_organization_builder, None),
                PLACE        : (self.init_place_builder, None),
                STRING       : (self.init_string_builder, self.np.parse_string_name),
            }.get(element_type)

            # @@@@@@@@@@@@@ TEMPORARY @@@@@@@@@@@@@
            if element_type in [BEING, STRING]:

                # Initialize, perform PE-specific work on, and return Builder object.
                peb = init_builder(record)

                # ENTRY NAME(S) AND QUALIFIERS
                # -------
                entry_names, entry_qualifiers = parse_name(record.get_id_field())
                for entry_name in entry_names:
                    peb.add_name(**entry_name)
                for entry_qualifier in entry_qualifiers:
                    peb.add_qualifier(entry_qualifier)

                # VARIANTS
                # -------
                # 400 / 410 / 411 / 430 / 450 / 451 / 455 / 482
                for variant in self.transform_variants(record):
                    peb.add_variant(variant)

                # NOTES
                # -------
                for note in self.transform_notes(record):
                    peb.add_note(note)

                rb.set_principal_element(peb.build())

                # -------------
                # RELATIONSHIPS
                # -------------
                relationships = self.transform_relationships_bib(record)  \
                                    if element_type in (WORK_INST, OBJECT)  \
                                    else self.transform_relationships_aut(record)
                for relationship in relationships:
                    rb.add_relationship(relationship)

                return rb.build()

        return None

    def init_being_builder(self, record):
        bb = BeingBuilder()

        # ROLE
        # ---
        # authority / instance / authority instance

        # all authorities (?)
        bb.set_role("authority")


        # TYPE
        # ---
        # human / nonhuman / special

        categories = record.get_all_categories()
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

        broad_category = record.get_broad_category()
        being_class = None
        if 'Persons, Undifferentiated' in record.get_subsets():
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
        ...
        ...
        ...

        # ENTRY TYPE
        # ---
        # Generic "entry type" is specific to Beings: birth name, pseudonym, etc.
        entry_type_kwargs, entry_type_time_or_duration_ref = self.get_type_and_time_from_relator(record['100'])
        if entry_type_kwargs:
            bb.set_entry_type(**entry_type_kwargs)
            bb.set_time_or_duration_ref(entry_type_time_or_duration_ref)

        return bb


    def init_concept_builder(self, record):
        cb = ConceptBuilder()

        # TYPE
        # ---
        # abstract, collective, control, specific
        # abstract = Artificial Intelligence; Cataloging;
        #            Statistical Hypothesis Testing; Surgery, Plastic
        # collective = Buildings; Databases; Gorilla gorilla; Kidney;
        #              Plastic Surgeons; Silver Nitrate
        # control =
        # specific = Pending Records; Suppressed Records;
        #           Subject Heading Schemes

        # categories = record.get_all_categories()
        ...
        ...
        ...
        # cb.set_type(concept_type)


        # USAGE
        # ---
        # subdivision or not
        ...
        ...
        ...
        cb.set_usage(concept_usage)


        # SUBTYPE
        # ---
        # = subdivision type
        # general, form, topical, unspecified
        ...
        # broad category: Qualifiers, Topical
        ...
        ...
        cb.set_type(concept_type)

        # SCHEME
        # ---
        # 008:11 ?
        ...
        ...
        ...
        # cb.set_scheme(concept_scheme)

        return cb


    def init_work_instance_builder(self, record):
        return None

    def init_object_builder(self, record):
        return None

    def init_organization_builder(self, record):
        return None

    def init_event_builder(self, record):
        return None

    def init_work_authority_builder(self, record):
        return None


    def init_language_builder(self, record):
        return None

    # def transform_time(self, record):
    #     return None

    def init_place_builder(self, record):
        return None


    def init_string_builder(self, record):
        sb = StringBuilder()

        # broad_category = record.get_broad_category()
        # categories = record.get_all_categories()
        # subsets = record.get_subsets()

        # TYPE
        # ---
        # textual / numeric / mixed
        # why is this important?
        # string_type = None
        # sb.set_type(string_type)


        # CLASS
        # ---
        # word / phrase
        if record['182'].indicator2 == '2':
            string_class = "phrase"
        else:
            string_class = "word"
        sb.set_class(string_class)

        return sb

    # def transform_relationship(self, record):
    #     return None

    # def transform_holdings(self, record):
    #     return None


    # bring imported methods into class scope
    # (temporary solution for the sake of organization)

    transform_variants = transform_variants
    transform_variant_being = transform_variant_being
    transform_variant_organization = transform_variant_organization
    transform_variant_concept = transform_variant_concept
    transform_variant_string = transform_variant_string

    transform_notes = transform_notes

    transform_relationships_aut = transform_relationships_aut
    transform_relationships_bib = transform_relationships_bib

    def __build_simple_org_ref(self, name):
        orb = OrganizationRefBuilder()
        orb.set_link(name, self.ix.quick_lookup(name, ORGANIZATION))
        orb.add_name(name, 'eng')
        return orb.build()

    def get_type_and_time_from_relator(self, field):
        """
        For 1XX and 4XX fields, the ^e "relator" and its time/duration qualifiers ^8 and ^9
        aren't describing an actual relationship, but rather a "type" of main or variant entry.

        Returns a Type kwarg dict and a Time/Duration Ref object, for use in a Builder.
        """
        type_kwargs, type_time_or_duration_ref = {}, None

        # Type "relator"
        entry_type = field['e']
        if entry_type:
            entry_type = entry_type.rstrip(':').strip()
            type_kwargs = { 'link_title' : entry_type,
                             'set_URI'   : self.ix.quick_lookup("Variant Type", CONCEPT),
                             'href_URI'  : self.ix.quick_lookup(entry_type, CONCEPT) }

        # Time or Duration
        start_type_datetime, end_type_datetime = field['8'], field['9']
        type_datetime = start_type_datetime + end_type_datetime  \
                        if start_type_datetime and end_type_datetime  \
                        else end_type_datetime or start_type_datetime
        if type_datetime:
            type_time_or_duration_ref = self.dp.parse(type_datetime, None)

        return type_kwargs, type_time_or_duration_ref
