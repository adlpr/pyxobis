#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pyxobis.builders import *
from .Indexer import Indexer
from .tf_common import *

# Default starting and ending Time Types by PE type
DEFAULT_TIME_TYPES = {
    None  : ("",""),
    BEING : ("Born", "Died"),
    EVENT : ("Began", "Ended"),
    ORGANIZATION : ("Began", "Ended"),
    WORK_AUT  : ("", ""),  # ??
    WORK_INST : ("", ""),  # ??
    # OBJECT : ("Created", "Destroyed"),
}

class DateTimeParser:
    def __init__(self):
        self.__set_default_type_kwargs()

    ix = Indexer()

    def parse_simple(self, datestring, type_kwargs=None):
        """
        Parse out a date value taken from an X50 field into a TimeContentSingle object.
        """
        tecb = TimeContentSingleBuilder()

        # TYPE: none

        # CERTAINTY
        # none on headings?
        # tecb.set_certainty("exact")

        # QUALITY
        # none on headings?

        # contents or name?
        time_kwargs = self.__parse_as_iso_datetime(datestring)
        if time_kwargs:
            tecb.set_time_contents(**time_kwargs)
        else:
            tecb.add_name(datestring)

        return tecb.build()

    def parse_as_ref(self, datestring, element_type=None, default_start_type=None, default_end_type=None):
        """
        Parse out a time or duration string into a Time or Duration ref element.
        """
        # Various preprocessing normalization
        # Punctuation
        dts = datestring.strip('.,: ').strip('() ').strip()
        if not dts:
            return None
        dts = re.sub(r"([\d\-s]+)~", r"approximately \1", dts)
        dts = re.sub(r"[\u200c-\u200f]", "", dts)
        # Arabic
        dts = re.sub(r"(حو(الي|\.?)|نحو) +", "approximately ", dts).replace('؟','?')
        dts = re.sub(r"ت(وفي|\.) +", "died ", dts)
        dts = re.sub(r" +[اأ]و +", " or ", dts)
        dts = re.sub(r"إزدهر +", "active ", dts)
        dts = re.sub(r"هـ", "AH", dts)
        dts = re.sub(r"\s+م([\s\.]+|$)", "", dts)  # abbr of تقويم ميلادي
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

        # --------
        # ELEMENT-SPECIFIC PARSING
        # --------
        type_kwargs = {}

        if element_type == BEING:
            # If this is an "active" date, make that the Type for all Contents.
            if re.match(r"(active|fl?(\.| ))", dts, flags=re.I):
                dts = re.sub(r"^(active|fl?\.?)\s*", '', dts, flags=re.I).strip()
                type_kwargs = self.__type_string_to_kwargs("Active")
            # Test for born/died and add appropriate other half.
            elif re.match(r"b(orn |\. ?|\.? )", dts):
                # "Born" date --> Died Unknown;
                dts = re.sub(r"^b(orn |\. ?|\.? )", '', dts).strip() + '-Unknown'
            elif re.match(r"d(ied |\. ?|\.? )", dts):
                # "Died" date --> Born Unknown.
                dts = 'Unknown-' + re.sub(r"^d(ied |\. ?|\.? )", '', dts).strip()
        # elif element_type == OBJECT:
        #     ...
        #     ...
        #     ...
        # elif element_type == ORGANIZATION:
        #     ...
        #     ...
        #     ...
        # elif element_type == EVENT:
        #     ...
        #     ...
        #     ...

        # calendar indication on ranges:
        # copy calendar indicators over.
        dts = re.sub(r"^([\d\-]+)-([\d\-]+) ([^\d ]+)$", r"\1 \3-\2 \3", dts)

        # --------
        # SPLIT
        # --------
        # Attempt to split dates at an appropriate hyphen; should result in 1-2.
        split_dates = re.split(r'-(?!\d\d(?:[\-\.]|[\?~]?$))', dts)

        if len(split_dates) == 1:
            # This should be a TimeRef.
            trb = TimeRefBuilder()

            date = split_dates[0]

            # CALENDAR
            calendar_kwargs, date = self.extract_calendar(date)
            if calendar_kwargs:
                trb.set_calendar(**calendar_kwargs)

            # TIME ENTRIES
            time_content1, time_content2 = self.__parse_for_double(date, type_kwargs)

            trb.set_time_content(time_content1, time_content2)

            # LINK
            if time_content2 is None:
                time_content_str = str(time_content1)
                trb.set_link(time_content_str, self.ix.simple_lookup(time_content_str, TIME))

            return trb.build()

        elif len(split_dates) == 2:
            # This should be a DurationRef.
            drb = DurationRefBuilder()

            date1, date2 = split_dates

            # CALENDAR(S)
            calendar_kwargs1, date1 = self.extract_calendar(date1)
            if calendar_kwargs1:
                trb.set_calendar1(**calendar_kwargs1)
            calendar_kwargs2, date2 = self.extract_calendar(date2)
            if calendar_kwargs2:
                drb.set_calendar2(**calendar_kwargs2)

            # TIME ENTRIES
            # Blank dates
            if date2 and not date1: date1 = "Unknown"
            if date1 and not date2: date2 = "Present"

            date1, date2 = self.__resolve_abbreviation(date1, date2)

            if type_kwargs:
                start_type_kwargs = end_type_kwargs = type_kwargs
            else:
                start_type_kwargs, end_type_kwargs = self.default_type_kwargs[element_type]
                # defaults given as arguments override the defaults by element
                if default_start_type:
                    start_type_kwargs = self.__type_string_to_kwargs(default_start_type)
                if default_end_type:
                    end_type_kwargs = self.__type_string_to_kwargs(default_end_type)
                elif date2 in ["Unknown","Present"]:
                    end_type_kwargs = {}

            # parse further for potential double dates
            time_content_single_s1, time_content_single_s2 = self.__parse_for_double(date1, start_type_kwargs)
            time_content_single_e1, time_content_single_e2 = self.__parse_for_double(date2, end_type_kwargs)

            drb.set_time_content1(time_content_single_s1, time_content_single_s2)
            drb.set_time_content2(time_content_single_e1, time_content_single_e2)

            # LINKS
            # Main Duration link only makes sense for a named Duration
            # (decades centuries etc.?? wouldnt that just be a Time??);
            # wouldn't be used here, but individual TimeContents can have links

            if time_content_single_s2 is None:
                time_content_single_s1_str = str(time_content_single_s1)
                drb.set_time_content1_link(time_content_single_s1_str, self.ix.simple_lookup(time_content_single_s1_str, TIME))
            if time_content_single_e2 is None:
                time_content_single_e1_str = str(time_content_single_e1)
                drb.set_time_content2_link(time_content_single_e1_str, self.ix.simple_lookup(time_content_single_e1_str, TIME))

            return drb.build()

        else:
            # Did not split as expected
            raise ValueError("problem parsing date: {}".format(datestring))


    def __parse_for_double(self, datestring, type_kwargs):
        # double dates might be separated with a slash:
        dts_split_slash = datestring.split('/')
        if len(dts_split_slash) == 2:
            # good! now parse each of these
            date1, date2 = self.__resolve_abbreviation(*dts_split_slash)
            return self.__parse_single(date1.strip(), type_kwargs),  \
                   self.__parse_single(date2.strip(), type_kwargs)
        elif len(dts_split_slash) > 2:
            raise ValueError("problem parsing date: {}".format(datestring))

        # or, they might be separated with "or",
        # in which case they're both "estimated" dates
        dts_split_or = re.split(r" +or +", datestring)
        if len(dts_split_or) == 2:
            # good! now parse each of these
            date1, date2 = self.__resolve_abbreviation(*dts_split_or)
            return self.__parse_single(date1.strip()+'?', type_kwargs),  \
                   self.__parse_single(date2.strip()+'?', type_kwargs)
        elif len(dts_split_or) > 2:
            raise ValueError("problem parsing date: {}".format(datestring))

        # not a double date
        return self.__parse_single(datestring, type_kwargs), None


    def __resolve_abbreviation(self, date1, date2):
        """
        Resolves cases of second-element abbreviation such as "1996/7",
        "851-73", etc.
        """
        if date1.lstrip('-').isdigit() and date2.lstrip('-').isdigit():
            if len(date1) > len(date2) and int(date1) > int(date2):
                date2 = date1[:-len(date2)] + date2
        return date1, date2


    def extract_calendar(self, datestring):
        """
        Input: Datetime string
        Output: 1) Calendar as kwargs if applicable; None otherwise
                2) Datetime string stripped of calendar indicator
        """
        # calendar = "Calendar, Gregorian"
        calendar = ""
        if re.search(r" A\.?H\.?$", datestring):
            datestring = re.sub(r" A\.?H\.?$", "", datestring).strip()
            calendar = "Calendar, Islamic"
        elif re.search(r"^F\.?R\.?\s+", datestring):
            datestring = re.sub(r"^F\.?R\.?\s+", "", datestring).strip()
            calendar = "Calendar, French Revolutionary"

        calendar_kwargs = {
            'link_title' : calendar,
            'set_URI'    : self.ix.simple_lookup("Calendars", CONCEPT),
            'href_URI'   : self.ix.simple_lookup(calendar, CONCEPT)
            } if calendar else None

        return calendar_kwargs, datestring


    def __parse_single(self, datestring, type_kwargs):
        """
        Parses a single date string (preprocessed by parse_date > __parse_for_double)
        into a TimeContentSingle object.
        """
        tecb = TimeContentSingleBuilder()

        # TYPE: Active/Born/Died
        if type_kwargs:
            tecb.set_type(**type_kwargs)

        # CERTAINTY
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
        if re.match(r"c(irca|\.)", dts, flags=re.I):
            dts = re.sub(r"^c(irca|\.) +", "", dts, flags=re.I).strip()
            certainty = "approximate"
        if dts.endswith('~'):
            dts = dts.rstrip('~').strip()
            certainty = "approximate"
        tecb.set_certainty(certainty)

        # QUALITY
        quality = ""
        for quality_candidate in ["before", "after", "early", "mid", "late"]:
            if re.match(r"^{}\s*".format(quality_candidate), dts, flags=re.I):
                dts = re.sub(r"^{}\s*".format(quality_candidate), "", dts, flags=re.I)
                quality += " {}".format(quality_candidate)
        if quality:
            tecb.set_quality(quality.strip())

        # Other string normalization:
        # "AD" should only be dates that span from BC to AD, so not needed.
        dts = re.sub(r"(^A\.?D\.?\s+|\s+A\.?D\.?$)", "", dts).strip()
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
        dts = re.sub(r" +may +",            "-05-", dts, flags=re.I)
        dts = re.sub(r" +jun[e\.]? +",      "-06-", dts, flags=re.I)
        dts = re.sub(r" +jul[y\.]? +",      "-07-", dts, flags=re.I)
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

        # if dts is blank at this point, there's an issue
        # decided to ignore and return nothing
        if not dts:
            # raise ValueError("attempt to parse blank datestring")
            return None

        # FINALLY: try to parse dts as ISO 8601, otherwise treat as a name
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


    def __type_string_to_kwargs(self, type_string):
        return { 'link_title' : type_string,
                 'set_URI'  : self.ix.simple_lookup("Time Type", CONCEPT),
                 'href_URI' : self.ix.simple_lookup(type_string, RELATIONSHIP) }  \
               if type_string else {}


    def __set_default_type_kwargs(self):
        # turn global into full map
        self.default_type_kwargs = {
            element_type : (
                self.__type_string_to_kwargs(time_types[0]),
                self.__type_string_to_kwargs(time_types[1])
            ) for element_type, time_types in DEFAULT_TIME_TYPES.items()
        }
        self.default_type_kwargs[ORGANIZATION] = self.default_type_kwargs[EVENT]
