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
        # Record types = subsets = 655 77 fields.
        for field in record.get_fields('655'):
            if field.indicator1 == '7':
                title, href = field['a'], field['0']
                if not href:
                    href = self.ix.quick_lookup(title, CONCEPT)
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


    def parse_date(self, datestring):
        """
        Parse out a time or duration string into a Time or Duration ref element.
        """
        # Various preprocessing normalization
        # Punctuation
        dts = datestring.rstrip('., ').strip('() ').strip()
        # Arabic
        dts = re.sub(r"حو(الي|\.) +", "approximately ", dts).replace('؟','?')
        for i,d in enumerate('٠١٢٣٤٥٦٧٨٩'):
            dts = dts.replace(d,str(i))

        # If this is an "active" date, make that the Type for all Contents.
        type_kwargs = {}
        if dts.lower().startswith('active'):
            dts = re.sub(r"^active\s*", '', dts, flags=re.I).strip()
            type_kwargs = { 'link_title' : "Active",
                            'role_URI'   : self.ix.quick_lookup("Time Type", CONCEPT),
                            'href_URI'   : self.ix.quick_lookup("Active", RELATIONSHIP) }

        # Test for born/died and add appropriate other half.
        if re.match(r"b(orn |\. ?|\.? )", dts):
            # "Born" date --> Died Unknown;
            dts = re.sub(r"^b(orn |\. ?|\.? )", '', dts).strip() + '-Unknown'
        elif re.match(r"d(ied |\. ?|\.? )", dts):
            # "Died" date --> Born Unknown.
            dts = 'Unknown-' + re.sub(r"^d(ied |\. ?|\.? )", '', dts).strip()

        # "AD" should only be dates that span from BC to AD, so not needed.
        dts = re.sub(r"\s+A\.?D", "", dts).strip()

        # Attempt to split dates at an appropriate hyphen; should result in 1-2.
        split_dates = re.split(r'-(?!\d\d(?:[\-\.]|$))', dts)

        if len(split_dates) == 1:
            # This should be a TimeRef.
            trb = TimeRefBuilder()

            # CALENDAR
            # right now the only calendar supported is Gregorian
            # trb.set_calendar("Calendar, Gregorian")

            # TIME ENTRIES
            date = split_dates[0]
            time_content1, time_content2 = self.__parse_for_double_date(date, type_kwargs)

            print("time:")
            print(time_content1)
            print(time_content2)
            print()

            # LINK
            # try to look it up in the index
            if time_content2 is None:
                # print(str(time_content1))
                # self.ix.
                ...

            return None
            return trb.build()

        elif len(split_dates) == 2:
            # This should be a DurationRef.
            drb = DurationRefBuilder()

            # CALENDAR
            # right now the only calendar supported is Gregorian
            # drb.set_calendar("Calendar, Gregorian")

            # TIME ENTRIES
            # if there are no type_kwargs (Active dates) already,
            # start is Born and end is Died
            date1, date2 = split_dates

            if type_kwargs:
                start_type_kwargs = end_type_kwargs = type_kwargs
            else:
                start_type_kwargs = { 'link_title' : "Born",
                    'role_URI' : self.ix.quick_lookup("Time Type", CONCEPT),
                    'href_URI' : self.ix.quick_lookup("Born", RELATIONSHIP) }
                end_type_kwargs = { 'link_title' : "Died",
                    'role_URI' : self.ix.quick_lookup("Time Type", CONCEPT),
                    'href_URI' : self.ix.quick_lookup("Died", RELATIONSHIP) }

            # parse further for potential double dates
            time_content_s1, time_content_s2 = self.__parse_for_double_date(date1, start_type_kwargs)
            time_content_e1, time_content_e2 = self.__parse_for_double_date(date2, end_type_kwargs)

            print("duration:")
            print(time_content_s1)
            print(time_content_s2)
            print(time_content_e1)
            print(time_content_e2)
            print()

            drb.set_time_entry1(time_content_s1, time_content_s2)
            drb.set_time_entry2(time_content_e1, time_content_e2)

            # LINK
            # Doesn't make sense here, unless this is a named Duration (?);
            # these are decades centuries etc? but those wouldn't be used in Beings.
            # not sure how to look this up in that case...

            return drb.build()

        else:
            # Did not split as expected...
            raise ValueError("problem parsing date: {}".format(datestring))


    def __parse_for_double_date(self, datestring, type_kwargs):
        # double dates might be separated with a slash:
        dts_split_slash = datestring.split('/')
        if len(dts_split_slash) == 2:
            # good! now parse each of these
            date1, date2 = dts_split_slash
            return self.__parse_single_datetime_to_time_entry(date1.strip(), type_kwargs),  \
                   self.__parse_single_datetime_to_time_entry(date2.strip(), type_kwargs)
        elif len(dts_split_slash) > 2:
            raise ValueError("problem parsing date: {}".format(datestring))

        # or, they might be separated with "or",
        # in which case they're both "estimated" dates
        dts_split_or = re.split(r" +or +", datestring)
        if len(dts_split_or) == 2:
            # good! now parse each of these
            date1, date2 = dts_split_or
            return self.__parse_single_datetime_to_time_entry(date1.strip(), type_kwargs),  \
                   self.__parse_single_datetime_to_time_entry(date2.strip(), type_kwargs)
        elif len(dts_split_or) > 2:
            raise ValueError("problem parsing date: {}".format(datestring))

        # not a double date
        return self.__parse_single_datetime_to_time_entry(datestring, type_kwargs), None


    def __parse_single_datetime_to_time_entry(self, datestring, type_kwargs):
        """
        Parses a single date string (preprocessed by parse_date > __parse_for_double_date)
        into a TimeEntryContent object.
        """
        tecb = TimeEntryContentBuilder()

        # TYPE: Active/Born/Died
        if type_kwargs:
            tecb.set_type(**type_kwargs)

        # CERTAINTY:
        dts = datestring
        # `exact`
        certainty = "exact"
        # `implied`
        if re.match(r"\[[\d-]+\]$", dts):
            dts = re.sub(r"\[([\d-]+)\]", r"\1", dts).strip()
            certainty = "implied"
        # `estimated` -- takes precedence over `implied`: [2018?] = estimated 2018

        # `approximate` --
        tecb.set_certainty(certainty)
        print(certainty)

        # BC(E)
        if re.search(r" +B\.?C\.?E?\.?$", dts):
            dts = '-' + re.sub(r" +B\.?C\.?E?\.?$", "", dts).strip()

        # NAME or CONTENTS
        # try to parse dts as ISO 8601, otherwise treat as a name
        time_kwargs = self.__parse_as_iso_8601(dts)
        if time_kwargs:
            tecb.set_time_contents(**time_kwargs)
        else:
            tecb.add_name(dts)

        return tecb.build()


    def __parse_as_iso_8601(self, datestring):
        """
        Attempt to parse (partial or full) ISO datetime string into kwarg dict
        """
        time_kwargs = {}
        m = re.match(r"^(?:(-?\d\d\d\d)(?:-(\d\d)(?:-(\d\d))?)?(?:T(\d\d)(?::(\d\d)(?::(\d\d)(?:([\+\-]\d\d)(?::(\d\d)(?::\d\d)?)?|(Z))?)?)?)?)$", datestring)

        # no match, return empty dict
        if not m:
            return time_kwargs

        # keyword for each group
        for i,kw in enumerate(('year','month','day','hour','minute','second','tz_hour','tz_minute')):
            if m.group(i+1):
                time_kwargs[kw] = int(m.group(i+1))

        # time zone zulu = GMT
        if m.group(9):
            time_kwargs['tz_hour'] = time_kwargs['tz_minute'] = 0

        return time_kwargs


    def parse_name(self, name):
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

        orb.set_link("Lane Medical Library", "Z1584")
        orb.add_name("Lane Medical Library", 'eng')
        return orb.build()
