#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pyxobis.builders import *
from .LaneMARCRecord import LaneMARCRecord
from .Indexer import Indexer
from .tf_being import *
from .tf_common import *


class Transformer:
    def __init__(self):
        self.lane_org_ref = self.__build_lane_org_ref()
        self.ix = Indexer()

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

        # -------
        # TYPES
        # -------
        # = Subsets = 655 77 fields.
        # NB: "Record Type" (Z47381) actually refers to which PE a record is
        for field in record.get_fields('655'):
            if field.indicator1 == '7':
                title = field['a']
                href = field['0'] or self.ix.quick_lookup(title, CONCEPT)
                rb.add_type(title,
                            xlink_href = href,
                            xlink_role = self.ix.quick_lookup("Subset", CONCEPT))

        # -------
        # ACTIONS
        # -------
        # Metametadata (from fields that are to be inserted by RIM?)...
        # Action Types
        # created; modified;
        ...
        ...
        ...

        # -------------
        # PRINCIPAL ELEMENT
        # -------------
        # Determine which function to delegate PE building based on record type

        element_type = record.get_xobis_element_type()
        if not element_type:
            # don't transform
            return None
        assert element_type, "could not determine type of record {}".format(record['001'].data)

        transform_function = { WORK_INST    : self.transform_work_instance,
                               WORK_AUT     : self.transform_work_authority,
                               BEING        : self.transform_being,
                               CONCEPT      : self.transform_concept,
                               EVENT        : self.transform_event,
                               LANGUAGE     : self.transform_language,
                               OBJECT       : self.transform_object,
                               ORGANIZATION : self.transform_organization,
                               PLACE        : self.transform_place,
                               TIME         : self.transform_time,
                               STRING       : self.transform_string,
                               RELATIONSHIP : self.transform_relationship,
                               HOLDINGS     : self.transform_holdings }.get(element_type)

        principal_element = transform_function(record)

        if transform_function == transform_being:
            return principal_element

        rb.set_principal_element(principal_element)

        # -------------
        # RELATIONSHIPS
        # -------------

        # ...

        return None

    def parse_being_name(self, name):
        """
        Parse out a Being name from a X00 into a list of labeled name parts.
        """
        name = name.rstrip(', ')
        ...
        ...
        ...
        ...
        return name



    # bring imported methods into class scope
    transform_being = transform_being

    def transform_work_instance(self, record):
        return None

    def transform_object(self, record):
        return None

    def transform_organization(self, record):
        return None

    def transform_event(self, record):
        return None

    def transform_work_authority(self, record):
        return None

    def transform_concept(self, record):
        return None

    def transform_language(self, record):
        return None

    def transform_time(self, record):
        return None

    def transform_place(self, record):
        return None

    def transform_string(self, record):
        return None

    def transform_relationship(self, record):
        return None

    def transform_holdings(self, record):
        return None

    def __build_lane_org_ref(self):
        orb = OrganizationRefBuilder()
        orb.set_link("Lane Medical Library",
                     "Z1584")
        orb.add_name("Lane Medical Library", 'eng')
        return orb.build()