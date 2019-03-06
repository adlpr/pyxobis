#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
import os, json
import pyxobis
from pyxobis.builders import *
from .LaneMARCRecord import LaneMARCRecord
from .Indexer import Indexer
from .DateTimeParser import DateTimeParser
from .NameParser import NameParser
from .tf_variants import *
from .tf_common import *
from .tf_relationships_aut import *
from .tf_relationships_bib import *
from .tf_notes_aut import *
from .tf_notes_bib import *


class Transformer:
    def __init__(self):
        self.ix = Indexer()
        self.dp = DateTimeParser()
        self.np = NameParser()
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
            TIME         : self.init_time_builder
        }
        self.name_parsers = {
            WORK_INST    : self.np.parse_work_instance_main_name,
            WORK_AUT     : self.np.parse_work_authority_name,
            BEING        : self.np.parse_being_name,
            CONCEPT      : self.np.parse_concept_name,
            RELATIONSHIP : self.np.parse_concept_name,
            EVENT        : self.np.parse_event_name,
            LANGUAGE     : self.np.parse_language_name,
            OBJECT       : self.np.parse_object_main_name,
            ORGANIZATION : self.np.parse_organization_name,
            PLACE        : self.np.parse_place_name,
            STRING       : self.np.parse_string_name,
            TIME         : lambda _: []
        }
        self.lane_org_ref = self.build_simple_ref("Lane Medical Library", ORGANIZATION)
        self.lc_org_ref   = self.build_simple_ref("Library of Congress", ORGANIZATION)
        self.nlm_org_ref  = self.build_simple_ref("National Library of Medicine (U.S.)", ORGANIZATION)
        self.oclc_org_ref = self.build_simple_ref("OCLC", ORGANIZATION)
        self.mesh_ref     = self.build_simple_ref("Medical subject headings", WORK_AUT)
        # map of 043 geographic area codes to entry names for relationships
        # with open(os.path.join(os.path.dirname(__file__), 'gacs.json'), 'r') as inf:
        #     self.gacs_map = json.load(inf)

    def transform(self, record):
        record.__class__ = LaneMARCRecord

        # Ignore record if suppressed.
        if record.is_suppressed():
            return None

        # @@@@@ TEMPORARY: IGNORE IMMI RECS @@@@@
        if '040' in record and record['040']['a'] == "IMMI":
            return None

        rb = RecordBuilder()

        # -------------
        # CONTROLDATA
        # -------------

        # -------
        # LANGUAGE OF RECORD
        # -------

        # Technically this should come from the 040 ^b? But all ours should be eng
        rb.set_lang('eng')

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

        # ID ALTERNATES
        # ---
        self.transform_id_alternates(record, rb)
        # AUT ONLY: 7XX LC/NLM forms
        if record.get_record_type() == record.AUT:
            self.transform_heading_linking_entries(record, rb)

        # -------
        # TYPES
        # -------
        # Record "Types" = Subsets = 655 77
        # NB: Established aut "Record Type" (Z47381) actually refers
        #     to which PE a record is
        for field in record.get_fields('655'):
            if field.indicator1 in '7':
                title = field['a']
                href  = "(CStL)" + field['0'] if '0' in field else self.ix.simple_lookup(title, CONCEPT)
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
        # assert element_type, f"{record.get_control_number()}: could not determine type of record"
        # @@@@@ TEMPORARY @@@@@
        if not element_type or element_type == HOLDINGS:
            # don't transform
            return None

        # ~~~~~~
        # RECORD PREPROCESSING
        # ~~~~~~
        # Preprocessing for entry groups/sumptions
        self.__preprocess_sumptions(record)
        # Fix 149 ^1 on bib records if necessary
        self.__reconstruct_149_subf_1(record)
        # Only use 043 geocode as variant on auts if exactly one
        self.__preprocess_043(record)
        # Convert 730 variant (translated) titles to 246, for ease of processing
        self.__translated_title_730_to_246(record)
        # Split aut 68X (education/affiliation) fields, and/or convert to 610 (Organizational Relationship).
        self.__preprocess_68X(record)
        # Relator on 785 #7 depends on position in record.
        self.__preprocess_785(record)
        # If a linking field just links a control number, pull info into the field itself.
        # self.__preprocess_w_only_linking_fields(record)

        # ~~~~~~
        # RECORD PROCESSING
        # ~~~~~~
        init_builder = self.init_builder_methods.get(element_type)
        parse_name = self.name_parsers.get(element_type)

        # Initialize, perform PE-specific work on, and return Builder object.
        peb = init_builder(record)

        # ENTRY NAME(S) AND QUALIFIERS
        # -------
        entry_names_and_qualifiers = parse_name(record.get_id_field())
        for entry_name_or_qualifier in entry_names_and_qualifiers:
            if isinstance(entry_name_or_qualifier, dict):
                peb.add_name(**entry_name_or_qualifier)
            else:
                peb.add_qualifier(entry_name_or_qualifier)

        # VARIANTS
        # -------
        for variant in self.transform_variants(record):
            peb.add_variant(variant)

        # NOTES
        # -------
        notes = self.transform_notes_bib(record)  \
                    if element_type in (WORK_INST, OBJECT)  \
                    else self.transform_notes_aut(record)
        for note in notes:
            peb.add_note(**note)

        rb.set_principal_element(peb.build())

        # RELATIONSHIPS
        # -------
        relationships = self.transform_relationships_bib(record)  \
                            if element_type in (WORK_INST, OBJECT)  \
                            else self.transform_relationships_aut(record)
        for relationship in relationships:
            rb.add_relationship(relationship)

        return rb.build()



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
                print(f"WARNING: Peoples without ind 9#: {self.get_control_number()}")
            else:
                being_class = 'collective'
        elif broad_category == 'Persons, Families or Groups':
            if record['100'].indicator1 != '3':
                print(f"WARNING: Family/Group without ind 3#: {self.get_control_number()}")
            being_class = 'familial'
        else:
            if record['100'].indicator1 not in '01':
                print(f"WARNING: Individual without ind [01]#: {self.get_control_number()}")
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
        wb.set_role('authority')

        # CLASS
        # ---
        # individual, serial, collective, referential
        if record.is_referential():
            wb.set_class('referential')
        else:
            broad_cat = record.get_broad_category()
            if broad_cat == "Series":
                # 130s should all be unnumbered series, NOT "serial"
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
        if any(cat in self.work_cats_artistic for cat in primary_cats):
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
            broad_cat = record.get_broad_category()

            # collections should have "collective"
            # ......

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
    transform_variant_work_instance_or_object = transform_variant_work_instance_or_object

    transform_notes_aut = transform_notes_aut
    transform_notes_bib = transform_notes_bib

    transform_relationships_aut = transform_relationships_aut
    transform_relationships_bib = transform_relationships_bib

    ref_builders = {
        WORK_INST    : WorkRefBuilder,
        WORK_AUT     : WorkRefBuilder,
        BEING        : BeingRefBuilder,
        CONCEPT      : ConceptRefBuilder,
        RELATIONSHIP : ConceptRefBuilder,
        EVENT        : EventRefBuilder,
        LANGUAGE     : LanguageRefBuilder,
        OBJECT       : ObjectRefBuilder,
        ORGANIZATION : OrganizationRefBuilder,
        PLACE        : PlaceRefBuilder,
        STRING       : StringRefBuilder
    }

    def build_simple_ref(self, name, element_type):
        """
        Build a ref based on only a single name string and its element type.
        """
        rb_class = self.ref_builders.get(element_type)
        assert rb_class, f"invalid element type: {element_type}"
        rb = rb_class()
        rb.set_link(name, self.ix.simple_lookup(name, element_type))
        rb.add_name(name)
        return rb.build()


    def build_ref_from_field(self, field, element_type):
        """
        Build a ref based on a parsable field and its element type.
        Most useful for generating targets of Relationships.
        """
        rb_class = self.ref_builders.get(element_type)
        name_parser = self.name_parsers.get(element_type)
        assert rb_class and name_parser, f"invalid element type: {element_type}"
        rb = rb_class()
        # names/qualifiers
        ref_names_and_qualifiers = name_parser(field)
        for ref_name_or_qualifier in ref_names_and_qualifiers:
            if isinstance(ref_name_or_qualifier, dict):
                rb.add_name(**ref_name_or_qualifier)
            else:
                rb.add_qualifier(ref_name_or_qualifier)
        # link attrs
        if not (field.tag in ('700','710') and element_type == WORK_INST): # ignore author-title field works
            rb.set_link(*self.get_linking_info(field, element_type))
        # subdivisions
        if element_type in (CONCEPT, LANGUAGE) and not field.tag.endswith('80'):
            # ^vxyz should always be subdivisions in concept/language fields
            for code, val in field.get_subfields('v','x','y','z', with_codes=True):
                if code == 'v':
                    # ^v = CONCEPT (i.e. form)
                    subdiv_element_type = CONCEPT
                elif code == 'x':
                    # ^x = CONCEPT or LANGUAGE
                    subdiv_element_type = CONCEPT if element_type == CONCEPT else LANGUAGE
                elif code == 'y':
                    # ^y = TIME
                    subdiv_element_type = TIME
                else:
                    # ^z = PLACE
                    subdiv_element_type = PLACE
                val_href = self.ix.simple_lookup(val, subdiv_element_type)
                rb.add_subdivision_link(val,
                                        content_lang = None,
                                        link_title = val,
                                        href_URI = val_href,
                                        substitute = None)
        return rb.build()


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
            id_alternate_notes = field.get_subfields('c','q')
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
                    id_description = self.build_simple_ref("International DOI Foundation", ORGANIZATION)
                else:
                    id_description = "Standard identifier; source: " + id_source
            else:
                id_description = { '1': "Universal Product Code",
                                   '3': "International Article Number (EAN) / ISBN 13",
                                   '4': "Serial Item and Contribution Identifier"
                                   }.get(field.indicator1)
            if not id_description:
                id_description = "Unspecified standard identifier"
            id_alternate_notes = field.get_subfields('c','d','q')
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
                               }.get(field.indicator1)
            if not id_description:
                id_description = "Unspecified standard identifier"
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
                        id_desc = self.build_simple_ref("PubMed", WORK_INST)
                    elif val_lower.startswith("(orcid)"):
                        id_desc = self.build_simple_ref("ORCID Initiative", ORGANIZATION)
                    elif val_lower.startswith("(stanf)"):
                        id_desc = self.build_simple_ref("Stanford University", ORGANIZATION)
                    elif val_lower.startswith("(ssn)"):
                        orb = OrganizationRefBuilder()
                        orb.add_qualifier(self.build_simple_ref("United States", PLACE))
                        # warning: hardcoded id!
                        orb.set_link("Social Security Administration", "Z32655")
                        orb.add_name("Social Security Administration")
                        id_desc = orb.build()
                    elif val_lower.startswith("(laneconnex)"):
                        id_desc = self.build_simple_ref("LaneConnex", WORK_INST)
                    elif val_lower.startswith("(bassett)"):
                        id_desc = self.build_simple_ref("Bassett collection of stereoscopic images of human anatomy", WORK_INST)
                    elif val_lower.startswith("(geonameid)"):
                        id_desc = "GeoNames"
                    elif val_lower.startswith("(isni)"):
                        id_desc = "International Standard Name Identifier"
                    elif val_lower.startswith("(viaf)"):
                        id_desc = "Virtual International Authority File"
                    else:
                        id_desc = "Other system control number"
                rb.add_id_alternate(id_desc, val.strip(), 'valid' if code=='a' else 'invalid')

        # 072   Subject Category Code (Lane: MeSH tree no.) (R)
        ...

        # 074   GPO Item Number (R)
        for field in record.get_fields('074'):
            for code, val in field.get_subfields('a','z', with_codes=True):
                rb.add_id_alternate("GPO Item Number",
                                    val.strip(),
                                    'invalid' if code=='z' else 'valid')

        # 086   Government Document Classification Number (R)
        ...

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


    def transform_heading_linking_entries(self, record, rb):
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

    relator_subf_i_tags = ['246','411']
    def get_type_and_time_from_relator(self, field):
        """
        For 1XX and 4XX fields, the ^e "relator" and its time/duration qualifiers ^8 and ^9
        aren't describing an actual relationship, but rather a "type" of main or variant entry.

        Returns a Type kwarg dict and a Time/Duration Ref object, for use in a Builder.
        """
        type_kwargs = {}

        # Entry Type
        # Valid variant types include any Equivalence relationship concepts
        if field.tag in self.relator_subf_i_tags:
            # exceptions where ^e has other uses
            entry_type = field['i']
        else:
            entry_type = field['e']
        if entry_type and not entry_type.startswith('Includes'):
            entry_type = entry_type.rstrip(':').strip()
            type_kwargs = { 'link_title' : entry_type,
                            'set_URI'    : self.ix.simple_lookup("Equivalence", CONCEPT),
                            'href_URI'   : self.ix.simple_lookup(entry_type, RELATIONSHIP) }

        return type_kwargs, self.get_field_chronology(field)


    def get_field_chronology(self, field):
        """
        Extract chronology of variant type or relation from field (typically subfs 8/9).
        Returns a Time/Duration Ref object.
        """
        type_time_or_duration_ref = None

        # Time or Duration
        if field.tag not in ['150','180','450','480']:  # exceptions for MeSH style fields
            if field.tag in ['650','651','655'] and '7' in field:  # ^7 is start time rather than ID
                start_type_datetime, end_type_datetime = field['7'], field['8'] or field['9']
            else:
                start_type_datetime, end_type_datetime = field['8'], field['9']
            type_datetime = start_type_datetime + end_type_datetime  \
                            if start_type_datetime and end_type_datetime  \
                            else end_type_datetime or start_type_datetime
            if type_datetime:
                type_time_or_duration_ref = self.dp.parse_as_ref(type_datetime, element_type=None)

        return type_time_or_duration_ref


    def get_type_and_time_from_title_field(self, field):
        """
        For bib 2XX fields, take into account particular subfields and
        indicator values to determine the type of title variant.

        Returns a Type kwarg dict and a Time/Duration Ref object, for use in a Builder.
        """
        type_kwargs, type_time_or_duration_ref = {}, None

        # Entry Type
        entry_type = None

        # 246 (or temp 245) ^i
        if 'i' in field:
            entry_type = field['i'].strip()

        # if not otherwise specified, use tag/I2
        if not entry_type:
            if field.tag == '210':
                entry_type = "Abbreviated title"
            elif field.tag == '245':
                # if 149 #8
                entry_type = "Transcribed title"
                # if 149 #9 should be "Descriptive title"
            elif field.tag == '246':
                entry_type = {
                    '0': "Portion of title",
                    '1': "Parallel title",
                    '2': "Distinctive title",
                    '4': "Cover title",
                    '5': "Added title page title",
                    '6': "Caption title",
                    '7': "Running title",
                    '8': "Spine title"
                }.get(field.indicator2, "Other title")
            elif field.tag == '247':
                entry_type = "Former title"
            elif field.tag == '249':
                entry_type = "Added title for website"

        type_kwargs = { 'link_title' : entry_type,
                        'set_URI'    : self.ix.simple_lookup("Equivalence", CONCEPT),
                        'href_URI'   : self.ix.simple_lookup(entry_type, RELATIONSHIP)
                      } if entry_type else {}

        # Time or Duration
        if field.tag in ('246','247'):
            for code, val in field.get_subfields('f','g', with_codes=True):
                # only use this if solely parsable as Time/Duration.
                # otherwise treat as Variant Note
                parsed = self.np.parse_generic_qualifier(val, field['3'], field['4'])
                if isinstance(parsed, pyxobis.classes.TimeRef) or isinstance(parsed, pyxobis.classes.DurationRef):
                    type_time_or_duration_ref = parsed
                    field.delete_subfield(code, val)

        return type_kwargs, type_time_or_duration_ref


    def extract_included_relation(self, field):
        """
        Input: PyMARC Field
        Output: 1) Changed (if applicable) Field object
                2) String value for "included" attribute for use in a VariantBuilder
        """
        subf_code = 'i' if field.tag in self.relator_subf_i_tags else 'e'
        for val in field.get_subfields(subf_code):
            if re.match(r"Includes broader", val, flags=re.I):
                field.delete_subfield(subf_code, val)
                return field, 'broader'
            elif re.match(r"Includes related", val, flags=re.I):
                field.delete_subfield(subf_code, val)
                return field, 'related'
            elif re.match(r"Includes[ :]*$", val, flags=re.I):
                field.delete_subfield(subf_code, val)
                return field, 'narrower'
        return field, None


    def extract_enumeration(self, field):
        """
        Returns a StringRef representing an enumeration
        to pass into a RelationshipBuilder, or None.
        """
        enum = None
        if '1' in field:
            enum = str(int(''.join(d for d in field['1'] if d.isdigit())))
        elif field.tag in ('551','651') and '6' in field:
            enum = str(int(''.join(d for d in field['6'] if d.isdigit())))
        elif field.tag in ('100','110','111'):
            enum = '1'
        return self.build_simple_ref(enum, STRING) if enum else None


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
        else:
            print(record)
        return record

    def __preprocess_043(self, record):
        """
        Only use 043 geocode as variant on auts if exactly one.
        Add ad-hoc 451 and supply the variant type.
        """
        geocodes = record.get_subfields('043','a')
        if len(geocodes) == 1 and record.get_record_type() == record.AUT:
            record.add_ordered_field(Field('451','  ',['e',"MARC geographic area code",'a',geocodes[0]]))
            record.remove_fields('043')
        return record

    def __translated_title_730_to_246(self, record):
        """
        Convert 730 variant (translated) titles to 246, for ease of processing.
        """
        for field in record.get_fields('730'):
            if field.indicator2 == '9' and 'l' in field:
                record.remove_field(field)
                field.delete_all_subfields('l')
                record.add_field(Field('246','  ',['i',"Translated title"] + field.subfields.copy()))
        return record

    def __preprocess_68X(self, record):
        """
        Split any compound 683/684/685 into separate fields,
        then convert any with linkable ^a to 610 for mapping to Relationships.
        """
        # split compound 68X
        for field in record.get_fields('683','684','685'):

            codes = ''.join(field.subfields[::2])
            if any(code not in 'abc' for code in codes):
                # warn of invalid code and ignore this field
                print(f"WARNING: {record.get_control_number()}: field contains invalid subfield: {field}")
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

            lookup_result = self.ix.lookup(org_rel_field, ORGANIZATION)
            # print(f"{record.get_control_number()}\t{field}\t{org_rel_field}\t{lookup_result}",end='\t')

            if lookup_result not in (self.ix.CONFLICT, self.ix.UNVERIFIED):
                # print(''.join([val if i%2 else '$'+val for i, val in enumerate(self.ix.reverse_lookup(lookup_result))]))
                record.remove_field(field)
                record.add_field(org_rel_field)
            # print()

        return record

    def __preprocess_785(self, record):
        """
        Relator on 785 #7 depends on position in record.
        Temporarily switch the indicator of the last one to 0,
        to be assigned relator "Continued by:"
        """
        merged_with_entries = [field for field in record.get_fields('785') if field.indicator2 == '7']
        if merged_with_entries:
            merged_with_entries[-1].indicator2 = '0'
        return record

    # def __preprocess_w_only_linking_fields(self, record):
    #     """
    #     If a 7XX linking field links only a control number,
    #     pull title info into the field itself.
    #     """
    #     for field in record.get_fields():
    #         if field.tag.startswith('7'):
    #             if len(field.subfields) == 2 and 'w' in field:
    #                 linking_ctrlno = "(CStL)" + field['w'].rstrip('. ')
    #                 linking_work_subfields = self.ix.reverse_lookup(linking_ctrlno)
    #                 if not linking_work_subfields:
    #                     # add dummy title
    #                     field.subfields.extend(['t', "Unknown title"])
    #                 else:
    #                     # convert subfield codes
    #                     # linking_work_subfields = []
    #                     print(record['001'].data, linking_ctrlno, linking_work_subfields)
    #                 ...
    #     return record

    def get_relation_type(self, rel_name):
        rel_types = self.ix.lookup_rel_types(rel_name)
        if len(rel_types) == 1:
            return rel_types.pop().lower()
        return None

    def get_linking_entry_field_default_relator(self, field):
        if field.tag in ('780','785'):
            return {'780': {'0': "Continues",
                            '1': "Continues in part",
                            '2': "Supersedes",
                            '3': "Supersedes in part",
                            '4': "Merger of",
                            '5': "Absorbed",
                            '6': "Absorbed in part",
                            '7': "Separated from"},
                    '785': {'0': "Continued by",
                            '1': "Offshoot",
                            '2': "Superseded by",
                            '3': "Superseded in part by",
                            '4': "Absorbed by",
                            '5': "Absorbed in part by",
                            '6': "Split into",
                            '7': "Merged with", # @@@@@@!!!!!
                            '8': "Continued by"}}.get(field.tag).get(field.indicator2, "Related title")
        return {'760': "Main series",
                '762': "Subseries",
                '765': "Translation of",
                '767': "Translated as",
                '770': "Supplement",
                '772': "Supplement to",
                '773': "Component of",
                '775': "Related edition",
                '776': "Also issued as",
                '777': "Issued with",
                '787': "Related title",
                '789': "Related title"}.get(field.tag)

    link_field_w = ('130','510','530','730','760','762','765','767',
        '770','772','773','775','776','777','780','785','787','789','830')
    link_field_0 = ('100','110','111','500','510','511','550','551',
        '555','580','582','600','610','611','650','651','653','655',
        '700','710','711','748','750','751','987')
    def get_linking_info(self, field, element_type):
        """
        Return a string representation of the authorized heading of the record
        the given field refers to, and the record's control number,
        if there is such a record (if not, generate a representation from the field).
        """
        ctrlno, id_subfs = None, None
        # first try looking up the control number given
        if field.tag in self.link_field_w:
            if 'w' in field:
                ctrlno = field['w']
                if not ctrlno.startswith('('):
                    ctrlno = "(CStL)" + ctrlno
                id_subfs = self.ix.reverse_lookup(ctrlno)
            elif '0' in field:
                ctrlno = field['0']
                if field.tag in self.link_field_0 and not ctrlno.startswith('('):
                    ctrlno = "(CStL)" + ctrlno
                id_subfs = self.ix.reverse_lookup(ctrlno)
        elif field.tag in self.link_field_0 and '0' in field:
            ctrlno = field['0']
            if not ctrlno.startswith('('):
                ctrlno = "(CStL)" + ctrlno
            id_subfs = self.ix.reverse_lookup(ctrlno)
        # if that's invalid, look it up based on the field and try again
        if ctrlno is None or id_subfs is None:
            ctrlno = ctrlno or self.ix.lookup(field, element_type)
            id_subfs = self.ix.reverse_lookup(ctrlno)
        # if still invalid, generate "heading" based on this field
        if ctrlno in (Indexer.UNVERIFIED, Indexer.CONFLICT) or id_subfs is None:
            id_from_field = LaneMARCRecord.get_identity_from_field(field, element_type, normalized=False)
            assert id_from_field, f"ID generation failed for field: {field}"
            id_subfs = id_from_field.split(LaneMARCRecord.UNNORMALIZED_SEP)
        # @@@ this part could be altered to use e.g. ISBD punctuation?
        id_repr = ' '.join(filter(None, id_subfs[1::2]))
        return id_repr, ctrlno
