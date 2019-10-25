#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os, json
import regex as re

from loguru import logger

from pymarc import Field

from pylmldb import LaneMARCRecord
from pylmldb.xobis_constants import *

from ..builders import *

from . import tf_common_methods as tfcm

from .Indexer import Indexer
from .DateTimeParser import DateTimeParser
from .NameParser import NameParser
from .FieldTransposer import FieldTransposer

from .VariantTransformer import VariantTransformer
from .RelationshipTransformer import RelationshipTransformer
from .NoteTransformer import NoteTransformer


class RecordTransformer:
    """
    Methods for transforming all bibliographic/authority/holdings records
    at the highest level.
    """
    def __init__(self):
        self.init_builder_methods = {
            WORK_INST    : self.init_work_instance_builder,
            WORK_AUT     : self.init_work_authority_builder,
            BEING        : self.init_being_builder,
            CONCEPT      : self.init_concept_builder,
            RELATIONSHIP : self.init_concept_builder,
            EVENT        : self.init_event_builder,
            LANGUAGE     : self.init_language_builder,
            OBJECT       : self.init_object_builder,
            ORGANIZATION : self.init_organization_builder,
            PLACE        : self.init_place_builder,
            STRING       : self.init_string_builder,
            TIME         : self.init_time_builder,
            HOLDINGS     : self.init_holdings_builder
        }

        self.lane_org_ref = tfcm.build_simple_ref("Lane Medical Library", ORGANIZATION)
        self.lc_org_ref   = tfcm.build_simple_ref("Library of Congress", ORGANIZATION)
        self.nlm_org_ref  = tfcm.build_simple_ref("National Library of Medicine (U.S.)", ORGANIZATION)
        self.oclc_org_ref = tfcm.build_simple_ref("OCLC", ORGANIZATION)

        self.subset_set_href = Indexer.simple_lookup("Subset", CONCEPT)
        self.action_type_set_href = Indexer.simple_lookup("Action Type", CONCEPT)

        self.ft = FieldTransposer()

        # subordinate Transformers
        self.vt  = VariantTransformer()
        self.rlt = RelationshipTransformer()
        self.nt  = NoteTransformer()


    def transform(self, record):
        """
        Transform a pymarc Record object into a pyxobis Record object.

        Returns None if unable to transform.
        """
        record.__class__ = LaneMARCRecord

        # Ignore record if suppressed
        if record.is_suppressed():
            return None

        # @@@@@ TEMPORARY: IGNORE IMMI RECORDS @@@@@
        if '040' in record and record['040']['a'] == "IMMI":
            return None

        element_type = record.get_xobis_element_type()
        if element_type is None:
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@
            # at this point these should all be 155 category dummy records
            #   we want to skip, but maybe make this into a warning
            #   just to make sure?
            return None
        elif element_type == HOLDINGS and record.get_holdings_type() is None:
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@
            # skip component records (may erroneously skip others if
            #   new/invalid loc codes added, so revisit this at some point)
            return None

        rb = RecordBuilder()

        # --------------------------
        # CONTROLDATA
        # --------------------------

        # -------
        # LANGUAGE OF RECORD
        # -------
        # Normally this might come from the 040 ^b? But all ours are English
        rb.set_lang('English')

        # -------
        # IDs
        # -------
        # ID ORG
        # ---
        # is us, Lane
        rb.add_id_description(self.lane_org_ref)

        # ID VALUE
        # ---
        # institutional prefix + record type prefix + field 001 data
        record_control_no = record.get_control_number()
        # @@@@@ TEMPORARY @@@@@@
        if record_control_no is None:
            return None
        rb.set_id_value(record_control_no)

        # ID STATUS
        # ---
        rb.set_id_status('valid')

        # ~~~~~~
        # RECORD PREPROCESSING
        # ~~~~~~
        # bib
        if element_type in (WORK_INST, OBJECT):
            # Fix 149 ^1 if necessary.
            self.__reconstruct_bib_149_subf_1(record)
            # Convert 730 variant (translated) titles to 246, for ease of processing.
            self.__translated_title_730_to_246(record)
            # Relator on 785 #7 depends on position in record.
            self.__preprocess_bib_785(record)
            # Juggle 880s based on linked field.
            self.__preprocess_bib_880(record)
            # Treat 904 as 246.
            self.__preprocess_bib_904(record)
            # Try to match up series fields.
            self.__resolve_bib_490_830_901(record)
            # 94Xs need to take into account certain fixed-field bytes.
            self.__preprocess_bib_94X(record)
        # aut
        elif element_type != HOLDINGS:
            # Entry groups/sumptions
            self.__preprocess_sumptions(record)
            # Only use 043 geocode as variant if exactly one.
            self.__preprocess_aut_043(record)
            # Split aut 68X (education/affiliation) fields,
            #   and/or convert to 610 (Organizational Relationship).
            self.__preprocess_aut_68X(record)
            # 94Xs need to take into account certain fixed-field bytes.
            self.__preprocess_aut_94X(record)
        # hdg
        else:
            # treat most 655 as subsets
            self.__preprocess_hdg_655(record)
            # reduce complexities of hdg 907 codes
            self.__preprocess_hdg_907(record)
            # Insert fields pulled from bibs by FieldTransposer
            record.add_field(*self.ft.get_transposed_fields(record_control_no))

        # ID ALTERNATES
        # ---
        self.transform_id_alternates(record, rb)

        # -------
        # TYPES
        # -------
        self.transform_record_types(record, rb)

        # -------
        # ACTIONS
        # -------
        self.transform_record_actions(record, rb)

        # --------------------------
        # PRINCIPAL ELEMENT
        # --------------------------
        # Determine which function to delegate PE building based on record type
        init_builder = self.init_builder_methods.get(element_type)

        # Initialize, perform PE-specific work on, and return Builder object.
        peb = init_builder(record)

        if element_type != HOLDINGS:
            # ENTRY NAME(S) AND QUALIFIERS
            # -------
            parse_name = NameParser.get_parser_for_element_type(element_type)
            entry_names_and_qualifiers = parse_name(record.get_id_field())
            for entry_name_or_qualifier in entry_names_and_qualifiers:
                if isinstance(entry_name_or_qualifier, dict):
                    peb.add_name(**entry_name_or_qualifier)
                else:
                    peb.add_qualifier(entry_name_or_qualifier)

            # VARIANTS
            # -------
            for variant in self.vt.transform_variants(record):
                peb.add_variant(variant)

        # NOTES
        # -------
        for note in self.nt.transform_notes(record):
            peb.add_note(**note)

        rb.set_principal_element(peb.build())

        # RELATIONSHIPS
        # -------
        for relationship in self.rlt.transform_relationships(record):
            rb.add_relationship(relationship)

        return rb.build()

    def transform_record_types(self, record, rb):
        """
        For each field describing a Record Type (Subset) in record,
        add to RecordBuilder rb.
        """

        # Record "Types" = Subsets = 655 77
        # NB: Established aut "Record Type" (Z47381) actually refers
        #     to which PE a record is
        for field in record.get_fields('655'):
            assert 'a' in field, f"{record.get_control_number()}: 655 with no $a: {field}"
            if field.indicator1 == '7':
                for val in field.get_subfields('a'):
                    rb.add_type(title = val,
                                href  = "(CStL)" + field['0'] if '0' in field else Indexer.simple_lookup(val, CONCEPT),
                                set_ref = self.subset_set_href)

        # 903 NEW(E) to Subset
        for field in record.get_fields('903'):
            assert 'a' in field, f"{record.get_control_number()}: 903 with no $a: {field}"
            for val in field.get_subfields('a'):
                val = val.upper()
                assert val.startswith('NEW'), f"{record.get_control_number()}: invalid value for 903 $a: {field}"
                if val.startswith('NEWE'):
                    title = f"Subset, New Digital {val[4:].strip()}"
                else:
                    title = f"Subset, New Resource {val[3:].strip()}"
                rb.add_type(title = title,
                            href  = Indexer.simple_lookup(title, CONCEPT),
                            set_ref = self.subset_set_href)

        # 906 ^a/^d (+ sometimes ^c) to Subsets
        for field in record.get_fields('906'):
            for val in field.get_subfields('a'):
                # exception for ASV since common in ^a when it should be ^d
                if val == 'ASV':
                    val = "Alpha Parent Visual"
                title = f"Subset, Component, {val}"
                rb.add_type(title = title,
                            href  = Indexer.simple_lookup(title, CONCEPT),
                            set_ref = self.subset_set_href)
            for val in field.get_subfields('c'):
                if val in ('LIB','REF'):
                    title = f"Subset, Component, {val}"
                    rb.add_type(title = title,
                                href  = Indexer.simple_lookup(title, CONCEPT),
                                set_ref = self.subset_set_href)
            for val in field.get_subfields('d'):
                title = {'AB'     : "Subset, Component, Alpha+Monograph Parents",
                         'AS'     : "Subset, Component, Alpha Parent",
                         'AS BDM' : "Subset, Component, Alpha Parent Batch",
                         'ASV'    : "Subset, Component, Alpha Parent Visual",
                         'CB'     : "Subset, Component, Classed Parents",
                         'CM'     : "Subset, Component, Classed Monograph Parent",
                         'CMV'    : "Subset, Component, Classed Parent Visual",
                         'CS'     : "Subset, Component, Classed Serial Parent",
                         'CU'     : "Subset, Component, Classed Unknown Parent",
                         'pubmed2marc' : "Subset, Component, pubmed2marc" }.get(val)
                assert title is not None, f"{record.get_control_number()}: invalid 906 $d: {field}"
                rb.add_type(title = title,
                            href  = Indexer.simple_lookup(title, CONCEPT),
                            set_ref = self.subset_set_href)

        # hdg 907 to Subsets
        if record.get_xobis_element_type() == LaneMARCRecord.HDG:
            for field in record.get_fields('907'):
                # a  Serial type (INC EXC 2ND N/A) (NR)
                for val in field.get_subfields('a'):
                    if val == '???':
                        continue
                    val = val.strip(" ;:.,'/").upper()
                    title = {'INC' : "Subset, Serial, Chiefly Articles",
                             'EXC' : "Subset, Serial, Chiefly Nonarticles",
                             'INR' : "Subset, Serial, Reference"}.get(val, "Subset, Serial, Pending")
                    rb.add_type(title = title,
                                href  = Indexer.simple_lookup(title, CONCEPT),
                                set_ref = self.subset_set_href)
                # b  Analysis treatment (AA CA DA PA NA) (NR)
                for val in field.get_subfields('b'):
                    # values should be cleaned up already from preprocessing
                    title = {'AA': "Subset, Analysis, Full",
                             'CA': "Subset, Analysis, Consider",
                             'DA': "Subset, Analysis, Do Not",
                             'PA': "Subset, Analysis, Partial",
                             'NA': "Subset, Analysis, Not Applicable"}.get(val)
                    assert title is not None, \
                        f"{record.get_control_number()}: problem parsing 907 $b: {field}"
                    rb.add_type(title = title,
                                href  = Indexer.simple_lookup(title, CONCEPT),
                                set_ref = self.subset_set_href)
                # c  Classification/shelving pattern (PER EPER SCN VCN MST N/A) (NR)
                for val in field.get_subfields('c'):
                    val = val.strip(" ;:.,'/").upper()
                    title = {'SCN': "Subset, Classed Together",
                             'VCN': "Subset, Classed Separately"}.get(val)
                    if title is not None:
                        rb.add_type(title = title,
                                    href  = Indexer.simple_lookup(title, CONCEPT),
                                    set_ref = self.subset_set_href)


    def transform_record_actions(self, record, rb):
        """
        For each field describing an Action in record,
        add to RecordBuilder rb.

        3 established types that aren't being fully mapped here:
            Batch imported:  (except for hdg 989)
            Batch revised:
            Lane imported:
        need information available only in Voyager's Oracle tables.
        """
        actions = []

        # 005  Date and Time of Latest Transaction (NR)
        #   --> Lane [OR Batch] revised
        modified_timestamp = record['005'].data
        if modified_timestamp.strip():
            # Format as ISO 8601 string and convert to TimeRef
            modified_time_fstr = f"{modified_timestamp[:4]}-{modified_timestamp[4:6]}-{modified_timestamp[6:8]}T{modified_timestamp[8:10]}:{modified_timestamp[10:12]}:{modified_timestamp[12:14]}"
            modified_time_ref = DateTimeParser.parse_as_ref(modified_time_fstr)
            actions.append(("Lane revised", modified_time_ref))

        # 008	Fixed-Length Data Elements (NR)  (first 6 bytes)
        #   --> LC OR NLM OR Lane OR Record created  [OR Batch imported]
        #       [for bibs; what about auts?]
        created_timestamp = record['008'].data[:6]
        if created_timestamp.strip():
            # Format as ISO 8601 string and convert to TimeRef
            year_start = "20" if created_timestamp[:2] < "60" else "19"
            created_time_fstr = f"{year_start}{created_timestamp[:2]}-{created_timestamp[2:4]}-{created_timestamp[4:]}"
            created_time_ref = DateTimeParser.parse_as_ref(created_time_fstr)
            # Determine creator from bib 040
            record_creator = 'Record'
            cataloging_source_field = record['040']
            if cataloging_source_field is not None:
                agency_code = cataloging_source_field['c'] or cataloging_source_field['a']
                if agency_code is not None:
                    agency_code = agency_code.lower()
                    if 'cstl' in agency_code.replace('cst-law','').replace('-',''):
                        record_creator = "Lane"
                    elif 'dnlm' in agency_code:
                        record_creator = "NLM"
                    elif 'dlc' in agency_code:
                        record_creator = "LC"
            actions.append((f"{record_creator} created", created_time_ref))

        # 915  ControlData - Temporal (Lane) (R)
        #   --> NLM types (use what's in $e)
        for field in record.get_fields('915'):
            subf_as, subf_es = field.get_subfields('a'), field.get_subfields('e')
            if len(subf_as) != 1 or len(subf_es) != 1:
                logger.warning(f"{record.get_control_number()}: invalid 915: {field}")
                continue
            timestamp, action_type = subf_as[0], subf_es[0]
            time_ref = DateTimeParser.parse_as_ref(timestamp)
            actions.append((action_type.rstrip(': '), time_ref))

        # hdg 989  Date/Time of Automated Processing (Lane) (NR)
        #   --> Batch imported
        for field in record.get_fields('989'):
            imported_timestamp = field['a']
            # Format as ISO 8601 string and convert to TimeRef
            imported_time_fstr = f"{imported_timestamp[:4]}-{imported_timestamp[4:6]}-{imported_timestamp[6:8]}T{imported_timestamp[8:10]}:{imported_timestamp[10:12]}:{imported_timestamp[12:14]}"
            imported_time_ref = DateTimeParser.parse_as_ref(imported_time_fstr)
            actions.append(("Batch imported", imported_time_ref))

        for action_type, action_time_or_duration_ref in actions:
            rb.add_action(action_time_or_duration_ref,
                          title = action_type,
                          href  = Indexer.simple_lookup(action_type, RELATIONSHIP),
                          set_ref = self.action_type_set_href)


    def init_being_builder(self, record):
        bb = BeingBuilder()

        # ROLE
        # ---
        # authority / instance / authority instance
        bb.set_role("authority")  # ?

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
        # referential: things like Mc/Mac, St.: 008/09 = b/c/e and/or 655 77 ^a Unestablished

        broad_category = record.get_broad_category()
        being_class = None
        if 'Persons, Undifferentiated' in record.get_subsets():
            being_class = 'undifferentiated'
        elif record.is_referential():
            being_class = 'referential'
        elif broad_category == 'Peoples':
            if record['100'].indicator1 != '9':
                logger.warning(f"{self.get_control_number()}: Peoples without I1=9")
            else:
                being_class = 'collective'
        elif broad_category == 'Persons, Families or Groups':
            if record['100'].indicator1 != '3':
                logger.warning(f"{self.get_control_number()}: Family/Group without I1=3")
            being_class = 'familial'
        else:
            if record['100'].indicator1 not in '01':
                logger.warning(f"{self.get_control_number()}: Individual without I1=[01]")
            being_class = 'individual'

        bb.set_class(being_class)

        # SCHEME
        # ---
        # is it LC for the 100 when 010? not really, consider this n/a for now

        # ENTRY GROUP
        # ---
        bb.set_entry_group_attributes(id = None,
                                      group = record['100']['6'],
                                      preferred = None )

        # ENTRY TYPE
        # ---
        # Generic entry type is routine for Variants, but specific to Beings
        # on the main entry (birth name, pseudonym, etc.)
        entry_type_kwargs, entry_type_time_or_duration_ref = tfcm.get_type_and_time_from_relator(record['100'])
        if entry_type_kwargs:
            bb.set_entry_type(**entry_type_kwargs)
            bb.set_time_or_duration_ref(entry_type_time_or_duration_ref)

        return bb


    def init_concept_builder(self, record):
        cb = ConceptBuilder()

        # TYPE
        # ---
        # abstract, collective, control, specific
        # abstract/specific/collective too hard to differentiate
        if record.get_broad_category() in ["Category", "Record Type", "Subset"]:
            cb.set_type("control")

        # USAGE
        # ---
        # subdivision or not?
        if record.get_broad_category() == "Qualifiers, Topical":
            cb.set_usage("subdivision")

            # SUBTYPE
            # ---
            # general, form, topical, unspecified
            cb.set_subtype("topical")
            # other types aren't really in our MARC, I guess

        # SCHEME
        # ---
        # 655 87 MeSH / 77 LaSH or LCSH
        subsets = record.get_subsets()
        for scheme in ("MeSH", "LCSH", "LaSH"):
            if scheme in subsets:
                cb.set_scheme(scheme)
                break

        # ENTRY GROUP
        # ---
        entry_field = record.get_id_field()
        if entry_field.tag != '155':
            cb.set_entry_group_attributes(id    = entry_field['4'],
                                          group = entry_field['3'],
                                          preferred = None )

        return cb


    # Defined in order of increasing priority
    event_type_map = {
        'miscellaneous' :
            ["Censuses", "Exhibitions", "Exhibits", "Experiments",
             "Special Events", "Trials", "Workshops"],
        'meeting' : ["Congresses", "Legislative Sessions"],
        'journey' : ["Expeditions", "Medical Missions, Official"],
        # Riots are occurrences even if they contain Fires (see Z58192 Tulsa Race Riot)
        'occurrence' :
            ["Armed Conflicts", "Biohazard Release",
             "Chemical Hazard Release", "Civil Disorders", "Disasters",
             "Disease Outbreaks", "Explosions", "Mass Casualty Incidents",
             "Radioactive Hazard Release", "Riots"],
        'natural' :
            ["Cyclonic Storms", "Earthquakes", "Fires", "Floods", "Tsunamis"]
    }

    def init_event_builder(self, record):
        eb = EventBuilder()

        # TYPE
        # ---
        # natural, meeting, journey, occurrence, miscellaneous
        # get by primary category
        primary_cats = record.get_primary_categories()
        for type, type_cats in self.event_type_map.items():
            if any(cat in type_cats for cat in primary_cats):
                eb.set_type(type)
                break

        # CLASS
        # ---
        # individual, collective, referential
        if record.is_referential():
            eb.set_class('referential')
        # individual/collective too hard to differentiate, n/a for now

        # SCHEME
        # ---
        # n/a for now

        # ENTRY GROUP
        # ---
        eb.set_entry_group_attributes(id    = None,
                                      group = record['111']['6'],
                                      preferred = None )

        return eb


    def init_language_builder(self, record):
        lb = LanguageBuilder()

        # TYPE
        # ---
        # natural, constructed, script
        broad_cat = record.get_broad_category()
        if broad_cat == "Scripts":
            lb.set_type('script')
        # natural/constructed not yet differentiable

        # CLASS
        # ---
        # individual, collective, referential
        if record.is_referential():
            lb.set_class('referential')
        # language families not marked

        # USAGE
        # ---
        # subdivision or not?
        # n/a for now

        # ENTRY GROUP
        # ---
        lb.set_entry_group_attributes(id    = record['150']['4'],
                                      group = record['150']['3'],
                                      preferred = None )

        return lb


    def init_organization_builder(self, record):
        ob = OrganizationBuilder()

        # TYPE
        # ---
        # business, government, nonprofit, other
        # get by primary category
        primary_cats = [cat.lower() for cat in record.get_primary_categories()]
        if any('nonprofit' in cat for cat in primary_cats):
            ob.set_type('nonprofit')
        elif any('for profit' in cat for cat in primary_cats):
            ob.set_type('business')
        elif any('government' in cat for cat in primary_cats):
            ob.set_type('government')

        # CLASS
        # ---
        # individual, collective, referential
        if record.is_referential():
            ob.set_class('referential')
        # individual/collective too hard to differentiate, n/a for now

        # SCHEME
        # ---
        # n/a for now

        # ENTRY GROUP
        # ---
        ob.set_entry_group_attributes(id    = None,
                                      group = record['110']['6'],
                                      preferred = None )

        return ob

    # Defined in order of increasing priority
    place_type_map = {
        'natural' : ["Bays", "Canals", "Caves", "Coasts", "Continents",
            "Deserts", "Forests", "Islands", "Lakes", "Minor Planets",
            "Natural Springs", "Mountains", "Oceans", "Peninsulas", "Planets",
            "Rivers", "Seas", "Stars, Celestial", "Straits", "Valleys",
            "Volcanoes"],
        'constructed' : ["Airports", "Building Complexes", "Buildings",
            "Health Resorts", "Hot Springs", "Laboratories", "Leper Colonies",
            "Military Facilities", "Monuments", "Open Space",
            "Parking Facilities", "Parks", "Roadways",
            "Collection, Shelving", "Location, Shelving"],  # <-- ?
        'jurisdictional' : ["Cities", "Cities, Extinct", "Cities, Independent",
            "Colonies", "Counties", "Countries", "County Seats",
            "Indian Reservations", "Locales", "Provinces", "Regions", "States",
            "Territories", "Villages"]
    }

    def init_place_builder(self, record):
        pb = PlaceBuilder()

        # ROLE
        # ---
        # authority / instance / authority instance
        pb.set_role("authority")  # ?

        # TYPE
        # ---
        # natural / constructed / jurisdictional
        primary_cats = record.get_primary_categories()
        for type, type_cats in self.place_type_map.items():
            if any(cat in type_cats for cat in primary_cats):
                pb.set_type(type)
                break

        # CLASS
        # ---
        # individual, collective, referential
        if record.is_referential():
            pb.set_class('referential')
        # others?

        # USAGE
        # ---
        # subdivision or not?
        # n/a for now

        # SCHEME
        # ---
        # n/a for now

        # ENTRY GROUP
        # ---
        # n/a

        return pb


    def init_string_builder(self, record):
        sb = StringBuilder()

        # categories = record.get_all_categories()
        # subsets = record.get_subsets()

        # TYPE
        # ---
        # textual / numeric / mixed
        broad_category = record.get_broad_category()
        string_type = None
        if "Numeric" in broad_category:
            string_type = "numeric"
        elif "Nominal" in broad_category:
            string_type = "textual"
        sb.set_type(string_type)

        # CLASS
        # ---
        # word / phrase
        id_field = record.get_id_field()
        if id_field.indicator2 == '2':
            string_class = "phrase"
        else:
            string_class = "word"
        sb.set_class(string_class)

        # PART(S) OF SPEECH
        # ---
        # ^g Grammatical type (R)
        field_lang, field_script = id_field['3'], id_field['4']
        for val in id_field.get_subfields('g'):
            sb.add_pos( pos_text    = val,
                        pos_lang    = field_lang,
                        title = None,  # we don't have these established yet
                        href  = None )

        # ENTRY GROUP
        # ---
        # n/a

        return sb


    def init_time_builder(self, record):
        tb = TimeBuilder()

        # CLASS
        # ---
        # individual, collective, referential
        if record.is_referential():
            tb.set_class('referential')
        # others?

        # USAGE
        # ---
        # subdivision or not? n/a for now

        # SCHEME
        # ---
        # n/a for now?

        # ENTRY GROUP
        # ---
        tb.set_entry_group_attributes(id    = record['150']['4'],
                                      group = record['150']['3'],
                                      preferred = None )

        # CALENDAR
        # ---
        entry_field = record.get_id_field()
        datestring = entry_field['a']
        calendar_kwargs, datestring = DateTimeParser.extract_calendar(datestring)
        if calendar_kwargs:
            tb.set_calendar(**calendar_kwargs)

        # ENTRY CONTENT
        # ---
        # This is necessary for Time in place of a NameParser method
        time_content_single = DateTimeParser.parse_simple(datestring)
        tb.set_time_content_single(time_content_single)

        return tb


    # Possible primary categories of "artistic" type Works
    work_cats_artistic = [
        "Animation", "Architectural Drawings", "Art Originals",
        "Art Reproductions", "Cartoons", "Drama", "Drawings",
        "Graphic Reproductions", "Graphics", "Herbal Illustrations",
        "Illustrations", "Music", "Paintings", "Phonodiscs", "Plates",
        "Portraits", "Postcards", "Posters",
        "Sculpture", "Visual Materials", "Video Games"
    ]

    work_aut_cats_collective = [
        'Databases', 'Databases, Bibliographic', 'Databases, Factual',
        'Libraries, Digital', 'Monographic Series', 'Online Systems',
        'Programming Languages', 'Series', 'Software', 'Video Games',
        'Vocabulary, Controlled', 'XML Schema'
    ]
    def init_work_authority_builder(self, record):
        wb = WorkBuilder()

        # TYPE
        # ---
        # intellectual, artistic
        primary_cats = record.get_primary_categories()
        if any(cat.rstrip(' .') in self.work_cats_artistic for cat in primary_cats):
            wb.set_type('artistic')
        else:
            wb.set_type('intellectual')

        # ROLE
        # ---
        # @@@@@@ if the aut has a 856 I2 in '01',
        #   it should instead have a role of "authority instance"
        #   to allow the generated hdg to be attached
        wb.set_role('authority')

        # CLASS
        # ---
        # individual, serial, collective, referential
        if record.is_referential():
            wb.set_class('referential')
        else:
            broad_cat = record.get_broad_category()
            if broad_cat == "Series" or any(cat.rstrip(' .') in self.work_aut_cats_collective for cat in primary_cats):
                # 130 Series should all be unnumbered series, NOT "serial"
                wb.set_class('collective')
            else:
                wb.set_class('individual')

        # ENTRY GROUP
        # ---
        # n/a

        return wb


    def init_work_instance_builder(self, record):
        # if 149 #9, add a temporary ^i to 245 to mark it as a "Descriptive title"
        if '149' in record and record['149'].indicator2 == '9':
            record['245']['i'] = "Descriptive title"

        wb = WorkBuilder()

        # TYPE
        # ---
        # intellectual, artistic
        primary_cats = record.get_primary_categories()
        if any(cat.rstrip(' .') in self.work_cats_artistic for cat in primary_cats):
            wb.set_type('artistic')
        else:
            wb.set_type('intellectual')

        # ROLE
        # ---
        wb.set_role('instance')

        # CLASS
        # ---
        # individual, serial, collective, referential
        if record.is_referential():
            wb.set_class('referential')
        else:
            broad_cat = record.get_broad_category().rstrip(' .')

            if broad_cat == "Serials":
                wb.set_class('serial')
            elif broad_cat in ("Collections", "Databases", "Websites"):
                # only bother with broad cat when it comes to bibs
                # (any exceptions that would necessitate looking at primaries?)
                wb.set_class('collective')
            else:
                wb.set_class('individual')

        # ENTRY GROUP
        # ---
        # n/a

        return wb


    def init_object_builder(self, record):
        ob = ObjectBuilder()

        # ROLE
        # ---
        ob.set_role('instance')

        # CLASS
        # ---
        # individual, collective, [referential: aut only]
        ob.set_class('individual')

        # TYPE
        # ---
        # natural, crafted, manufactured
        # too difficult to determine this for sure based on category alone.
        # n/a for now

        # ENTRY GROUP
        # ---
        # n/a

        return ob


    def init_holdings_builder(self, record):
        hb = HoldingsBuilder()

        # WORK/OBJECT REF
        # ---
        # get bib number from 004
        linked_ctrlno = record['004'].data
        # ad hoc holdings generated by FieldTransposer
        if linked_ctrlno.startswith('Z'):
            linked_full_ctrlno = f"(CStL){linked_ctrlno}"
            target_identity = Indexer.reverse_lookup(linked_full_ctrlno)
            assert target_identity is not None, \
                f"{record.get_control_number()}: could not find linked aut id: {linked_ctrlno}"
        else:
            # full ctrlno has prepended L or Q
            linked_full_ctrlno = f"(CStL)L{linked_ctrlno}"
            target_identity = Indexer.reverse_lookup(linked_full_ctrlno)
            if target_identity is None:
                linked_full_ctrlno = f"(CStL)Q{linked_ctrlno}"
                target_identity = Indexer.reverse_lookup(linked_full_ctrlno)
            assert target_identity is not None, \
                f"{record.get_control_number()}: could not find linked bib id: {linked_ctrlno}"
        work_or_object_ref = self.rlt.build_ref_from_field(Field('730','  ',target_identity+['w',linked_full_ctrlno]), WORK_INST)
        hb.set_work_or_object_ref(work_or_object_ref)

        # CONCEPT REF
        # ---
        # i.e. digital/physical
        holdings_type = record.get_holdings_type()
        assert holdings_type is not None, f"{record.get_control_number()}: invalid holdings type"
        holdings_type_concept_name = { LaneMARCRecord.PHYSICAL  : "Physical Resources",
                                       LaneMARCRecord.DIGITAL   : "Internet Resources",
                                       LaneMARCRecord.COMPONENT : "Components" }.get(holdings_type)
        concept_ref = tfcm.build_simple_ref(holdings_type_concept_name, CONCEPT)
        hb.set_concept_ref(concept_ref)

        # QUALIFIER(S)
        # ---
        # look up 844a as Work -> Org -> String
        for val in record.get_subfields('844','a'):
            # WORK_AUT
            ref = tfcm.build_simple_ref(val, WORK_AUT)
            if ref.link_attributes is not None and ref.link_attributes.href.anyURI not in (Indexer.UNVERIFIED, Indexer.CONFLICT):
                hb.add_qualifier(ref)
                # logger.debug(f"{val}\t{WORK_AUT}\t{ref.link_attributes.href.anyURI}")
                continue
            # WORK_INST
            ref = tfcm.build_simple_ref(val, WORK_INST)
            if ref.link_attributes is not None and ref.link_attributes.href.anyURI not in (Indexer.UNVERIFIED, Indexer.CONFLICT):
                hb.add_qualifier(ref)
                # logger.debug(f"{val}\t{WORK_INST}\t{ref.link_attributes.href.anyURI}")
                continue
            # ORGANIZATION
            ref = tfcm.build_simple_ref(val, ORGANIZATION)
            if ref.link_attributes is not None and ref.link_attributes.href.anyURI not in (Indexer.UNVERIFIED, Indexer.CONFLICT):
                hb.add_qualifier(ref)
                # logger.debug(f"{val}\t{ORGANIZATION}\t{ref.link_attributes.href.anyURI}")
                continue
            # STRING
            ref = tfcm.build_simple_ref(val, STRING)
            hb.add_qualifier(ref)
            # logger.debug(f"{val}\t{STRING}\t{ref.link_attributes.href.anyURI}")

        # SUMMARY
        # ---
        # from 866
        record_summary_field = record['866']
        if record_summary_field is not None:
            summary_enum, summary_chron = None, None
            if 'v' in record_summary_field:
                if len(record_summary_field.get_subfields('v')) > 1:
                    logger.warning(f"{record.get_control_number()}: >1 866v")
                summary_enum = record_summary_field['v']
            if 'y' in record_summary_field:
                if len(record_summary_field.get_subfields('y')) > 1:
                    logger.warning(f"{record.get_control_number()}: >1 866y")
                summary_chron = record_summary_field['y']
            hb.set_summary(summary_enum, summary_chron)
            for code, val in record_summary_field.get_subfields('x','z', with_codes=True):
                hb.add_summary_note(val,
                                    role = "annotation" if code == 'z' else "documentation")

        return hb


    def transform_id_alternates(self, record, rb):
        # 010  Library of Congress Control Number (NR)
        for field in record.get_fields('010'):
            for code, val in field.get_subfields('a','b','z', with_codes=True):
                rb.add_id_alternate("NUCMC" if code=='b' else self.lc_org_ref,
                                    val.strip(),
                                    'invalid' if code=='z' else 'valid')

        # 015  National Bibliography Number (NR)
        for val in record.get_subfields('015','a'):
            rb.add_id_alternate("National Bibliography Number", val.strip())

        # 017  Copyright Registration Number (R)
        for field in record.get_fields('017'):
            id_description = "Copyright Registration Number"
            if 'b' in field:
                id_description += " assigned by: " + field['b'].strip()
            rb.add_id_alternate(id_description, field['a'].strip())

        # 020  International Standard Book Number (R)
        for field in record.get_fields('020'):
            id_alternate_notes = field.get_subfields('c','q','9')
            for code, val in field.get_subfields('a','z', with_codes=True):
                rb.set_id_alternate("ISBN",  # "International Standard Book Number" ?
                                    val.strip(),
                                    'invalid' if code=='z' else 'valid')
                for note in id_alternate_notes:
                    rb.add_id_alternate_note(note, "annotation")
                rb.add_id_alternate()

        # 022  International Standard Serial Number (R)
        for field in record.get_fields('022'):
            id_alternate_notes = field.get_subfields('9')
            for code, val in field.get_subfields('a','l','m','y','z', with_codes=True):
                status = { 'a': 'valid',
                           'l': 'valid linking',
                           'm': 'cancelled linking',
                           'y': 'incorrect',
                           'z': 'cancelled' }.get(code)
                rb.set_id_alternate("ISSN",  # "International Standard Serial Number" ?
                                    val.strip(),
                                    status)
                for note in id_alternate_notes:
                    rb.add_id_alternate_note(note, "annotation")
                rb.add_id_alternate()

        # 024  Other Standard Identifier (incl ISBN 13) (R)
        for field in record.get_fields('024'):
            if field.indicator1 == '7':
                id_source = field['2'] if '2' in field else 'unknown'
                if id_source.strip().lower() == 'doi':
                    id_description = tfcm.build_simple_ref("International DOI Foundation", ORGANIZATION)
                else:
                    id_description = f"Standard identifier; source: {id_source}"
            else:
                id_description = { '0': "International Standard Recording Code",
                                   '1': "Universal Product Code",
                                   '2': "International Standard Music Number",
                                   '3': "International Article Number (EAN) / ISBN 13",
                                   '4': "Serial Item and Contribution Identifier"
                                   }.get(field.indicator1, "Unspecified standard identifier")
            id_alternate_notes = field.get_subfields('c','d','q','9')
            for code, val in field.get_subfields('a','z', with_codes=True):
                rb.set_id_alternate(id_description, val.strip(),
                                    'invalid' if code=='z' else 'valid')
                for note in id_alternate_notes:
                    rb.add_id_alternate_note(note, "annotation")
                rb.add_id_alternate()

        # 027  Standard Technical Report Number (R)
        for field in record.get_fields('027'):
            for code, val in field.get_subfields('a','z', with_codes=True):
                rb.add_id_alternate("Standard Technical Report Number",
                                    val.strip(),
                                    'invalid' if code=='z' else 'valid')

        # 028  [NON-LANE] Publisher or Distributor Number (R)
        for field in record.get_fields('028'):
            id_description = { '0': "Issue number",
                               '1': "Matrix number",
                               '2': "Plate number",
                               '3': "Music publisher number",
                               '4': "Video recording publisher number",
                               '5': "Publisher number",
                               '6': "Distributor number"
                             }.get(field.indicator1, \
                                   "Unspecified standard identifier")
            id_description += f" ({field['b'] if 'b' in field else 'source unknown'})"
            id_alternate_notes = field.get_subfields('q')
            for code, val in field.get_subfields('a', with_codes=True):
                rb.set_id_alternate(id_description, val.strip())
                for note in id_alternate_notes:
                    rb.add_id_alternate_note(note, "annotation")
                rb.add_id_alternate()

        # 030  CODEN Designation (R)
        for field in record.get_fields('030'):
            for code, val in field.get_subfields('a','z', with_codes=True):
                rb.add_id_alternate("CODEN",
                                    val.strip(),
                                    'invalid' if code=='z' else 'valid')

        # 032  Postal Registration Number (R)
        for field in record.get_fields('032'):
            id_description = "Postal Registration Number"
            id_description += f" ({field['b'] if 'b' in field else 'source unknown'})"
            for code, val in field.get_subfields('a', with_codes=True):
                rb.add_id_alternate(id_description, val.strip())

        # 035  System Control Number
        for field in record.get_fields('035'):
            for code, val in field.get_subfields('a','z', with_codes=True):
                if code == 'a' and val == record['001'].data:
                    # ignore repeated Lane control number
                    continue
                if field.indicator1 == '8':
                    # 8#  MeSH Control No.
                    id_desc = self.nlm_org_ref
                else:
                    val_lower = val.lower().strip()
                    if val_lower.startswith("(ocolc)(dnlm)") or val_lower.startswith("(dnlm)(ocolc)"):
                        id_desc = [self.nlm_org_ref, self.oclc_org_ref]
                    elif val_lower.startswith("(dnlm)"):
                        id_desc = self.nlm_org_ref
                    elif val_lower.startswith("(ocolc)"):
                        id_desc = self.oclc_org_ref
                    elif val_lower.startswith("(pmid)"):
                        id_desc = tfcm.build_simple_ref("PubMed", WORK_INST)
                    elif val_lower.startswith("(orcid)"):
                        id_desc = tfcm.build_simple_ref("ORCID Initiative", ORGANIZATION)
                    elif val_lower.startswith("(stanf)"):
                        id_desc = tfcm.build_simple_ref("Stanford University", ORGANIZATION)
                    elif val_lower.startswith("(ssn)"):
                        id_desc = tfcm.build_simple_ref("United States Social Security Administration", ORGANIZATION)
                    elif val_lower.startswith("(laneconnex)"):
                        id_desc = tfcm.build_simple_ref("LaneConnex", WORK_INST)
                    elif val_lower.startswith("(bassett)"):
                        id_desc = tfcm.build_simple_ref("Bassett collection of stereoscopic images of human anatomy", WORK_INST)
                    elif val_lower.startswith("(geonameid)"):
                        id_desc = "GeoNames"
                    elif val_lower.startswith("(isni)"):
                        id_desc = "International Standard Name Identifier"
                    elif val_lower.startswith("(viaf)"):
                        id_desc = "Virtual International Authority File"
                    else:
                        id_desc = "Other system control number"
                rb.add_id_alternate(id_desc, val.strip(), 'valid' if code=='a' else 'invalid')

        # 074   GPO Item Number (R)
        for field in record.get_fields('074'):
            for code, val in field.get_subfields('a','z', with_codes=True):
                rb.add_id_alternate("GPO Item Number",
                                    val.strip(),
                                    'invalid' if code=='z' else 'valid')

        # HOLDINGS ONLY: call numbers
        if record.get_record_type() == record.HDG:
            # 050   Library of Congress Call Number (R)
            # for field in record.get_fields('050'):
            #     for code, val in field.get_subfields('a','b', with_codes=True):
            #         rb.add_id_alternate("Library of Congress Call Number",
            #                             val.strip(), 'valid')
            # 060   National Library of Medicine Call Number (R)
            # for field in record.get_fields('060'):
            #     for code, val in field.get_subfields('a','b', with_codes=True):
            #         rb.add_id_alternate("National Library of Medicine Call Number",
            #                             val.strip(), 'valid')
            # 086   Government Document Classification Number (R)
            for field in record.get_fields('086'):
                id_description = "Government Document Classification Number"
                if field.indicator1 == '0':
                    id_description += f" (Superintendent of Documents Classification System)"
                elif field.indicator1 == '1':
                    id_description += f" (Government of Canada Publications: Outline of Classification)"
                elif '2' in field:
                    id_description += f"; source: {field['2']}"
                for code, val in field.get_subfields('a','z', with_codes=True):
                    rb.add_id_alternate(id_description, val.strip(),
                                        'invalid' if code=='z' else 'valid')

        # AUT ONLY: 7XX LC/NLM forms
        elif record.get_record_type() == record.AUT:
            """
                700  Established Heading Linking Entry, Personal Name (Lane: LC naf equiv) (R)
                710  Established Heading Linking Entry, Organization Name (Lane: LC naf equiv) (R)
                711  Established Heading Linking Entry, Event Name (Lane: LC naf equiv) (R)
                730  Established Heading Linking Entry, Uniform Title (Lane: LC naf equiv) (R)
                748  Established Heading Linking Entry, Chronological Term (Lane: NLM equiv) (R)
                750  Established Heading Linking Entry, Topical Term (Lane: LCSH equiv) (R)
                751  Established Heading Linking Entry, Geographic Name (Lane: LCSH equiv) (R)
                755  Established Heading Linking Entry, Category Term (Lane: NLM PT equiv) (R)
                780  Qualifier Heading Linking Entry, General Qualifier (Lane: pending) (R)
                781  Qualifier Heading Linking Entry, Geographic Qualifier (Lane: pending) (R)
                782  Qualifier Heading Linking Entry, Textword (Lane: pending. UMLS equiv?) (R)
                785  Qualifier Heading Linking Entry, Category Qualifier (Lane: pending) (R)
            """
            for field in record.get_fields("700","710","711","730","748","750","751","755","780","781","782","785"):
                if field.indicator2 == '9':
                    # Lane topical equivalent to category.
                    # Used on 155 "shadow records" of equivalent 150s for Voyager indexing purposes.
                    # records with these shouldn't be transformed in the first place.
                    raise ValueError(f"{record.get_control_number()}: 7XX I2=9: {field}")

                id_description = self.nlm_org_ref if field.tag in ('748','755') or field.indicator2 == '2' else self.lc_org_ref
                id_value = ' '.join(field.get_subfields('0')).strip() or "notyet"

                field.delete_all_subfields('0')

                rb.set_id_alternate(id_description, id_value, 'valid')
                rb.add_id_alternate_note(str(field), "documentation")
                rb.add_id_alternate()

        # 902   Expanded ISN Information (Lane) (R)
        for field in record.get_fields('902'):
            for code, val in field.get_subfields('a','z', with_codes=True):
                # either ISBN or ISSN, needs parsing to figure out which
                # parse out parenthetics (qualifiers)
                has_qualifier = re.match(r'([^\(]+)(\(.+)$', val)
                if has_qualifier:
                    val, qualifier = has_qualifier.groups()
                digit_count = len(re.sub(r'[^0-9X]', '', val.upper()))
                if digit_count >= 9:
                    id_description = "ISBN"
                elif digit_count == 8:
                    id_description = "ISSN"
                else:
                    id_description = "Unspecified standard identifier"
                rb.set_id_alternate(id_description,
                                    val.strip(),
                                    'invalid' if code=='z' else 'valid')
                if has_qualifier:
                    rb.add_id_alternate_note(qualifier, "annotation")
                rb.add_id_alternate()

        # 990 ^w Purchase Order no./Obsolete Lane Control No. (NR)
        for field in record.get_fields('990'):
            for val in field.get_subfields('w'):
                rb.add_id_alternate(self.lane_org_ref,
                                    val.strip(),
                                    'cancelled')


    def __get_entry_group_id(self, field):
        if field.tag.endswith('50') or field.tag.endswith('80'):
            return field['3'] or field['7']
        return field['6'] or field['7']


    def __preprocess_sumptions(self, record):
        """
        For concept authority records that include 4XX variants of different scope,
        copy all Includes.*: relations to variants of the same group.
        """
        sumptions_map = {}
        for field in record.get_fields('400','410','411','430','450','451','455','480','482'):
            for val in field.get_subfields('e'):
                if re.match(r"Includes( broader| related|[ :]*$)", val, flags=re.I):
                    group_id = self.__get_entry_group_id(field)
                    sumptions_map[group_id] = val
        for field in record.get_fields('400','410','411','430','450','451','455','480','482'):
            group_id = self.__get_entry_group_id(field)
            if group_id in sumptions_map:
                if not any(re.match(r"Includes( broader| related|[ :]*$)", val, flags=re.I) for val in field.get_subfields('e')):
                    field.add_subfield('e',sumptions_map[group_id])
        return record


    def __reconstruct_bib_149_subf_1(self, record):
        """
        149 ^1 generated by RIM strips ending whitespace.
        Look at the 245 to add the whitespace back if necessary.
        """
        if '149' in record and '1' in record['149'] and '245' in record:
            assert record['245'].indicator2.isdigit(), \
                f"{record.get_control_number()}: invalid 245 I2"
            record['149']['1'] = record['245']['a'][:int(record['245'].indicator2)]
        return record


    def __preprocess_041(self, record):
        """
        Only use 043 geocode as variant on auts if exactly one.
        Add ad-hoc 451 and supply the variant type.
        """
        if '041' not in record:
            return record
        language_code_field = record['041']
        if language_code_field.indicator1 == '1' and "Translations" not in record.get_all_categories():
            record.add_ordered_field(Field('655','17',['a','Translations']))
        # @@@@@@@@@@@@@@@@@@@
        # $h isn't a relationship to the present work
        # but if record has a 765 or (single) 730 this is the language of that; add $3 language to that field
        orig_langs = language_code_field.get_subfields('h')
        orig_langs_as_note = True
        if len(orig_langs) == 1:
            fields_730 = [field for field in record.get_fields('730') if field.indicator2 != '8' and 'l' in field]
            fields_765 = record.get_fields('765')
            if len(fields_730) == 1:
                fields_730[0].subfields += ['3', orig_langs[0]]
                orig_langs_as_note = False
            for field in fields_765:
                field.subfields += ['3', orig_langs[0]]
                orig_langs_as_note = False
        # if no field can be found to accept the information, just add a 546 note instead
        if orig_langs_as_note:
            record.add_ordered_field(Field('546','  ',['a', f'Language(s) of original: {"; ".join(orig_langs)}']))
        return record


    def __preprocess_aut_043(self, record):
        """
        Only use 043 geocode as variant on auts if exactly one.
        Add ad-hoc 451 and supply the variant type.
        """
        geocodes = record.get_subfields('043','a')
        if len(geocodes) == 1:
            record.add_ordered_field(Field('451','  ',['e',"MARC geographic area code",'a',geocodes[0]]))
            record.remove_fields('043')
        return record


    @staticmethod
    def __translated_title_730_to_246(record):
        """
        Convert 730 variant (translated) titles to 246, for ease of processing.
        """
        for field in record.get_fields('730'):
            if field.indicator2 == '9' and 'l' in field:
                record.remove_field(field)
                field.delete_all_subfields('l')
                record.add_field(Field('246','  ',['i',"Translated title"] + field.subfields.copy()))
        return record


    @staticmethod
    def __preprocess_aut_68X(record):
        """
        Split any compound 683/684/685 into separate fields,
        then convert any with linkable ^a to 610 for mapping to Relationships.
        """
        # split compound 68X
        for field in record.get_fields('683','684','685'):

            codes = ''.join(field.subfields[::2])
            if any(code not in 'abc' for code in codes):
                # warn of invalid code and ignore this field
                logger.warning(f"{record.get_control_number()}: field contains invalid subfield: {field}")
                continue

            record.remove_field(field)

            # step 1: separate at each abc sequence
            code_sets = re.split(r'(ab?c?|a?bc?|a?b?c)', codes)[1::2]

            # step 2: calculate indices to split at
            subfield_set_lengths = list(map(len, code_sets))
            subfield_set_end_indices = [0] + [sum(subfield_set_lengths[:i+1]) for i, l in enumerate(subfield_set_lengths)]

            # step 3: split subfields into sets, keeping track of current ^a and adding it on
            # to sets without an ^a
            current_a = ''
            subfield_sets = []
            for i,j in zip(subfield_set_end_indices, subfield_set_end_indices[1:]):
                subfield_set = field.subfields[i*2:j*2]
                if 'a' in subfield_set[::2]:
                    current_a = subfield_set[subfield_set[::2].index('a')*2+1]
                elif current_a:
                    subfield_set = ['a',current_a] + subfield_set
                subfield_sets.append(subfield_set)

            for subfield_set in subfield_sets:
                record.add_field(Field(field.tag,'  ',subfield_set))

        # attempt link to organizational authority; but if not, make into Note
        for field in record.get_fields('683','684','685'):
            if any(code not in 'abc' for code in field.subfields[::2]):
                # invalid subfield code, ignore again
                continue
            if 'a' not in field:
                continue

            # all these fields should now only have ^a/^b/^c, and only one of each
            # a -> a, b -> j, c -> 9
            org_rel_subfields = [val if i%2 else {'b':'j','c':'9'}.get(val, val) for i, val in enumerate(field.subfields)]

            # determine relator to insert
            if field.tag == '683':
                relator = 'Graduate'
            else:
                if 'b' in field and re.search(r'(^| )prof(essor)?([ ,;\.]|$)', field['b'].lower()):
                    relator = 'Faculty'
                else:
                    relator = 'Affiliation'

            org_rel_field = Field('610','24', ['e', relator] + org_rel_subfields)

            lookup_result = Indexer.lookup(org_rel_field, ORGANIZATION)
            # logger.debug(f"{record.get_control_number()}\t{field}\t{org_rel_field}\t{lookup_result}",end='\t')

            if lookup_result not in (Indexer.CONFLICT, Indexer.UNVERIFIED):
                # logger.debug(''.join([val if i%2 else '$'+val for i, val in enumerate(Indexer.reverse_lookup(lookup_result))]))
                record.remove_field(field)
                record.add_field(org_rel_field)

        return record


    @staticmethod
    def __preprocess_bib_785(record):
        """
        Relator on bib 785 #7 depends on position in record.
        Temporarily switch the indicator of the last one to 0,
        to be assigned relator "Continued by:"
        """
        merged_with_entries = [field for field in record.get_fields('785') if field.indicator2 == '7']
        if merged_with_entries:
            merged_with_entries[-1].indicator2 = '0'
        return record


    @staticmethod
    def __preprocess_bib_880(record):
        """
        Change tags of certain bib 880s based on linked field.
        """
        for field in record.get_fields('880'):
            linked_field_tag = field['6']
            if linked_field_tag is None:
                raise ValueError(f"linking field tag ($6) not found: {field}")
            linked_field_tag = linked_field_tag[:3]

            if linked_field_tag in ('245','246','500'):
                # 245 --> 246 + ^i Descriptive title, vernacular:
                # 246 --> 246 + ^i Vernacular title:
                # 500 --> 246 (^9 Incipit / Explicit to ^i)
                new_subfields = [code_or_val for code, val in zip(field.subfields[::2], field.subfields[1::2]) for code_or_val in (code, val) if code not in '69']
                if linked_field_tag == '245':
                    new_subfields.extend(['i', "Descriptive title, vernacular"])
                elif linked_field_tag == '246':
                    new_subfields.extend(['i', "Vernacular title"])
                display_text = field['9'] or ''
                if display_text.rstrip(' :').lower() == 'colophon':
                    # skip these here, add them as notes in transform bib note method
                    continue
                if display_text.rstrip(' :').lower() not in ('','title','variant title'):
                    new_subfields.extend(['i', display_text])
                record.remove_field(field)
                record.add_field(Field('246', field.indicators, new_subfields))
            elif linked_field_tag == '250':
                # 250 --> treat as 250
                new_subfields = [code_or_val for code, val in zip(field.subfields[::2], field.subfields[1::2]) for code_or_val in (code, val) if code not in '69']
                record.remove_field(field)
                record.add_field(Field('246', field.indicators, new_subfields))

            # ^6 130, 630, 730, 740, 830 --> note on relationship; deal with this during bib rel transform for those fields
            # but log a warning here if there are multiple candidates
            if linked_field_tag in ('130','630','730','740','830') and len(record.get_fields(linked_field_tag)) > 1:
                logger.warning(f"{record.get_control_number()}: multiple candidates for 880 with linked tag {linked_field_tag}")

        return record


    def __resolve_bib_490_830_901(self, record):
        # first, take every traced 490,
        fields_490 = [field for field in record.get_fields('490') if field.indicator1 == '1']
        #   every nonlocal 830,
        fields_830 = [field for field in record.get_fields('830') if field.indicator1 != '9']
        #   and every 901
        fields_901 = record.get_fields('901')
        # if there's only one relevant 830, the 490s and/or 901s should all match it
        if len(fields_830) == 1:
            for field_490 in fields_490:
                self.__make_490_into_note_on_830(fields_830[0], field_490)
                record.remove_field(field_490)
            for field_901 in fields_901:
                self.__split_830_over_901(record, fields_830[0], field_901)
        else:
            # otherwise, try to align them.
            # 490s:
            #   create map for 490 matching
            field_490_to_830 = {}
            for field_830 in fields_830:
                field_830_normalized_for_490 = re.sub(r'[\s;,.]+$', '', ' '.join(field_830.get_subfields('a','n','p'))).strip().lower()
                if field_830_normalized_for_490 not in field_490_to_830:
                    field_490_to_830[field_830_normalized_for_490] = []
                field_490_to_830[field_830_normalized_for_490].append(field_830)

            for field_490 in fields_490:
                # normalization: strip dates in front and punctuation at end of 490 ^a
                #   (first ^a only, may not work well for multiple ^a)
                series_statement_normalized = re.sub(r'(^[^:]+:\s+|[\s;,.]+$)', '', field_490['a']).strip().lower()
                # now try to match to a SINGLE 830 ^anp
                field_490_to_830_matches = field_490_to_830.get(series_statement_normalized, [])
                if len(field_490_to_830_matches) == 1:
                    # single match found, attach 490 as note and remove 490 from record
                    self.__make_490_into_note_on_830(field_490_to_830_matches[0], field_490)
                    record.remove_field(field_490)
                else:
                    # if no match to a single 830, turn the 490 into a record-level note, as if it were I1==0
                    field_490.indicator1 = '0'
            # 901s:
            #   create map for 901 matching (830 ^aqnp [830 a+q is 901 a])
            field_901_to_830 = {}
            for field_830 in fields_830:
                field_830_normalized_for_901 = re.sub(r'[\s;,.]+$', '', ' '.join(field_830.get_subfields('a','q','n','p'))).strip().lower()
                if field_830_normalized_for_901 not in field_901_to_830:
                    field_901_to_830[field_830_normalized_for_901] = []
                field_901_to_830[field_830_normalized_for_901].append(field_830)

            for field_901 in fields_901:
                # normalization: 901 ^anp
                series_statement_normalized = re.sub(r'[\s;,.]+$', '', ' '.join(field_901.get_subfields('a','n','p'))).strip().lower()
                # now try to match to a SINGLE 830 ^anp
                field_490_to_830_matches = field_901_to_830.get(series_statement_normalized, [])
                if len(field_490_to_830_matches) == 1:
                    # single match found, insert as expansion of that 830
                    self.__split_830_over_901(record, field_490_to_830_matches[0], field_901)
                    record.remove_field(field_901)
                else:
                    # if no match to a single 830, keep the 901 to transform to a record-level note
                    logger.warning(f"{record.get_control_number()}: no 830 match for 901, default to Series Note: {field_901}")


    @staticmethod
    def __make_490_into_note_on_830(field_830, field_490):
        # Attach 490 as note (ad hoc subf @) on 830
        field_830.add_subfield('@', tfcm.concat_subfs(field_490, with_codes=False))


    def __split_830_over_901(self, record, field_830, field_901):
        """
        For each ^v, build separate series entry:
        Title:  ^anpqs ^d <supply> ^v <transform> ^w <if present>
        Override ^d date with parenthetic in ^v; default to date in fixed field
        """
        # 830 might have been split and removed from the record already,
        #   so only do this once
        if field_830 in record.fields:
            record.remove_field(field_830)
        shared_subfields = [code_or_val for code, val in zip(field_830.subfields[::2], field_830.subfields[1::2]) for code_or_val in (code, val) if code not in 'dv']
        default_date = field_830['d'] or record['008'].data[7:10].strip() or 'uuuu'
        for val in field_901.get_subfields('v'):
            # logger.debug(f"{record.get_control_number()}\t{val}")
            enum, date = self.__parse_901_v(val)
            record.add_field(Field('830', '  ', shared_subfields + ['d', date or default_date, 'v', enum]))


    @staticmethod
    def __parse_901_v(val):
        """
        Normalization of enum/chron applied retrospectively for 830, but not to 901.
        For consistency, needs to be applied to ^v
        Omit initial enum labels ("v."/"no."/etc), and parse out parenthetic dates
        """
        # series + number -> ss(nn)
        val = re.sub(r'^ser\.?\s*(\d+),?\s*no\.?\s*(\d+)', r'\1(\2)', val.strip('.,;: '))
        # other enum labels
        val = re.sub(r'^(report register )?no\.?\s*', r'', val.strip('.,;: '))
        # finally parse out date
        val_parse_out_parenthetic_date = re.match(r"([^(]+)\((\d+)\)$", val)
        if val_parse_out_parenthetic_date:
            val, date = val_parse_out_parenthetic_date.groups()
            return val.strip(), date.strip()
        return val.strip(), None


    @staticmethod
    def __preprocess_bib_904(record):
        """
        Convert 904 Title Sort/Shelving Version (Normalized) to equivalent 246 field
        """
        for field in record.get_fields('904'):
            assert 'a' in field or 'x' in field, f"{record.get_control_number()}: 904 with no $a or $x: {field}"
            record.remove_field(field)
            for code, val in field.get_subfields('a','x', with_codes=True):
                new_subfields = ['i',"Normalized sort title",'a',val]
                if code == 'x':
                    new_subfields += ['@',"Exception to algorithm"]
                record.add_field(Field('246','  ',new_subfields))


    def __preprocess_bib_94X(self, record):
        """
        Convert all bib 94X to equivalent Relationship field, based on relevant
        element type/fixed-field data
        """
        element_type = record.get_xobis_element_type()
        bib_type = record.leader[6:8]
        # 941 Place --> 651 27
        for field in record.get_fields('941'):
            # rel = am, as, e, f: "Place of publication:"; aa, ab: ignore; else: "Place of production:"
            if bib_type in ('aa','ab'):
                continue
            if bib_type in ('am','as') or bib_type[0] in 'ef':
                relator = "Place of publication"
            else:
                relator = "Place of production"
            record.remove_field(field)
            record.add_field(Field('651','27',['e',relator,'a',field['a']]))

        # 942 Language --> 650 26
        for field in record.get_fields('942'):
            # rel = aa, ab, am, as, e, f: "Language of text:"; else: "Language:"
            relator = "Language"
            if bib_type in ('aa','ab','am','as') or bib_type[0] in 'ef':
                relator += " of text"
            record.remove_field(field)
            record.add_field(Field('650','26',['e',relator,'a',field['a']]))

        # 943 Date --> 650 25
        #   first, pull dates from fixed field
        fixed_field_dates = record['008'].data[6:15]
        date_type, d1, d2 = fixed_field_dates[0], fixed_field_dates[1:5], fixed_field_dates[5:]
        #     recombine e dates
        if date_type == 'e':
            d1 = (d1 + '-' + d2[:2] + '-' + d2[2:]).strip(' -u')
        relator = self.__get_relator_for_bib_943(record)
        # NONE:
        if date_type == 'b':
            # b - No dates given; B.C. date involved
            record.add_field(Field('650','25',['e',"Produced",'a',"Ancient"]))
        elif date_type in 'n|':
            # n - Dates unknown  /  | - No attempt to code
            record.add_field(Field('650','25',['e',relator,'a',"Unknown"]))
        # SINGLE:
        elif date_type in 'es':
            record.add_field(Field('650','25',['e',relator,'a',d1]))
        # SINGLE or RANGE:
        elif date_type == 'q':
            if d2.strip():
                # range
                record.add_field(Field('650','25',['e',relator,'a',d1+'?','x',d2+'?']))
                if relator == "Published":
                    record.add_field(Field('655','77',['a',"Subset, Date Range Verify"]))
            else:
                # single
                record.add_field(Field('650','25',['e',relator,'a',d1+'?']))
        # RANGE:
        elif date_type == 'c':
            record.add_field(Field('650','25',['e',relator,'a',d1,'x',"Present"]))
        elif date_type in 'dm':
            record.add_field(Field('650','25',['e',relator,'a',d1,'x',d2]))
        elif date_type == 'u':
            record.add_field(Field('650','25',['e',relator,'a',d1,'x',"Unknown"]))
        elif date_type == 'i':
            record.add_field(Field('650','25',['e',"Inclusive dates",'a',d1,'x',d2]))
        elif date_type == 'k':
            record.add_field(Field('650','25',['e',"Bulk dates",'a',d1,'x',d2]))
        # DOUBLE:
        elif date_type == 'p':
            record.add_field(Field('650','25',['e',"Distributed",'a',d1]))
            record.add_field(Field('650','25',['e',"Produced",'a',d2 if d2.strip() else "Unknown"]))
        elif date_type == 'r':
            record.add_field(Field('650','25',['e',"Reprinted",'a',d1]))
            record.add_field(Field('650','25',['e',"Published originally",'a',d2 if d2.strip() else "Unknown"]))
        elif date_type == 't':
            record.add_field(Field('650','25',['e',"Published",'a',d1]))
            record.add_field(Field('650','25',['e',"Copyright",'a',d2 if d2.strip() else "Unknown"]))
        #   then, get manually-entered dates (ignore i2==8)
        manual_dates = [field['a'] for field in record.get_fields('943') if 'a' in field and field.indicator2 != '8']
        record.remove_fields('943')
        for date in manual_dates:
            record.add_field(Field('650','25',['e',"Produced",'a',"Ancient"]))

        return record


    def __preprocess_aut_94X(self, record):
        """
        Convert all aut 94X to equivalent Relationship field, based on relevant
        element type/fixed-field data
        """
        element_type = record.get_xobis_element_type()
        if element_type in (STRING, TIME):
            pass
        elif element_type == CONCEPT:
            self.__handle_943_insert_as_650(record, "Related")
        else:
            relator_941 = {BEING: "Active", EVENT: "Venue"}.get(element_type, "Related")
            for field in record.get_fields('941'):
                assert 'a' in field, f"{record.get_control_number()}: 941 with no $a: {field}"
                record.remove_field(field)
                record.add_field(Field('651','27',['e',relator_941,'a',field['a']]))

            relator_942 = "Related"
            for field in record.get_fields('942'):
                assert 'a' in field, f"{record.get_control_number()}: 942 with no $a: {field}"
                record.remove_field(field)
                record.add_field(Field('650','26',['e',relator_942,'a',field['a']]))

            relator_943 = {EVENT: "Held", ORGANIZATION: "Active", PLACE: "Active"}.get(element_type, "Related")
            self.__handle_943_insert_as_650(record, relator_943)

        return record


    @staticmethod
    def __preprocess_hdg_655(record):
        """
        Most hdg 655 are subsets, so convert their I1 to be treated as such,
        except for a few hardcoded exceptions
        """
        for field in record.get_fields('655'):
            if field['a'] not in ("Archival Materials","Letters","Print Reproductions","Subunits"):
                field.indicator1 = '7'
        return record


    subfb_regex = re.compile(r'(?:^|\s)(AA|CA|DA|PA|NA)(?:[\s:;.,/!?+*]|$)', flags=re.I)
    subfc_regex = re.compile(r'(?:^|\s)(AA|CA|DA|PA|NA)(?:[\s:;.,/!?+*]|$)', flags=re.I)
    def __preprocess_hdg_907(self, record):
        """
        Reduce the compexity of 907s for other transform methods, by splitting
        subfields with multiple codes and separating out notes into ad-hoc subfields
        """
        for field in record.get_fields('907'):
            new_subfields = []
            for code, val in field.get_subfields(with_codes=True):
                if code == 'b':
                    # b  Analysis treatment (AA CA DA PA NA) (NR)
                    # split
                    for extracted_subset_code in self.subfb_regex.findall(val):
                        new_subfields.append(code)
                        new_subfields.append(extracted_subset_code.upper())
                    if re.sub('[\s:;.,/!?+*]', '', self.subfb_regex.sub('', val)):
                        # rest --> $α -> Analysis Treatment Note
                        new_subfields.append('α')
                        new_subfields.append(val)
                elif code == 'c':
                    # c  Classification/shelving pattern (PER EPER SCN VCN MST N/A) (NR)
                    for extracted_subset_code in self.subfb_regex.findall(val):
                        new_subfields.append(code)
                        new_subfields.append(extracted_subset_code.upper())
                    if re.sub('[\s:;.,/!?+*]', '', self.subfb_regex.sub('', val)):
                        # --> $α -> Analysis Treatment Note
                        new_subfields.append('α')
                        new_subfields.append(val)
                else:
                    new_subfields.append(code)
                    new_subfields.append(val)
            field.subfields = new_subfields
        return record


    @staticmethod
    def __get_relator_for_bib_943(record):
        """
        Default relator for (most types of) bib 943 date(s), based on fixed-field material type
        """
        bib_type = record.leader[6:8]
        if re.match(r'[ace][abms]', bib_type):
            return "Published"
        elif bib_type[0] == 't':
            if "Manuscripts, Handwritten" in record.get_all_categories():
                return "Written"
            else:
                return "Printed"
        return "Produced"


    @staticmethod
    def __handle_943_insert_as_650(record, relator):
        """
        Combine all 943 subfields into single 650 25 with single date ($a) or range ($a+$x)
        ("Unknown" if no 943 $a, empty string if no 943 $b)
        """
        if '943' not in record:
            return
        combined_943_subfields = {}
        for field in record.get_fields('943'):
            record.remove_field(field)
            for code, vals in field.subfields_as_dict().items():
                if code not in combined_943_subfields:
                    combined_943_subfields[code] = []
                combined_943_subfields[code].extend(vals)
        start_vals, end_vals = combined_943_subfields.get('a', []), combined_943_subfields.get('b', [])
        assert (len(start_vals) <= 1 and len(end_vals) <= 1), f"{record.get_control_number()}: >1 943 $a or $b"
        new_subfields = ['e', relator, 'a', start_vals[0] if start_vals else "Unknown"]
        if end_vals:
            new_subfields += ['x', end_vals[0]]
        record.add_field(Field('650','25',new_subfields))
