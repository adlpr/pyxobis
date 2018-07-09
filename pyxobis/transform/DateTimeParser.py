#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pyxobis.builders import *
from .LaneMARCRecord import LaneMARCRecord
from .Indexer import Indexer
from .tf_being import *
from .tf_common import *


class DateTimeParser:
    def __init__(self, element_type=BEING):
        self.ix = Indexer()
        self.set_element_type(element_type)

    def set_element_type(self, element_type):
        """
        Element type that the datetime pertains to
        (sets defaults: Born/Died vs Began/Ended etc.).
        """
        self.element_type = element_type

    def parse(self, datestring):
        """
        Parse out a time or duration string into a Time or Duration ref element.
        """
        # Various preprocessing normalization
        # Punctuation
        dts = datestring.rstrip('.,: ').strip('() ').strip()
        dts = re.sub(r"[\u200c-\u200f]", "", dts)
        # Arabic
        dts = re.sub(r"حو(الي|\.?) +", "approximately ", dts).replace('؟','?')
        dts = re.sub(r"ت(وفي|\.) +", "died ", dts)
        dts = re.sub(r" +[اأ]و +", " or ", dts)
        dts = re.sub(r"إزدهر +", "active ", dts)
        dts = re.sub(r"هـ", "AH", dts)
        for i,d in enumerate('٠١٢٣٤٥٦٧٨٩'):
            dts = dts.replace(d,str(i))

        # Hebrew
        m = re.search(r"(\d{4})־(\d{4})", dts)
        # flip dates entered in reverse
        if m and int(m.group(1)) > int(m.group(2)):
            dts = re.sub(r"(\d{4})־(\d{4})", r"\2-\1", dts)
        dts = re.sub(r"־", "-", dts)
        dts = re.sub(r"נפ?[׳'] +", "died ", dts)
        dts = re.sub(r" +או +", " or ", dts)

        # BEING-SPECIFIC PARSING
        type_kwargs = {}

        if self.element_type == BEING:
            # If this is an "active" date, make that the Type for all Contents.
            if re.match(r"(active|fl?(\.| ))", dts, flags=re.I):
                dts = re.sub(r"^(active|fl?\.?)\s*", '', dts, flags=re.I).strip()
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
        elif self.element_type == ORGANIZATION:
            ...
            ...
            ...
        elif self.element_type == EVENT:
            ...
            ...
            ...
        elif self.element_type == OBJECT:
            ...
            ...
            ...

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

            # !!!!!!!!!!! A single Time ref doesn't allow for double dates??
            trb.set_time_entry_content(time_content1)

            # LINK
            # try to look it up in the index
            if time_content2 is None:
                # print(str(time_content1))
                self.ix.quick_lookup(date, TIME)
                ...
                ...

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

            # Blank dates
            if date2 and not date1: date1 = "Unknown"
            if date1 and not date2: date2 = "Present"

            if date1.isdigit() and date2.isdigit():
                if int(date1) > int(date2):
                    print("\nPROBLEM: {} > {}".format(date1, date2))

            if type_kwargs:
                start_type_kwargs = end_type_kwargs = type_kwargs
            else:
                start_type_kwargs = { 'link_title' : "Born",
                    'role_URI' : self.ix.quick_lookup("Time Type", CONCEPT),
                    'href_URI' : self.ix.quick_lookup("Born", RELATIONSHIP) }
                end_type_kwargs = { 'link_title' : "Died",
                    'role_URI' : self.ix.quick_lookup("Time Type", CONCEPT),
                    'href_URI' : self.ix.quick_lookup("Died", RELATIONSHIP) } \
                    if date2 not in ["Unknown","Present"] else {}

            # parse further for potential double dates
            time_content_s1, time_content_s2 = self.__parse_for_double_date(date1, start_type_kwargs)
            time_content_e1, time_content_e2 = self.__parse_for_double_date(date2, end_type_kwargs)

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
            return self.__parse_single_datetime_to_time_entry(date1.strip()+'?', type_kwargs),  \
                   self.__parse_single_datetime_to_time_entry(date2.strip()+'?', type_kwargs)
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
        if re.match(r"\[.*\]$", dts):
            dts = re.sub(r"(^\[|\]$)", "", dts).strip()
            certainty = "implied"
        # `estimated` -- takes precedence over `implied`: [2018?] = estimated 2018
        if re.match(r".+\?+$", dts):
            dts = re.sub(r"\?+$", "", dts).strip()
            certainty = "estimated"
        # `approximate` -- highest precedence
        if re.match(r"approx", dts, flags=re.I):
            dts = re.sub(r"^approx(imate(ly)?|\.)?", "", dts, flags=re.I).strip()
            certainty = "approximate"
        tecb.set_certainty(certainty)

        # BC(E)
        if re.search(r" +B\.?C\.?E?\.?$", dts, flags=re.I):
            dts = '-' + re.sub(r" +B\.?C\.?E?\.?$", "", dts, flags=re.I).strip()

        # synonyms for "Unknown"
        dts = re.sub(r"(yyyy|uuuu)", "Unknown", dts, flags=re.I)

        # convert month names
        dts = re.sub(r" +jan(uary|\.)? +",  "-01-", dts, flags=re.I)
        dts = re.sub(r" +feb(ruary|\.)? +", "-02-", dts, flags=re.I)
        dts = re.sub(r" +mar(ch|\.)? +",    "-03-", dts, flags=re.I)
        dts = re.sub(r" +apr(il|\.)? +",    "-04-", dts, flags=re.I)
        dts = re.sub(r" +may +",         "-05-", dts, flags=re.I)
        dts = re.sub(r" +jun[e\.]? +",       "-06-", dts, flags=re.I)
        dts = re.sub(r" +jul[y\.]? +",       "-07-", dts, flags=re.I)
        dts = re.sub(r" +aug(ust|\.)? +",   "-08-", dts, flags=re.I)
        dts = re.sub(r" +sep(t(ember|\.)?|\.)? +", "-09-", dts, flags=re.I)
        dts = re.sub(r" +oct(ober|\.)? +",  "-10-", dts, flags=re.I)
        dts = re.sub(r" +nov(ember|\.)? +", "-11-", dts, flags=re.I)
        dts = re.sub(r" +dec(ember|\.)? +", "-12-", dts, flags=re.I)

        # make sure year is zero padded
        m = re.match(r"^(-?)(\d{1,3})(?:-|$)", dts)
        if m: dts = re.sub(r"^(-?)(\d{1,3})(-|$)", r"\g<1>"+m.group(2).zfill(4)+r"\g<3>", dts)
        # make sure DOTM is zero padded
        dts = re.sub(r"(\-\d\d\-)(\d(?:[^\d]|$))", r"\g<1>0\g<2>", dts, flags=re.I)

        # try to parse dts as ISO 8601, otherwise treat as a name
        time_kwargs = self.__parse_as_iso_datetime(dts)
        if time_kwargs:
            tecb.set_time_contents(**time_kwargs)
        else:
            tecb.add_name(dts)

        return tecb.build()


    def __parse_as_iso_datetime(self, datestring):
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
