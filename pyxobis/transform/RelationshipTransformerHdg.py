#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from loguru import logger

from pymarc import Field

from pylmldb import LaneMARCRecord
from pylmldb.xobis_constants import *

from ..builders import RelationshipBuilder, WorkRefBuilder

from . import tf_common_methods as tfcm

from .Indexer import Indexer
from .DateTimeParser import DateTimeParser


class RelationshipTransformerHdg:
    """
    Methods for extracting and building Relationship objects from
    holdings pymarc Records.
    """
    def __init__(self, rlt):
        # shared objects and methods from instantiating RelationshipTransformer
        self.get_relation_type = rlt.get_relation_type
        self.build_ref_from_field = rlt.build_ref_from_field
        # self.extract_enumeration = rlt.extract_enumeration

    def transform_relationships(self, record):
        """
        For each field describing a relationship
        in authority LaneMARCRecord record,
        build a Relationship.

        Returns a list of zero or more Relationship objects.
        """

        holdings_type = record.get_holdings_type()

        relationships = []

        # Category Entry (Lane) (R)
        for field in record.get_fields('655'):
            if field.indicator1 in '12':
                rb = RelationshipBuilder()

                # Name/Type
                rel_name = "Category"
                rb.set_name(rel_name)
                rb.set_type(self.get_relation_type(rel_name))

                # Degree
                rb.set_degree({'1': 'primary',
                               '2': 'secondary'}.get(field.indicator1))

                # Enumeration: n/a
                # Chronology: n/a

                # Target
                rb.set_target(self.build_ref_from_field(field, CONCEPT))

                # Notes: n/a

                relationships.append(rb.build())


        # Collection/Location/Call Number (R)
        for field in record.get_fields('852'):
            rb = RelationshipBuilder()

            # Name/Type
            if 'b' not in field:
                logger.warning(f"{record.get_control_number()}: loc code ($b) not found: {field}")
                continue
            loc_code = field['b'].strip(' .').upper()
            rel_name = self.location_code_to_relator_map.get(loc_code, "Access")
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a

            # Enumeration
            # if not digital holdings, h/i are enum on rel to Place, else ignore
            if holdings_type != LaneMARCRecord.DIGITAL:
                # just concat??
                enum = ' '.join(field.get_subfields('h','i')).strip()
                rb.set_enumeration(tfcm.build_simple_ref(enum, STRING) if enum else None)

            # Chronology: n/a

            # Target
            rb.set_target(self.build_ref_from_field(Field('651',' 7',['a',loc_code]), PLACE))

            # Notes
            # map ind 1
            # ...
            # ...
            # ...
            for code, val in field.get_subfields('x','z', with_codes=True):
                rb.add_note(val,
                            role = "annotation" if code == 'x' else "documentation")

            relationships.append(rb.build())

        # Electronic Location And Access (R)
        for field in record.get_fields('856'):
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = field['e'] if 'e' in field else \
                       ("Access" if field.indicator2 in '01' else "Related")
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a
            # Chronology: n/a

            # Notes
            for code, val in field.get_subfields('9','i','r','x', with_codes=True):
                if code == 'x':
                    val = "Date verified: " + val
                rb.add_note(val,
                            role = "annotation" if code in 'irx' else "documentation")

            # Target
            wrb = WorkRefBuilder()

            # field should only have one y or z, but do all just in case.
            link_name = ' '.join(field.get_subfields('y','z')).strip()
            if not link_name:
                link_name = 'Link'
            wrb.add_name(link_name)
            wrb.set_link(link_name,
                         href_URI = field['u'] )

            for val in field.get_subfields('q'):
                # take a guess at the qualifier type
                qualifier_type = Indexer.simple_element_type_from_value(val)
                if qualifier_type is None:
                    qualifier_type = STRING
                wrb.add_qualifier(tfcm.build_simple_ref(val, qualifier_type))

            rb.set_target(wrb.build())

            relationships.append(rb.build())

        # Uniform Title Associated with Version (Lane) (R)
        for field in record.get_fields('963'):
            rb = RelationshipBuilder()

            # Name/Type
            rel_name = "Related uniform title"
            rb.set_name(rel_name)
            rb.set_type(self.get_relation_type(rel_name))

            # Degree: n/a
            # Enumeration: n/a

            # Chronology:
            for val in field.get_subfields('d','f'):
                rb.set_time_or_duration_ref(DateTimeParser.parse_as_ref(val))
            field.delete_all_subfields('d')
            field.delete_all_subfields('f')

            # Notes: n/a

            # these often link to work insts instead of auts, but
            # should be PARSED most similarly to e.g. bib 730 (aut)
            rb.set_target(self.build_ref_from_field(field, WORK_AUT))

            relationships.append(rb.build())

        return relationships

    location_code_to_relator_map = {
        # "ACQ": "???",
        "APER": "Stored",
        "ARAB": "Mediated",
        "ARASZ": "Mediated",
        "ARCH": "Mediated",
        "AV": "Mediated",
        "BOOK": "Mediated",
        "BSP": "Shelved",
        "BSW": "Shelved",
        # "CAT": "???",
        "CDLC": "Mediated",
        # "CDPER": "???",
        "CIRC": "Mediated",
        "COM": "Shelved",
        "COMP": "Access",
        "COR": "Shelved",
        "CRDSK": "Mediated",
        "CRES": "Mediated",
        "DESKCOPY": "Mediated",
        "DTBS": "Access",
        "ECOLL": "Access",
        "ECOMP": "Access",
        "EDATA": "Access",
        "EDOC": "Access",
        "EFEE": "Access",
        "EPER": "Access",
        "EPER1": "Access",
        "EPER2": "Access",
        "EPER3": "Access",
        "EPER4": "Access",
        "EPER5": "Access",
        "EPER6": "Access",
        "EPER7": "Access",
        "EQUIP": "Mediated",
        # "ERQC": "???",
        "FLAT": "Shelved",
        "FOLIO": "Shelved",
        "FOTOF": "Mediated",
        "FPER": "Mediated",
        "FSDOC": "Mediated",
        "FSOFT": "Mediated",
        "FTHSS": "Stored",
        "GRATIS": "Mediated",
        "HIST": "Shelved",
        "HSFLE": "Mediated",
        "IFOAV": "Mediated",
        "IFOEQ": "Mediated",
        "ILLDK": "Mediated",
        "IMAGE": "Access",
        "IMMI": "Access",
        "INCAT": "Mediated",
        "INDEX": "Shelved",
        "INSTR": "Mediated",
        "ISIIF": "Access",
        "LAN": "Shelved",
        "LASER": "Mediated",
        "LC2": "Stored",
        "LECT": "Mediated",
        "LIBR": "Mediated",
        "LKSC": "Mediated",
        "MAP": "Mediated",
        "MICRO": "Shelved",
        "MINI": "Mediated",
        "MISC": "Shelved",
        "MOBI": "Access",
        "MODEL": "Mediated",
        "MSS": "Mediated",
        # "NEWB": "???",
        "NEWS": "Shelved",
        "NLOC": "Access",
        "NOLOC": "Access",
        # "OHIST": "???",
        "OLC": "Mediated",
        "OLD": "Stored",
        "OVPER": "Shelved",
        "OVSZE": "Shelved",
        "PANL": "Access",
        "PARCH": "Mediated",
        "PAV": "Mediated",
        # "PCOMP": "???",
        "PER": "Shelved",
        "PLIBR": "Mediated",
        "PMICR": "Mediated",
        "POLC": "Mediated",
        "PORT": "Mediated",
        "PREF": "Shelved",
        # "PRES": "???",
        "PROLC": "Mediated",
        "PRREF": "Shelved",
        # "PRSV": "???",
        "PSPEC": "Mediated",
        "PTS": "Mediated",
        "QUERY": "Mediated",
        "REF": "Shelved",
        # "REFREV": "???",
        # "RES": "???",
        # "REVIEW": "???",
        "RFDSK": "Mediated",
        "RFFLE": "Mediated",
        "RLIN": "Mediated",
        "RLOC": "Access",
        "ROLC": "Shelved",
        "RREF": "Shelved",
        "RREF2": "Stored",
        "RTHSS": "Mediated",
        "SAL3": "Stored",
        "SAL3X": "Mediated",
        # "SC1": "???",
        "SCAN": "Mediated",
        "SDOC": "Mediated",
        # "SELF": "???",
        "SERIES": "Shelved",
        "SFLAT": "Mediated",
        "SFOL": "Mediated",
        "SIMUL": "Mediated",
        "SKKAT": "Mediated",
        "SOFT": "Mediated",
        "SOMCC": "Shelved",
        "SPAV": "Mediated",
        "SPEC": "Mediated",
        "SPLCO": "Mediated",
        "SPOLD": "Mediated",
        "SPOO1": "Mediated",
        "SPOO2": "Mediated",
        "SPOO3": "Mediated",
        "SREF": "Mediated",
        "STEAM": "Stored",
        "STOR": "Stored",
        "STRG": "Mediated",
        "SUL": "Access",
        "TELBK": "Mediated",
        # "TEST": "???",
        "THSS": "Stored",
        "TS": "Mediated",
        "WKSTA": "Mediated",
        "WKSTB": "Mediated",
        "WKSTC": "Mediated",
        "WKSTD": "Mediated",
        "WKSTE": "Mediated"
    }
