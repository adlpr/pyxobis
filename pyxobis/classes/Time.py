#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re
from .common import *

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={'xobis':"http://www.xobis.info/ns/2.0/",
                        'xlink':"https://www.w3.org/1999/xlink"})


class Time(PrincipalElement):
    """
    timePE |=
        element xobis:time {
            optClass_,
            attribute usage { "subdivision" }?,
            _timeInstanceEntry,
            _timeVariant+,     # <-- treating this + as a mistake for *
            optNoteList_
        }
        | element xobis:duration {
              optClass_,
              attribute usage { "subdivision" }?,
              _timeDurationEntry,
              _timeVariant+,   # <-- treating this + as a mistake for *
              optNoteList_
          }
    """
    USAGES = ["subdivision", None]
    def __init__(self, time_or_duration_entry, \
                       opt_class=OptClass(), usage=None, \
                       variants=[], opt_note_list=OptNoteList()):
        # attributes
        assert isinstance(opt_class, OptClass)
        self.opt_class = opt_class
        assert usage in Time.USAGES
        self.usage = usage
        # for entry element
        self.is_duration = isinstance(time_or_duration_entry, TimeDurationEntry)
        assert self.is_duration or isinstance(time_or_duration_entry, TimeInstanceEntry)
        self.time_or_duration_entry = time_or_duration_entry
        # for variant elements
        assert all(isinstance(variant, TimeVariant) for variant in variants)
        self.variants = variants
        # for note list
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        time_attrs = {}
        opt_class_attrs = self.opt_class.serialize_xml()
        time_attrs.update(opt_class_attrs)
        if self.usage:
            time_attrs['usage'] = self.usage
        time_e = E('duration' if self.is_duration else 'time', **time_attrs)
        # entry element
        time_or_duration_entry_e = self.time_or_duration_entry.serialize_xml()
        if self.is_duration:
            time_e.extend(time_or_duration_entry_e)
        else:
            time_e.append(time_or_duration_entry_e)
        # variant elements
        variant_elements = [variant.serialize_xml() for variant in self.variants]
        time_e.extend(variant_elements)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            time_e.append(opt_note_list_e)
        return time_e


class TimeInstanceEntry(Component):
    """
    _timeInstanceEntry |=
        element xobis:entry {
            optScheme_,
            attribute calendar { text }?,
            _timeEntryContent
        }
    """
    def __init__(self, time_entry_content, opt_scheme=OptScheme(), calendar=None):
        assert isinstance(time_entry_content, TimeEntryContent)
        self.time_entry_content = time_entry_content
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        self.calendar = calendar
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        entry_attrs = {}
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_attrs.update(opt_scheme_attrs)
        if self.calendar:
            entry_attrs['calendar'] = self.calendar
        entry_e = E('entry', **entry_attrs)
        # contents
        time_entry_content_elements = self.time_entry_content.serialize_xml()
        entry_e.extend(time_entry_content_elements)
        return entry_e


class TimeEntry(Component):
    # TimeEntry is the substructure of times found in the Time principal element's
    # entry, the target of a relationship, the time qualifier, and anywhere else
    # times are used in XOBIS.  It may contain the time substructure directly or
    # represent a time that has two components (for instance, some serials have a
    # structure like: [start]1983/84-[end]1984/85).
    """
    _timeEntry |=
        _timeEntryContent
        | (element xobis:part { _timeEntryContent },
           element xobis:part { _timeEntryContent })
    """
    def __init__(self, time_entry1, time_entry2=None):
        self.is_parts = time_entry2 is not None
        self.time_entry_contents = [time_entry1, time_entry2] if self.is_parts else [time_entry1]
        assert all(isinstance(content, TimeEntryContent) for content in self.time_entry_contents)
    def serialize_xml(self):
        # Returns a list of one to eleven Elements.
        if self.is_parts:
            elements = []
            for content in self.time_entry_contents:
                part_e = E('part')
                time_entry_content_elements = content.serialize_xml()
                part_e.extend(time_entry_content_elements)
                elements.append(part_e)
            return elements
        return self.time_entry_contents.serialize_xml()


class TimeEntryContent(Component):
    """
    _timeEntryContent |=
        type_?,
        element xobis:certainty {
            attribute set { text },
            content_
        }?,
        ((_year, _month?, _day?, (_hour, _tzHour?)?, (_minute, _tzMinute?)?, _second?, _milliseconds?)
         | (_month, _day?, (_hour, _tzHour?)?, (_minute, _tzMinute?)?, _second?, _milliseconds?)
         | (_day, (_hour, _tzHour?)?, (_minute, _tzMinute?)?, _second?, _milliseconds?)
         | _milliseconds
         | genericName)
    """
    def __init__(self, time_contents, type_=Type(), certainty=None):
        assert isinstance(type_, Type)
        self.type = type_
        if certainty:
            assert isinstance(certainty, Certainty)
        self.certainty = certainty
        # parse out what the content passed in represents.
        try:
            time_contents = list(time_contents)
        except:
            time_contents = [time_contents]
        assert all(isinstance(time_content, TimePart) for time_content in time_contents)  \
               or len(time_contents) == 1 and isinstance(time_contents[0], GenericName)
        time_content_types = { type(time_content) : time_content for time_content in time_contents }
        assert len(time_content_types) == len(time_contents), "Repeated element type"
        self.year         = time_content_types.get(Year)
        self.month        = time_content_types.get(Month)
        self.day          = time_content_types.get(Day)
        self.hour         = time_content_types.get(Hour)
        self.tz_hour      = time_content_types.get(TZHour)
        self.minute       = time_content_types.get(Minute)
        self.tz_minute    = time_content_types.get(TZMinute)
        self.second       = time_content_types.get(Second)
        self.milliseconds = time_content_types.get(Milliseconds)
        self.generic_name = time_content_types.get(GenericName)
        # now enforce specs
        if self.generic_name:
            # type 5
            assert not any((self.year, self.month, self.day, self.hour, self.tz_hour, \
                            self.minute, self.tz_minute, self.second, self.milliseconds))
        elif any((self.hour, self.tz_hour, self.minute, self.tz_minute, self.second)):
            # type 1, 2, 3
            assert any((self.year, self.month, self.day))
    def serialize_xml(self):
        # Returns a list of one to eleven Elements.
        elements = []
        for prop in (self.type, self.certainty, self.year, self.month, self.day, \
                     self.hour, self.tz_hour, self.minute, self.tz_minute, \
                     self.second, self.milliseconds, self.generic_name):
            if prop:
                prop_e = prop.serialize_xml()
                if prop_e is not None:
                    elements.append(prop_e)
        return elements


class Certainty(Component):
    """
    element xobis:certainty {
        attribute set { text },
        content_
    }
    """
    def __init__(self, content, set_=None):
        self.set = set_
        assert isinstance(content, Content)
        self.content = content
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        certainty_attrs = {}
        if self.set:
            certainty_attrs['set'] = self.set
        # content
        content_text, content_attrs = self.content.serialize_xml()
        certainty_attrs.update(content_attrs)
        certainty_e = E('certainty', **certainty_attrs)
        certainty_e.text = content_text
        return certainty_e


class TimeVariant(Component):
    """
    _timeVariant |= element xobis:variant { type_?, (_timeInstanceEntry | _timeDurationEntry) }
    """
    def __init__(self, time_or_duration_entry, type_=Type()):
        assert isinstance(type_, Type)
        self.type = type_
        self.is_duration = isinstance(time_or_duration_entry, TimeDurationEntry)
        assert self.is_duration or isinstance(time_or_duration_entry, TimeInstanceEntry)
        self.time_or_duration_entry = time_or_duration_entry
    def serialize_xml(self):
        # Returns an Element.
        variant_e = E('variant')
        # type
        type_e = self.type.serialize_xml()
        if type_e is not None:
            variant_e.append(type_e)
        # entry element
        time_or_duration_entry_e = self.time_or_duration_entry.serialize_xml()
        if self.is_duration:
            variant_e.extend(time_or_duration_entry_e)
        else:
            variant_e.append(time_or_duration_entry_e)
        return variant_e


class TimeRef(RefElement):
    """
    timeRef |=
        element xobis:time {
            attribute calendar { text }?,
            linkAttributes_?,
            (_timeEntryContent | xsd:dateTime)
        }
    """
    def __init__(self, time_entry_content, calendar=None, link_attributes=None):
        self.calendar = calendar
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        self.is_time_entry = isinstance(time_entry_content, TimeEntryContent)
        assert self.is_time_entry or isinstance(time_entry_content, XSDDateTime)
        self.time_entry_content = time_entry_content
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        attrs = {}
        if self.time:
            attrs['calendar'] = self.calendar
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        time_e = E('time', **attrs)
        # content
        if self.is_time_entry:
            time_entry_content_elements = self.time_entry_content.serialize_xml()
            time_e.extend(time_entry_content_elements)
        else:
            time_entry_content_text = self.time_entry_content.serialize_xml()
            time_e.text = time_entry_content_text
        return time_e


class TimeDurationEntry(Component):
    """
    _timeDurationEntry |=
        element xobis:entry {
            optScheme_,
            attribute calendar { text }?,
            _timeEntry
        },
        element xobis:entry {
            optScheme_,
            attribute calendar { text }?,
            _timeEntry
        }
    """
    def __init__(self, time_duration_entry_part1, time_duration_entry_part2):
        assert isinstance(time_duration_entry_part1, TimeDurationEntryPart)
        self.time_duration_entry_part1 = time_duration_entry_part1
        assert isinstance(time_duration_entry_part2, TimeDurationEntryPart)
        self.time_duration_entry_part2 = time_duration_entry_part2
    def serialize_xml(self):
        # Returns a list of two Elements.
        time_duration_entry_part1_e = self.time_duration_entry_part1.serialize_xml()
        time_duration_entry_part2_e = self.time_duration_entry_part2.serialize_xml()
        return [time_duration_entry_part1_e, time_duration_entry_part2_e]


class TimeDurationEntryPart(Component):
    """
    element xobis:entry {
        optScheme_,
        attribute calendar { text }?,
        _timeEntry
    }
    """
    def __init__(self, time_entry, opt_scheme=OptScheme(), calendar=None):
        assert isinstance(time_entry, TimeEntry)
        self.time_entry = time_entry
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        self.calendar = calendar
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        entry_attrs = {}
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_attrs.update(opt_scheme_attrs)
        if self.calendar:
            entry_attrs['calendar'] = self.calendar
        entry_e = E('entry', **entry_attrs)
        # contents
        time_entry_elements = self.time_entry.serialize_xml()
        entry_e.extend(time_entry_elements)
        return entry_e


class DurationRef(RefElement):
    """
    durationRef |=
        element xobis:duration {
            attribute calendar { text }?,
            linkAttributes_?,
            element xobis:time { _timeEntry },
            element xobis:time { _timeEntry }?
        }
    """
    def __init__(self, time_entry1, time_entry2=None, calendar=None, link_attributes=None):
        self.calendar = calendar
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(time_entry1, TimeEntry)
        self.time_entry1 = time_entry1
        if time_entry2:
            assert isinstance(time_entry2, TimeEntry)
            self.time_entry2 = time_entry2
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        attrs = {}
        if self.time:
            attrs['calendar'] = self.calendar
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        duration_e = E('duration', **attrs)
        # content
        time_entry1_e = self.time_entry1.serialize_xml()
        duration_e.append(time_entry1_e)
        if time_entry2:
            time_entry2_e = self.time_entry2.serialize_xml()
            duration_e.append(time_entry2_e)
        return time_e


"""
_year   |= element xobis:year { xsd:positiveInteger }   # <-- what about BCE? does this assume holocene?
_month  |= element xobis:month { xsd:positiveInteger }
_day    |= element xobis:day { xsd:positiveInteger }
_hour   |= element xobis:hour { xsd:positiveInteger }
_minute |= element xobis:minute { xsd:positiveInteger }
_second |= element xobis:second { xsd:positiveInteger }
_milliseconds |= element xobis:millisecs { xsd:positiveInteger }
_tzHour |= element xobis:TZHour { xsd:integer }
_tzMinute |= element xobis:TZMinute { xsd:integer }
"""

class TimePart(Component):
    def __init__(self, value):
        assert is_positive_integer(value)
        self.value = str(int(value))
    def serialize_xml(self, tag):
        # Returns an Element.
        e = E(tag)
        e.text = self.value
        return e

class Year(TimePart):
    def serialize_xml(self):
        return super().serialize_xml('year')

class Month(TimePart):
    def serialize_xml(self):
        return super().serialize_xml('month')

class Day(TimePart):
    def serialize_xml(self):
        return super().serialize_xml('day')

class Hour(TimePart):
    def serialize_xml(self):
        return super().serialize_xml('hour')

class Minute(TimePart):
    def serialize_xml(self):
        return super().serialize_xml('minute')

class Second(TimePart):
    def serialize_xml(self):
        return super().serialize_xml('second')

class Milliseconds(TimePart):
    def serialize_xml(self):
        return super().serialize_xml('millisecs')


class TimeZonePart(Component):
    def __init__(self, value):
        assert isinstance(value, int) or value.isdigit()
        self.value = int(value)
    def serialize_xml(self, tag):
        # Returns an Element.
        e = E(tag)
        e.text = self.value
        return e

class TZHour(TimeZonePart):
    def serialize_xml(self):
        return super().serialize_xml('TZHour')

class TZMinute(TimeZonePart):
    def serialize_xml(self):
        return super().serialize_xml('TZMinute')
