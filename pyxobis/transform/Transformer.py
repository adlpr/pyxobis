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

        # Technically this should come from the 040 ^b? But let's just assume eng
        rb.set_lang('eng')

        # -------
        # IDs
        # -------

        # ID ORG
        # ---
        # is us, Lane
        rb.set_id_org_ref_or_description(self.lane_org_ref)

        # ID VALUE
        # ---
        # 001 plus prefix letter; generated by RIM in 035 ^9
        record_control_no = record.get_control_number()
        # @@@@@ TEMPORARY @@@@@@
        if record_control_no is None:
            return None
        rb.set_id_value(record_control_no)

        # ID STATUS
        # ---
        rb.set_id_status('valid')

        # ID ALTERNATES
        # ---
        self.process_id_alternates(record, rb)

        # -------
        # TYPES
        # -------
        # Record "Types" = Subsets = 655 77
        # NB: Established aut "Record Type" (Z47381) actually refers
        #     to which PE a record is
        for field in record.get_fields('655'):
            if field.indicator1 == '7':
                title = field['a']
                href  = field['0'] or self.ix.simple_lookup(title, CONCEPT)
                set_ref = self.ix.simple_lookup("Subset", CONCEPT)
                rb.add_type(title, href, set_ref)

        # -------
        # ACTIONS
        # -------
        # Administrative metadata (get these from: 007; oracle??)
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
        assert element_type, "could not determine type of record {}".format(record['001'].data)
        # @@@@@ TEMPORARY @@@@@
        if not element_type:
            # don't transform
            return None

        # Preprocessing for entry groups/sumptions
        record = self.__preprocess_sumptions(record)
        # Fix 149 ^1 on bib records if necessary
        record = self.__reconstruct_149_subf_1(record)

        if element_type != HOLDINGS:

            init_builder, parse_name = {
                WORK_INST    : (self.init_work_instance_builder, self.np.parse_work_instance_main_name),
                WORK_AUT     : (self.init_work_authority_builder, self.np.parse_work_authority_name),
                BEING        : (self.init_being_builder, self.np.parse_being_name),
                CONCEPT      : (self.init_concept_builder, self.np.parse_concept_name),
                RELATIONSHIP : (self.init_concept_builder, self.np.parse_concept_name),
                EVENT        : (self.init_event_builder, self.np.parse_event_name),
                LANGUAGE     : (self.init_language_builder, self.np.parse_language_name),
                OBJECT       : (self.init_object_builder, self.np.parse_object_main_name),
                ORGANIZATION : (self.init_organization_builder, self.np.parse_organization_name),
                PLACE        : (self.init_place_builder, self.np.parse_place_name),
                STRING       : (self.init_string_builder, self.np.parse_string_name),
                TIME         : (self.init_time_builder, lambda x: ([],[])),  # first method does the name parsing
            }.get(element_type)

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
                print("WARNING: Peoples without ind 9#: {}".format(record['001'].data))
            else:
                being_class = 'collective'
        elif broad_category == 'Persons, Families or Groups':
            if record['100'].indicator1 != '3':
                print("WARNING: Family/Group without ind 3#: {}".format(record['001'].data))
            being_class = 'familial'
        else:
            if record['100'].indicator1 not in '01':
                print("WARNING: Individual without ind [01]#: {}".format(record['001'].data))
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
            # other types aren't really in our catalog, I guess
            cb.set_subtype("topical")

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


    # Defined in order of increasing priority.
    event_type_map = {
        'miscellaneous' : ["Censuses", "Exhibitions", "Exhibits", "Experiments",
            "Special Events", "Trials", "Workshops"],
        'natural' : ["Cyclonic Storms", "Earthquakes", "Fires", "Floods", "Tsunamis"],
        'meeting' : ["Congresses", "Legislative Sessions"],
        'journey' : ["Expeditions", "Medical Missions, Official"],
        'occurrence' : ["Armed Conflicts", "Biohazard Release",
            "Chemical Hazard Release", "Civil Disorders", "Disasters",
            "Disease Outbreaks", "Explosions", "Mass Casualty Incidents",
            "Radioactive Hazard Release", "Riots"]
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

        # PREQUALIFIER(S)
        # ---
        event_prequalifiers = self.np.parse_event_prequalifiers(record.get_id_field())
        for prequalifier in event_prequalifiers:
            eb.add_prequalifier(prequalifier)

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

        # PREQUALIFIER(S)
        # ---
        org_prequalifiers = self.np.parse_organization_prequalifiers(record.get_id_field())
        for prequalifier in org_prequalifiers:
            ob.add_prequalifier(prequalifier)

        return ob

    # Defined in order of increasing priority.
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
        # ^g Grammatical type
        field_lang, field_script = id_field['3'], id_field['4']
        for val in id_field.get_subfields('g'):
            sb.add_pos( pos_text    = val,
                        pos_lang    = field_lang,
                        xlink_title = None,  # we don't have these established yet
                        xlink_href  = None )

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
        calendar_kwargs, datestring = self.dp.extract_calendar(datestring)
        if calendar_kwargs:
            tb.set_calendar(**calendar_kwargs)

        # ENTRY CONTENT
        # ---
        # This is necessary for Time in place of a NameParser method
        time_content_single = self.dp.parse_simple(datestring)
        tb.set_time_content_single(time_content_single)

        return tb


    # Possible primary categories of "artistic" type Works.
    work_cats_artistic = [
        "Animation", "Architectural Drawings", "Art Originals",
        "Art Reproductions", "Cartoons", "Drama", "Drawings",
        "Graphic Reproductions", "Graphics", "Herbal Illustrations",
        "Illustrations", "Music", "Paintings", "Phonodiscs", "Plates",
        "Portraits", "Postcards", "Posters",
        "Sculpture", "Visual Materials", "Video Games"
    ]

    def init_work_authority_builder(self, record):
        wb = WorkBuilder()

        # TYPE
        # ---
        # intellectual, artistic
        primary_cats = record.get_primary_categories()
        if any(cat in self.work_cats_artistic for cat in primary_cats):
            wb.set_type('artistic')
        else:
            wb.set_type('intellectual')

        # ROLE
        # ---
        # (authority)
        wb.set_role('authority')

        # CLASS
        # ---
        # individual, serial, collective, referential
        if record.is_referential():
            wb.set_class('referential')
        else:
            broad_cat = record.get_broad_category()
            if broad_cat == "Series":
                wb.set_class('serial')
            # otherwise is Title, Formal
            wb.set_class('collective')  # ??

        # ENTRY GROUP
        # ---
        # n/a

        return wb


    def init_work_instance_builder(self, record):
        wb = WorkBuilder()

        # TYPE
        # ---
        # intellectual, artistic
        primary_cats = record.get_primary_categories()
        if any(cat in self.work_cats_artistic for cat in primary_cats):
            wb.set_type('artistic')
        else:
            wb.set_type('intellectual')

        # ROLE
        # ---
        # (instance)
        wb.set_role('instance')

        # CLASS
        # ---
        # individual, serial, collective, referential
        # auts are collective? so instances are only ref/ind/ser?
        if record.is_referential():
            wb.set_class('referential')
        else:
            broad_cat = record.get_broad_category()
            if broad_cat == "Serials":
                wb.set_class('serial')
            else:
                wb.set_class('individual')

        # ENTRY GROUP
        # ---
        # n/a

        # HOLDINGS
        # ---
        ...
        ...
        ...

        return wb


    def init_object_builder(self, record):
        ob = ObjectBuilder()

        # ROLE
        # ---
        # (instance)
        ob.set_role('instance')

        # CLASS
        # ---
        # individual, collective, [referential: aut only]
        ob.set_role('individual')

        # TYPE
        # ---
        # natural, crafted, manufactured
        # too difficult to determine this for sure based on category alone.
        # n/a for now

        # ENTRY GROUP
        # ---
        # n/a

        # ORGANIZATION
        # ---
        # = Lane for all our items
        ob.set_organization(self.lane_org_ref)

        # HOLDINGS
        # ---
        ...
        ...
        ...

        return ob



    # def transform_holdings(self, record):
    #     return None


    # bring imported methods into class scope
    # (temporary solution for the sake of organization)

    transform_variants = transform_variants
    transform_variant_being = transform_variant_being
    transform_variant_concept = transform_variant_concept
    transform_variant_event = transform_variant_event
    transform_variant_language = transform_variant_language
    transform_variant_organization = transform_variant_organization
    transform_variant_place = transform_variant_place
    transform_variant_string = transform_variant_string
    transform_variant_time = transform_variant_time
    transform_variant_work_instance = transform_variant_work_instance
    transform_variant_work_authority = transform_variant_work_authority
    transform_variant_object = transform_variant_object

    transform_notes = transform_notes

    transform_relationships_aut = transform_relationships_aut
    transform_relationships_bib = transform_relationships_bib


    def __build_simple_org_ref(self, name):
        orb = OrganizationRefBuilder()
        orb.set_link(name, self.ix.simple_lookup(name, ORGANIZATION))
        orb.add_name(name, 'eng')
        return orb.build()

    def process_id_alternates(self, record, rb):
        # 010  Library of Congress Control Number (NR)
        for val in record.get_subfields('010','a'):
            rb.add_id_alternate(self.lc_org_ref, val.strip(), 'valid')
        for val in record.get_subfields('010','b'):
            rb.add_id_alternate("NUCMC", val.strip(), 'valid')
        for val in record.get_subfields('010','z'):
            rb.add_id_alternate(self.lc_org_ref, val.strip(), 'invalid')

        # 015  National Bibliography Number (NR)
        for val in record.get_subfields('015','a'):
            rb.add_id_alternate("National Bibliography Number", val.strip())

        # 017  Copyright Registration Number (R)
        for field in record.get_fields('017'):
            id_description = "Copyright Registration Number"
            if 'b' in field:
                id_description += " assigned by: {}".format(field['b'].strip())
            rb.add_id_alternate(id_description, field['a'].strip())

        # ARE THESE IDS OR NOTES OR WHAT
        # 020  International Standard Book Number (R)
        ...
        ...
        ...
        ...
        ...
        ...
        # 022  International Standard Serial Number (R)
        # 024  Other Standard Identifier (incl ISBN 13) (R)
        # 027  Standard Technical Report Number (R)
        # 028  [NON-LANE] Publisher or Distributor Number (R)
        # 030  CODEN Designation (R)
        # 032  Postal Registration Number (R)
        # 034  [NON-LANE] Coded Cartographic Mathematical Data (R)

        # 035  System Control Number
        #    8#  MeSH Control No.
        for field in record.get_fields('035'):
            if field.indicator1 == '8':
                for val in field.get_subfields('a'):  # ^z ??
                    rb.add_id_alternate(self.nlm_org_ref, val.strip(), 'valid')
                for val in field.get_subfields('z'):  # ^z ??
                    rb.add_id_alternate(self.nlm_org_ref, val.strip(), 'invalid')

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

    def get_type_and_time_from_relator(self, field):
        """
        For 1XX and 4XX fields, the ^e "relator" and its time/duration qualifiers ^8 and ^9
        aren't describing an actual relationship, but rather a "type" of main or variant entry.

        Returns a Type kwarg dict and a Time/Duration Ref object, for use in a Builder.
        """
        type_kwargs, type_time_or_duration_ref = {}, None

        # Type "relator"
        # Valid variant types include any Equivalence relationship concepts
        entry_type = field['e']
        if entry_type and not entry_type.startswith('Includes'):
            entry_type = entry_type.rstrip(':').strip()
            type_kwargs = { 'link_title' : entry_type,
                            'set_URI'    : self.ix.simple_lookup("Equivalence", CONCEPT),
                            'href_URI'   : self.ix.simple_lookup(entry_type, CONCEPT) }

        # Time or Duration
        if field.tag not in ['150','180','450','480']:  # exceptions for MeSH style fields
            start_type_datetime, end_type_datetime = field['8'], field['9']
            type_datetime = start_type_datetime + end_type_datetime  \
                            if start_type_datetime and end_type_datetime  \
                            else end_type_datetime or start_type_datetime
            if type_datetime:
                type_time_or_duration_ref = self.dp.parse_as_ref(type_datetime, element_type=None)

        return type_kwargs, type_time_or_duration_ref

    def get_type_and_time_from_title_field(self, field):
        """
        For bib 2XX fields, its tag and indicators indicate the type of title variant.
        Returns a Type kwarg dict for use in a Builder.
        """
        entry_type = None

        if field.tag == '210':
            entry_type = "Abbreviated title"
        elif field.tag == '245':
            entry_type = "Descriptive title"
        elif field.tag == '246':
            if field.indicator2 == '0':
                entry_type = "Portion of title"
            elif field.indicator2 == '1':
                entry_type = "Parallel title"
            elif field.indicator2 == '2':
                entry_type = "Distinctive title"
            elif field.indicator2 == '4':
                entry_type = "Cover title"
            elif field.indicator2 == '5':
                entry_type = "Added title page title"
            elif field.indicator2 == '6':
                entry_type = "Caption title"
            elif field.indicator2 == '7':
                entry_type = "Running title"
            elif field.indicator2 == '8':
                entry_type = "Spine title"
            else:
                entry_type = "Other title"
        elif field.tag == '247':
            entry_type = "Former title"
        elif field.tag == '249':
            entry_type = "Added title for website"

        type_kwargs = { 'link_title' : entry_type,
                        'set_URI'    : self.ix.simple_lookup("Equivalence", CONCEPT),
                        'href_URI'   : self.ix.simple_lookup(entry_type, CONCEPT)
                      } if entry_type else {}

        return type_kwargs

    def extract_included_relation(self, field):
        """
        Input: PyMARC Field
        Output: 1) Changed (if applicable) Field object
                2) String value for "included" attribute for use in a VariantBuilder
        """
        for val in field.get_subfields('e'):
            if re.match(r"Includes broader", val, flags=re.I):
                field.delete_subfield('e', val)
                return field, 'broader'
            elif re.match(r"Includes related", val, flags=re.I):
                field.delete_subfield('e', val)
                return field, 'related'
            elif re.match(r"Includes[ :]*$", val, flags=re.I):
                field.delete_subfield('e', val)
                return field, 'narrower'
        return field, None

    def __get_entry_group_id(self, field):
        if field.tag.endswith('50') or field.tag.endswith('80'):
            return field['3'] or field['7']
        else:
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

    def __reconstruct_149_subf_1(self, record):
        """
        149 ^1 generated by RIM strips ending whitespace.
        Look at the 245 to add the whitespace back if necessary.
        """
        if '149' in record and '1' in record['149'] and '245' in record:
            assert record['245'].indicator2.isdigit(), \
                   "Invalid 245 indicator 2 in record {}".format(record.get_control_number())
            record['149']['1'] = record['245']['a'][:int(record['245'].indicator2)]
        return record
