#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import regex as re
from pyxobis.builders import *
from .Indexer import Indexer
from .tf_common import *

# Default starting and ending Time Types by PE type
DEFAULT_TIME_TYPES = {
    None  : ("", ""),
    BEING : ("Born", "Died"),
    EVENT : ("Began", "Ended"),
    # ORGANIZATION : ("Began", "Ended"),
    # WORK_AUT  : ("", ""),
    # WORK_INST : ("", ""),
    # OBJECT : ("Created", "Destroyed"),  # ??
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
        # Misc preprocessing
        # print("start", datestring)

        """
        [between 1401 and 1425?]	1
        [between 1401 and 1450]	1
        [between 1401 and 425?]	1
        [between 1451 and 1500]	3
        [between 1451-1500]	1
        [between 1476 and 1500]	10
        [between 1501 and 1525]	4
        [between 1551 and 1554]	1
        [between 880 and 898?]	391

        anything DD month YYYY

        2019 Aug 2-10

        1943 September-
        """

        # Punctuation / control chars
        dts = re.sub(r'^\((.*)\)$', r'\1', datestring.strip('.,:; ').strip()).strip()
        if not dts:
            return None
        dts = re.sub(r"([\d\-s]+)~", r"approximately \1", dts)
        # dts = re.sub(r" +cent( |$)", r" century\1", dts)
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

        # print("punct", dts)

        # single digit days
        dts = re.sub(r"(^|[ \-])([\w\.]+) (\d)(\D|$)",  r"\1\2 0\3\4", dts, flags=re.I)
        dts = re.sub(r"(^|[ \-])(\d) ([\w\.]+)([ \-]|$)",  r"\1\3 0\2\4", dts, flags=re.I)

        # abbreviated ranges that could be misparsed as YYYY-MM e.g. 1875-76
        m = re.search(r"(\d{1,2})(\d{2}-)(\d{2})(\D|$)", dts)
        if m and int(m.group(3)) > 12:
            # potential problem here if multiple instances
            dts = dts.replace(m.group(0), m.group(1)+m.group(2)+m.group(1)+m.group(3)+m.group(4))

        # English
        # DD Month YYYY
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(jan(?:\.|uary)?,?) (\d{3,4})(\D|$)",  r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(feb(?:\.|ruary)?,?) (\d{3,4})(\D|$)", r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(mar(?:\.|ch)?,?) (\d{3,4})(\D|$)",    r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(apr(?:\.|il)?,?) (\d{3,4})(\D|$)",    r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(may) (\d{3,4})(\D|$)",                r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(jun[\.e]?,?) (\d{3,4})(\D|$)",        r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(jul[\.y]?,?) (\d{3,4})(\D|$)",           r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(aug(?:\.|ust)?,?) (\d{3,4})(\D|$)",      r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(sep(?:[t\.]|t\.|tember)?,?) (\d{3,4})(\D|$)", r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(oct(?:\.|ober)?,?) (\d{3,4})(\D|$)",     r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(nov(?:\.|ember)?,?) (\d{3,4})(\D|$)",    r"\1\3 \2 \4\5", dts, flags=re.I)
        dts = re.sub(r"(^|\D)((\d\d?-)?\d\d?) *(dec(?:\.|ember)?,?) (\d{3,4})(\D|$)",    r"\1\3 \2 \4\5", dts, flags=re.I)
        # YYYY Month DD
        dts = re.sub(r"(\d{3,4}) *jan(?:\.|uary)?,? (\d\d?)",  r"\1-01-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *feb(?:\.|ruary)?,? (\d\d?)", r"\1-02-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *mar(?:\.|ch)?,? (\d\d?)",    r"\1-03-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *apr(?:\.|il)?,? (\d\d?)",    r"\1-04-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *may (\d\d?)",                r"\1-05-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *jun[\.e]?,? (\d\d?)",        r"\1-06-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *jul[\.y]?,? (\d\d?)",           r"\1-07-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *aug(?:\.|ust)?,? (\d\d?)",      r"\1-08-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *sep(?:[t\.]|t\.|tember)?,? (\d\d?)", r"\1-09-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *oct(?:\.|ober)?,? (\d\d?)",     r"\1-10-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *nov(?:\.|ember)?,? (\d\d?)",    r"\1-11-\2", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) *dec(?:\.|ember)?,? (\d\d?)",    r"\1-12-\2", dts, flags=re.I)
        # Month DD, YYYY
        dts = re.sub(r"jan(?:\.|uary)? (\d\d?),? (\d{3,4})",  r"\2-01-\1", dts, flags=re.I)
        dts = re.sub(r"feb(?:\.|ruary)? (\d\d?),? (\d{3,4})", r"\2-02-\1", dts, flags=re.I)
        dts = re.sub(r"mar(?:\.|ch)? (\d\d?),? (\d{3,4})",    r"\2-03-\1", dts, flags=re.I)
        dts = re.sub(r"apr(?:\.|il)? (\d\d?),? (\d{3,4})",    r"\2-04-\1", dts, flags=re.I)
        dts = re.sub(r"may (\d\d?),? (\d{3,4})",              r"\2-05-\1", dts, flags=re.I)
        dts = re.sub(r"jun[\.e]? (\d\d?),? (\d{3,4})",        r"\2-06-\1", dts, flags=re.I)
        dts = re.sub(r"jul[\.y]? (\d\d?),? (\d{3,4})",           r"\2-07-\1", dts, flags=re.I)
        dts = re.sub(r"aug(?:\.|ust)? (\d\d?),? (\d{3,4})",      r"\2-08-\1", dts, flags=re.I)
        dts = re.sub(r"sep(?:[t\.]|t\.|tember)? (\d\d?),? (\d{3,4})", r"\2-09-\1", dts, flags=re.I)
        dts = re.sub(r"oct(?:\.|ober)? (\d\d?),? (\d{3,4})",     r"\2-10-\1", dts, flags=re.I)
        dts = re.sub(r"nov(?:\.|ember)? (\d\d?),? (\d{3,4})",    r"\2-11-\1", dts, flags=re.I)
        dts = re.sub(r"dec(?:\.|ember)? (\d\d?),? (\d{3,4})",    r"\2-12-\1", dts, flags=re.I)
        # YYYY Month
        dts = re.sub(r"(\d{3,4}) jan(?:\.|uary)?",  r"\1-01", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) feb(?:\.|ruary)?", r"\1-02", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) mar(?:\.|ch)?",    r"\1-03", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) apr(?:\.|il)?",    r"\1-04", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) may",              r"\1-05", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) jun[\.e]?",        r"\1-06", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) jul[\.y]?",           r"\1-07", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) aug(?:\.|ust)?",      r"\1-08", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) sep(?:[t\.]|t\.|tember)?", r"\1-09", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) oct(?:\.|ober)?",     r"\1-10", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) nov(?:\.|ember)?",    r"\1-11", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}) dec(?:\.|ember)?",    r"\1-12", dts, flags=re.I)
        # YYYY Month[-/]Month
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])jan(?:\.|uary)?",  r"\1\2\g<1>01", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])feb(?:\.|ruary)?", r"\1\2\g<1>02", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])mar(?:\.|ch)?",    r"\1\2\g<1>03", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])apr(?:\.|il)?",    r"\1\2\g<1>04", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])may",              r"\1\2\g<1>05", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])jun[\.e]?",        r"\1\2\g<1>06", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])jul[\.y]?",           r"\1\2\g<1>07", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])aug(?:\.|ust)?",      r"\1\2\g<1>08", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])sep(?:[t\.]|t\.|tember)?", r"\1\2\g<1>09", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])oct(?:\.|ober)?",     r"\1\2\g<1>10", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])nov(?:\.|ember)?",    r"\1\2\g<1>11", dts, flags=re.I)
        dts = re.sub(r"(\d{3,4}-)(\d\d[-/])dec(?:\.|ember)?",    r"\1\2\g<1>12", dts, flags=re.I)

        # print("normalize", dts)

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

        # calendar indication on ranges:
        # copy calendar indicators over.
        dts = re.sub(r"^([\d\-]+)-([\d\-]+) ([^\d ]+)$", r"\1 \3-\2 \3", dts)

        # print("pre split", dts)

        # --------
        # SPLIT
        # --------
        # Attempt to split dates at an appropriate hyphen; should result in 1-2.
        split_dates = re.split(r'-(?!\d\d(?:[\-\./]|[\?~]?$))', dts)

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
            time_content1_str = str(time_content1)
            trb.set_time_content_part1_link(time_content1_str, self.ix.simple_lookup(time_content1_str, TIME))
            if time_content2 is not None:
                time_content2_str = str(time_content2)
                trb.set_time_content_part2_link(time_content2_str, self.ix.simple_lookup(time_content2_str, TIME))

            return trb.build()

        elif len(split_dates) == 2:
            # This should be a DurationRef.
            drb = DurationRefBuilder()

            date1, date2 = split_dates

            # CALENDAR(S)
            calendar_kwargs1, date1 = self.extract_calendar(date1)
            if calendar_kwargs1:
                drb.set_calendar1(**calendar_kwargs1)
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
            time_content_single_s1_str = str(time_content_single_s1)
            drb.set_time_content1_part1_link(time_content_single_s1_str, self.ix.simple_lookup(time_content_single_s1_str, TIME))
            if time_content_single_s2 is not None:
                time_content_single_s2_str = str(time_content_single_s2)
                drb.set_time_content1_part2_link(time_content_single_s2_str, self.ix.simple_lookup(time_content_single_s2_str, TIME))

            time_content_single_e1_str = str(time_content_single_e1)
            drb.set_time_content2_part1_link(time_content_single_e1_str, self.ix.simple_lookup(time_content_single_e1_str, TIME))
            if time_content_single_e2 is not None:
                time_content_single_e2_str = str(time_content_single_e2)
                drb.set_time_content2_part2_link(time_content_single_e2_str, self.ix.simple_lookup(time_content_single_e2_str, TIME))

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
        Resolves cases of abbreviation in a pair of dates.
        """
        # 2012-09-02-28
        if re.match(r"\d{4}-\d\d-\d\d$", date1) and re.match(r"\d\d?$", date2):
            date2 = date1[:-2] + date2.zfill(2)
        # "<1842/43>"
        if re.match(r"<[^<>]+$", date1) and re.match(r"[^<>]+>$", date2):
            date1, date2 = date1[1:], date2[:-1]
            if date1.isdigit() and date2.isdigit():
                if len(date1) > len(date2) and int(date1) > int(date2):
                    date2 = date1[:-len(date2)] + date2
            date1, date2 = "<{}>".format(date1), "<{}>".format(date2)
        # "Nov./Dec. 1967"
        m = re.match(r"[\w\.]+( \d+)$", date2)
        if m and re.match(r"[\w\.]+$", date1):
            date1 += m.group(1)
        # "1996/7", "851-73"
        elif date1.lstrip('-').isdigit() and date2.lstrip('-').isdigit():
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
        if re.search(r"(^\[|\]$)", dts):
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
        if re.match(r"c(irca|a?\.)", dts, flags=re.I):
            dts = re.sub(r"^c(irca|a?\.) +", "", dts, flags=re.I)
            certainty = "approximate"
        if re.match(r"^<.*>$", dts, flags=re.I):
            dts = re.sub(r"^<(.*)>$", r"\1", dts, flags=re.I).strip()
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
        dts = re.sub(r"^(yyyy|uuuu|unknown)$", "Unknown", dts, flags=re.I)

        # synonyms for "Present"
        dts = re.sub(r"^(continuing|ongoing|present)$", "Present", dts, flags=re.I)

        # convert solo month names
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
        dts = re.sub(r"^jan(?:uary|\.)? +(.*)$",  r"\1-01", dts, flags=re.I)
        dts = re.sub(r"^feb(?:ruary|\.)? +(.*)$", r"\1-02", dts, flags=re.I)
        dts = re.sub(r"^mar(?:ch|\.)? +(.*)$",    r"\1-03", dts, flags=re.I)
        dts = re.sub(r"^apr(?:il|\.)? +(.*)$",    r"\1-04", dts, flags=re.I)
        dts = re.sub(r"^may +(.*)$",              r"\1-05", dts, flags=re.I)
        dts = re.sub(r"^jun[e\.]? +(.*)$",        r"\1-06", dts, flags=re.I)
        dts = re.sub(r"^jul[y\.]? +(.*)$",        r"\1-07", dts, flags=re.I)
        dts = re.sub(r"^aug(?:ust|\.)? +(.*)$",   r"\1-08", dts, flags=re.I)
        dts = re.sub(r"^sep(?:t(?:ember|\.)?|\.)? +(.*)$", r"\1-09", dts, flags=re.I)
        dts = re.sub(r"^oct(?:ober|\.)? +(.*)$",  r"\1-10", dts, flags=re.I)
        dts = re.sub(r"^nov(?:ember|\.)? +(.*)$", r"\1-11", dts, flags=re.I)
        dts = re.sub(r"^dec(?:ember|\.)? +(.*)$", r"\1-12", dts, flags=re.I)

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
        self.default_type_kwargs[WORK_AUT] = self.default_type_kwargs[WORK_INST] = self.default_type_kwargs[None]
