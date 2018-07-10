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
            element xobis:variants { anyVariant+ }?,
            optNoteList_
        }
        | element xobis:duration {
              optClass_,
              attribute usage { "subdivision" }?,
              _durationEntry,
              element xobis:variants { anyVariant+ }?,
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
        self.is_duration = isinstance(time_or_duration_entry, DurationEntry)
        assert self.is_duration or isinstance(time_or_duration_entry, TimeInstanceEntry)
        self.time_or_duration_entry = time_or_duration_entry
        # for variant elements
        assert all(isinstance(variant, VariantEntry) for variant in variants)
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
        if self.variants:
            variant_elements = [variant.serialize_xml() for variant in self.variants]
            variants_e = E('variants')
            variants_e.extend(variant_elements)
            time_e.append(variants_e)
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
            _timeContent
        }
    """
    def __init__(self, time_content, opt_scheme=OptScheme(), calendar=None):
        assert isinstance(time_content, TimeContent)
        self.time_content = time_content
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
        # contents
        time_content_elements, time_content_attrs = self.time_content.serialize_xml()
        entry_attrs.update(time_content_attrs)
        entry_e = E('entry', **entry_attrs)
        entry_e.extend(time_content_elements)
        return entry_e


class TimeEntry(Component):
    # TimeEntry is the substructure of times found in the Time principal element's
    # entry, the target of a relationship, the time qualifier, and anywhere else
    # times are used in XOBIS.  It may contain the time substructure directly or
    # represent a time that has two components (for instance, some serials have a
    # structure like: [start]1983/84-[end]1984/85).
    """
    _timeEntry |=
        linkAttributes_?,
        (_timeContent
        | (element xobis:part { _timeContent },
           element xobis:part { _timeContent }))
    """
    def __init__(self, time_content1, time_content2=None, link_attributes=None):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        self.is_parts = time_content2 is not None
        if self.is_parts:
            self.time_contents = [time_content1, time_content2]
            assert all(isinstance(content, TimeContent) for content in self.time_contents)
        else:
            assert isinstance(time_content1, TimeContent)
            self.time_contents = time_content1
    def serialize_xml(self):
        # Returns a list of one to eleven Elements, and a dict of parent attributes.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        if self.is_parts:
            elements = []
            for content in self.time_contents:
                time_content_elements, time_content_attrs = content.serialize_xml()
                part_e = E('part', **time_content_attrs)
                part_e.extend(time_content_elements)
                elements.append(part_e)
            return elements, attrs
        else:
            time_content_elements, time_content_attrs = self.time_contents.serialize_xml()
            attrs.update(time_content_attrs)
            return time_content_elements, attrs


class TimeContent(Component):
    """
    _timeContent |=
        type_?,
        attribute certainty {
            string "exact"
            | string "implied"       # [2018]
            | string "estimated"     # 2018?
            | string "approximate"   # approximately 2018/ca. 2018
        }?,
        attribute quality {
            _timeQuality (~ string " " ~ _timeQuality)*
        }?,
        ((_year, _month?, _day?, (_hour, _tzHour?)?, (_minute, _tzMinute?)?, _second?, _milliseconds?)
         | (_month, _day?, (_hour, _tzHour?)?, (_minute, _tzMinute?)?, _second?, _milliseconds?)
         | (_day, (_hour, _tzHour?)?, (_minute, _tzMinute?)?, _second?, _milliseconds?)
         | _milliseconds
         | genericName)
     _timeQuality |=
         string "before"
         | string "after"
         | string "early"
         | string "mid"
         | string "late"
    """
    CERTAINTIES = ["exact", "implied", "estimated", "approximate", None]
    QUALITIES   = ["before", "after", "early", "mid", "late", None]
    def __init__(self, time_contents, type_=Type(), certainty=None, quality=None):
        assert isinstance(type_, Type)
        self.type = type_
        assert certainty in self.CERTAINTIES
        self.certainty = certainty
        assert quality in self.QUALITIES or all(q in self.QUALITIES for q in quality.split(' '))
        self.quality = quality
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
    def __str__(self):
        # Convert to readable standardized-ish string
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # THIS IS TENTATIVE AND NOT ABLE TO REPRESENT EVERYTHING UNAMBIGUOUSLY!!!
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if self.generic_name:
            if self.generic_name.is_parts:
                return ' '.join([content.text for content in self.generic_name.name_content])
            else:
                return self.generic_name.name_content.text
        else:
            # ISO 8601
            result = ''
            if self.year:
                result += self.year.value
            elif self.month or self.day:
                result += '-'
            if self.month or self.day:
                if self.month:
                    result += '-' + self.month.value
                    if self.day:
                        result += '-' + self.day.value
                elif self.day:
                    result += '-' + self.day.value.zfill(3)
            if self.hour:
                if self.year or self.month or self.day:
                    result += 'T'
                result += self.hour.value
                if self.minute:
                    result += ':' + self.minute.value
                    if self.second:
                        result += ':' + self.second.value
                        if self.millisecond:
                            result += ':' + self.second.value
                if self.tz_hour:
                    if int(self.tz_hour.value) == 0 and (not self.tz_minute or (self.tz_minute and int(self.tz_minute.value) == 0)):
                        result += 'Z'
                    else:
                        if int(self.tz_hour.value) > 0 or (self.tz_minute and int(self.tz_minute.value) > 0):
                            result += '+'
                        else:
                            result += '-'
                        result += str(int(self.tz_hour.value))
            elif self.milliseconds:
                result = str(self.milliseconds.value / 1000.0)
            return result
    def serialize_xml(self):
        # Returns a list of one to eleven Elements and a dict of parent attributes.
        attrs = {}
        if self.certainty:
            attrs['certainty'] = self.certainty
        if self.quality:
            attrs['quality'] = self.quality
        elements = []
        for prop in (self.type, self.year, self.month, self.day, \
                     self.hour, self.tz_hour, self.minute, self.tz_minute, \
                     self.second, self.milliseconds, self.generic_name):
            if prop:
                prop_e = prop.serialize_xml()
                if prop_e is not None:
                    elements.append(prop_e)
        return elements, attrs


class TimeVariant(VariantEntry):
    """
    timeVariant |=
        element xobis:time { type_?, _timeInstanceEntry }
    """
    def __init__(self, time_or_duration_entry, type_=Type()):
        assert isinstance(type_, Type)
        self.type = type_
        assert isinstance(time_or_duration_entry, TimeInstanceEntry)
        self.time_or_duration_entry = time_or_duration_entry
    def serialize_xml(self):
        # Returns an Element.
        variant_e = E('time')
        # type
        type_e = self.type.serialize_xml()
        if type_e is not None:
            variant_e.append(type_e)
        # entry element
        time_or_duration_entry_e = self.time_or_duration_entry.serialize_xml()
        variant_e.append(time_or_duration_entry_e)
        return variant_e


class DurationVariant(VariantEntry):
    """
    durationVariant |=
        element xobis:duration { type_?, _durationEntry }
    """
    def __init__(self, time_or_duration_entry, type_=Type()):
        assert isinstance(type_, Type)
        self.type = type_
        assert isinstance(time_or_duration_entry, DurationEntry)
        self.time_or_duration_entry = time_or_duration_entry
    def serialize_xml(self):
        # Returns an Element.
        variant_e = E('duration')
        # type
        type_e = self.type.serialize_xml()
        if type_e is not None:
            variant_e.append(type_e)
        # entry element
        time_or_duration_entry_e = self.time_or_duration_entry.serialize_xml()
        variant_e.extend(time_or_duration_entry_e)
        return variant_e


class TimeRef(RefElement):
    """
    timeRef |=
        element xobis:time {
            attribute calendar { text }?,
            _timeEntry
        }
    """
    def __init__(self, time_entry, calendar=None):
        self.calendar = calendar
        assert isinstance(time_entry, TimeEntry),  \
            "time_entry is {}, must be TimeEntry".format(type(time_entry))
        self.time_entry = time_entry
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        attrs = {}
        if self.calendar:
            attrs['calendar'] = self.calendar
        # content
        time_entry_elements, time_entry_attrs = self.time_entry.serialize_xml()
        attrs.update(time_entry_attrs)
        time_e = E('time', **attrs)
        time_e.extend(time_entry_elements)
        return time_e


class DurationEntry(Component):
    """
    _durationEntry |=
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
        assert isinstance(time_duration_entry_part1, DurationEntryPart)
        self.time_duration_entry_part1 = time_duration_entry_part1
        assert isinstance(time_duration_entry_part2, DurationEntryPart)
        self.time_duration_entry_part2 = time_duration_entry_part2
    def serialize_xml(self):
        # Returns a list of two Elements.
        time_duration_entry_part1_e = self.time_duration_entry_part1.serialize_xml()
        time_duration_entry_part2_e = self.time_duration_entry_part2.serialize_xml()
        return [time_duration_entry_part1_e, time_duration_entry_part2_e]


class DurationEntryPart(Component):
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
        # contents
        time_entry_elements, time_entry_attrs = self.time_entry.serialize_xml()
        entry_attrs.update(time_entry_attrs)
        entry_e = E('entry', **entry_attrs)
        entry_e.extend(time_entry_elements)
        return entry_e


class DurationRef(RefElement):
    """
    durationRef |=
        element xobis:duration {
            linkAttributes_?,
            element xobis:time {
                attribute calendar { text }?,
                _timeEntry
            },
            element xobis:time {
                attribute calendar { text }?,
                _timeEntry
            }
        }
    """
    def __init__(self, time_entry1, time_entry2, calendar1=None, calendar2="", link_attributes=None):
        if link_attributes:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(time_entry1, TimeEntry)
        self.calendar1 = calendar1
        self.time_entry1 = time_entry1
        assert isinstance(time_entry2, TimeEntry)
        self.calendar2 = calendar1 if calendar2 == "" else calendar2
        self.time_entry2 = time_entry2
    def serialize_xml(self):
        # Returns an Element.
        # duration attributes
        attrs = {}
        if self.link_attributes:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        duration_e = E('duration', **attrs)
        # content
        # time 1
        time_entry1_elements, time_entry1_attrs = self.time_entry1.serialize_xml()
        if self.calendar1:
            time_entry1_attrs['calendar'] = self.calendar1
        time1_e = E('time', **time_entry1_attrs)
        time1_e.extend(time_entry1_elements)
        duration_e.append(time1_e)
        # time 2
        time_entry2_elements, time_entry2_attrs = self.time_entry2.serialize_xml()
        if self.calendar2:
            time_entry2_attrs['calendar'] = self.calendar2
        time2_e = E('time', **time_entry2_attrs)
        time2_e.extend(time_entry2_elements)
        duration_e.append(time2_e)
        return duration_e


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
    def __init__(self, value, zf=2):
        assert is_positive_integer(value)
        self.value = str(int(value)).zfill(zf)
    def serialize_xml(self, tag):
        # Returns an Element.
        e = E(tag)
        e.text = self.value
        return e

class Year(TimePart):
    def __init__(self, value, zf=4):
        assert isinstance(value, int) or value.isdigit()
        self.value  = '-' if int(value) != abs(int(value)) else ''
        self.value += str(abs(int(value))).zfill(zf)
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
    def __init__(self, value):
        super().__init__(value, zf=0)
    def serialize_xml(self):
        return super().serialize_xml('millisecs')


class TimeZonePart(Component):
    def __init__(self, value, zf=2):
        assert isinstance(value, int) or value.isdigit()
        self.is_negative = int(value) != abs(int(value))
        self.value  = '-' if self.is_negative else ''
        self.value += str(abs(int(value))).zfill(zf)
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
