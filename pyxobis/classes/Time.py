#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .common import *

from lxml.builder import ElementMaker
E = ElementMaker(namespace="http://www.xobis.info/ns/2.0/",
                 nsmap={None:"http://www.xobis.info/ns/2.0/"})


class Time(PrincipalElement):
    """
    timePE |= timeInstancePE | durationPE

    timeInstancePE |=
        element xobis:time {
            optClass,
            attribute usage { "subdivision" }?,
            timeInstanceEntry,
            element xobis:variants { anyVariant+ }?,
            optNoteList
        }

    durationPE |=
        element xobis:duration {
            optClass,
            attribute usage { "subdivision" }?,
            durationEntry,
            element xobis:variants { anyVariant+ }?,
            optNoteList
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
    timeInstanceEntry |=
        element xobis:entry {
            optScheme,
            optEntryGroupAttributes,
            calendar?,
            timeContentSingle
        }
    """
    def __init__(self, time_content_single, opt_scheme=OptScheme(), \
                       opt_entry_group_attributes=OptEntryGroupAttributes(), \
                       calendar=None):
        assert isinstance(time_content_single, TimeContentSingle)
        self.time_content_single = time_content_single
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        assert isinstance(opt_entry_group_attributes, OptEntryGroupAttributes)
        self.opt_entry_group_attributes = opt_entry_group_attributes
        if calendar is not None:
            assert isinstance(calendar, Calendar)
        self.calendar = calendar
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        entry_attrs = {}
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        entry_attrs.update(opt_scheme_attrs)
        opt_entry_group_attributes_attrs = self.opt_entry_group_attributes.serialize_xml()
        entry_attrs.update(opt_entry_group_attributes_attrs)
        # contents
        time_content_single_elements, time_content_single_attrs = self.time_content_single.serialize_xml()
        entry_attrs.update(time_content_single_attrs)
        entry_e = E('entry', **entry_attrs)
        if self.calendar is not None:
            calendar_e = self.calendar.serialize_xml()
            entry_e.append(calendar_e)
        entry_e.extend(time_content_single_elements)
        return entry_e


class TimeContentSingle(Component):
    """
    timeContentSingle |=
        genericType?,
        attribute certainty {
            string "exact"
            | string "implied"       # [2018]
            | string "estimated"     # 2018?
            | string "approximate"   # approximately 2018/ca. 2018
        }?,
        attribute quality {
            timeQuality (~ string " " ~ timeQuality)*
        }?,
        (year?, month?, day?, hour?, minute?, second?, millisecond?, tzHour?, tzMinute?
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
    def __init__(self, time_contents, type_=None, certainty=None, quality=None):
        if type_ is not None:
            assert isinstance(type_, GenericType)
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
        self.millisecond  = time_content_types.get(Millisecond)
        self.generic_name = time_content_types.get(GenericName)
        if self.generic_name:
            assert not any((self.year, self.month, self.day, self.hour, self.tz_hour, \
                            self.minute, self.tz_minute, self.second, self.millisecond))
    def __str__(self):
        # Convert to readable standardized-ish string
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
            if self.month:
                result += '-' + self.month.value
                if self.day:
                    result += '-' + self.day.value
            elif self.day:
                result += '-' + self.day.value.zfill(3)
            if self.hour or self.minute or self.second or self.millisecond or self.tz_hour or self.tz_minute:
                result += 'T'
                if self.hour:
                    result += self.hour.value
                if self.minute or self.second or self.millisecond:
                    result += ':'
                    if self.minute:
                        result += self.minute.value
                    if self.second or self.millisecond:
                        result += ':'
                        if self.second:
                            result += self.second.value
                        if self.millisecond:
                            result += self.millisecond.value.zfill(3)
                if self.tz_hour and self.tz_minute and int(self.tz_hour.value)==0 and int(self.tz_minute.value)==0:
                    result += 'Z'
                else:
                    if self.tz_hour:
                        if not self.tz_hour.value.startswith('-'):
                            result += '+'
                        result += self.tz_hour.value
                        if self.tz_minute:
                            result += ':' + self.tz_minute.value
                    elif self.tz_minute:
                        result += ':' + self.tz_minute.value
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
                     self.second, self.millisecond, self.generic_name):
            if prop is not None:
                prop_e = prop.serialize_xml()
                if prop_e is not None:
                    elements.append(prop_e)
        return elements, attrs


class TimeContent(Component):
    """
    timeContent |=
        ( timeContentPart
          | element xobis:part { timeContentPart },
            element xobis:part { timeContentPart } )
    """
    def __init__(self, time_content_part1, time_content_part2=None):
        self.is_parts = time_content_part2 is not None
        if self.is_parts:
            self.time_contents = [time_content_part1, time_content_part2]
            assert all(isinstance(content_part, TimeContentPart) for content_part in self.time_contents)
        else:
            assert isinstance(time_content_part1, TimeContentPart)
            self.time_contents = time_content_part1
    def serialize_xml(self):
        # Returns a list of one to eleven Elements, and a dict of parent attributes.
        if self.is_parts:
            elements = []
            for content in self.time_contents:
                time_content_elements, time_content_attrs = content.serialize_xml()
                part_e = E('part', **time_content_attrs)
                part_e.extend(time_content_elements)
                elements.append(part_e)
            return elements, {}
        else:
            return self.time_contents.serialize_xml()

class TimeContentPart(Component):
    """
    timeContentPart |=
        linkAttributes?, optSubstituteAttribute, timeContentSingle
    """
    def __init__(self, time_content_single, link_attributes=None, opt_substitute_attribute=OptSubstituteAttribute()):
        if link_attributes is not None:
            assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(opt_substitute_attribute, OptSubstituteAttribute)
        self.opt_substitute_attribute = opt_substitute_attribute
        assert isinstance(time_content_single, TimeContentSingle)
        self.time_content_single = time_content_single
    def serialize_xml(self):
        # Returns a list of one to eleven Elements, and a dict of parent attributes.
        attrs = {}
        if self.link_attributes is not None:
            link_attributes_attrs = self.link_attributes.serialize_xml()
            attrs.update(link_attributes_attrs)
        opt_substitute_attribute_attrs = self.opt_substitute_attribute.serialize_xml()
        attrs.update(opt_substitute_attribute_attrs)
        time_content_elements, time_content_attrs = self.time_content_single.serialize_xml()
        attrs.update(time_content_attrs)
        return time_content_elements, attrs


class TimeVariant(VariantEntry):
    """
    timeVariant |=
        element xobis:time { optVariantAttributes, genericType?, timeInstanceEntry, optNoteList }
    """
    def __init__(self, time_instance_entry, \
                       opt_variant_attributes=OptVariantAttributes(), \
                       type_=None, opt_note_list=OptNoteList()):
        assert isinstance(opt_variant_attributes, OptVariantAttributes)
        self.opt_variant_attributes = opt_variant_attributes
        if type_ is not None:
            assert isinstance(type_, GenericType)
        self.type = type_
        assert isinstance(time_instance_entry, TimeInstanceEntry)
        self.time_instance_entry = time_instance_entry
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        opt_variant_attributes_attrs = self.opt_variant_attributes.serialize_xml()
        variant_e = E('time', **opt_variant_attributes_attrs)
        # type
        if self.type is not None:
            type_e = self.type.serialize_xml()
            variant_e.append(type_e)
        # entry element
        time_instance_entry_e = self.time_instance_entry.serialize_xml()
        variant_e.append(time_instance_entry_e)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e


class TimeRef(RefElement):
    """
    timeRef |=
        element xobis:time {
            calendar?,
            timeContent
        }
    """
    def __init__(self, time_content, calendar=None):
        if calendar is not None:
            assert isinstance(calendar, Calendar)
        self.calendar = calendar
        assert isinstance(time_content, TimeContent),  \
            "time_content is {}, must be TimeContent".format(type(time_content))
        self.time_content = time_content
    def serialize_xml(self):
        # Returns an Element.
        time_content_elements, time_content_attrs = self.time_content.serialize_xml()
        time_e = E('time', **time_content_attrs)
        if self.calendar is not None:
            calendar_e = self.calendar.serialize_xml()
            time_e.append(calendar_e)
        time_e.extend(time_content_elements)
        return time_e


class DurationEntry(Component):
    """
    durationEntry |=
        element xobis:entry {
            optEntryGroupAttributes,
            element xobis:time {
              optScheme,
              calendar?,
              timeContent
            },
            element xobis:time {
              optScheme,
              calendar?,
              timeContent
            }
        }
    """
    def __init__(self, time_duration_entry_part1, time_duration_entry_part2,
                       opt_entry_group_attributes=OptEntryGroupAttributes()):
        assert isinstance(opt_entry_group_attributes, OptEntryGroupAttributes)
        self.opt_entry_group_attributes = opt_entry_group_attributes
        assert isinstance(time_duration_entry_part1, DurationEntryPart)
        self.time_duration_entry_part1 = time_duration_entry_part1
        assert isinstance(time_duration_entry_part2, DurationEntryPart)
        self.time_duration_entry_part2 = time_duration_entry_part2
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        opt_entry_group_attributes_attrs = self.opt_entry_group_attributes.serialize_xml()
        entry_e = E('entry', **opt_entry_group_attributes_attrs)
        # contents
        time_duration_entry_part1_e = self.time_duration_entry_part1.serialize_xml()
        entry_e.append(time_duration_entry_part1_e)
        time_duration_entry_part2_e = self.time_duration_entry_part2.serialize_xml()
        entry_e.append(time_duration_entry_part2_e)
        return entry_e


class DurationEntryPart(Component):
    """
    element xobis:time {
        optScheme,
        calendar?,
        timeContent
    }
    """
    def __init__(self, time_content, opt_scheme=OptScheme(), calendar=None):
        assert isinstance(time_content, TimeContent)
        self.time_content = time_content
        assert isinstance(opt_scheme, OptScheme)
        self.opt_scheme = opt_scheme
        if calendar is not None:
            assert isinstance(calendar, Calendar)
        self.calendar = calendar
    def serialize_xml(self):
        # Returns an Element.
        # attributes
        time_attrs = {}
        opt_scheme_attrs = self.opt_scheme.serialize_xml()
        time_attrs.update(opt_scheme_attrs)
        # contents
        time_content_elements, time_content_attrs = self.time_content.serialize_xml()
        time_attrs.update(time_content_attrs)
        time_e = E('time', **time_attrs)
        if self.calendar is not None:
            calendar_e = self.calendar.serialize_xml()
            time_e.append(calendar_e)
        time_e.extend(time_content_elements)
        return time_e


class DurationVariant(VariantEntry):
    """
    durationVariant |=
        element xobis:duration { optVariantAttributes, genericType?, durationEntry, optNoteList }
    """
    def __init__(self, duration_entry, \
                       opt_variant_attributes=OptVariantAttributes(), \
                       type_=None, opt_note_list=OptNoteList()):
        assert isinstance(opt_variant_attributes, OptVariantAttributes)
        self.opt_variant_attributes = opt_variant_attributes
        if type_ is not None:
            assert isinstance(type_, GenericType)
        self.type = type_
        assert isinstance(duration_entry, DurationEntry)
        self.duration_entry = duration_entry
        assert isinstance(opt_note_list, OptNoteList)
        self.opt_note_list = opt_note_list
    def serialize_xml(self):
        # Returns an Element.
        # variant attributes
        opt_variant_attributes_attrs = self.opt_variant_attributes.serialize_xml()
        variant_e = E('duration', **opt_variant_attributes_attrs)
        # type
        if self.type is not None:
            type_e = self.type.serialize_xml()
            variant_e.append(type_e)
        # entry element
        duration_entry_e = self.duration_entry.serialize_xml()
        variant_e.append(duration_entry_e)
        # note list
        opt_note_list_e = self.opt_note_list.serialize_xml()
        if opt_note_list_e is not None:
            variant_e.append(opt_note_list_e)
        return variant_e


class DurationRef(RefElement):
    """
    durationRef |=
        element xobis:duration {
            element xobis:time {
                calendar?,
                timeContent
            },
            element xobis:time {
                calendar?,
                timeContent
            }
        }
    """
    def __init__(self, time_content1, time_content2, calendar1=None, calendar2=""):
        assert isinstance(time_content1, TimeContent)
        if calendar1 is not None:
            assert isinstance(calendar1, Calendar)
        self.calendar1 = calendar1
        self.time_content1 = time_content1
        assert isinstance(time_content2, TimeContent)
        if calendar2 not in [None, ""]:
            assert isinstance(calendar2, Calendar)
        self.calendar2 = calendar1 if calendar2 == "" else calendar2
        self.time_content2 = time_content2
    def serialize_xml(self):
        # Returns an Element.
        duration_e = E('duration')
        # time 1
        time_content1_elements, time_content1_attrs = self.time_content1.serialize_xml()
        time1_e = E('time', **time_content1_attrs)
        time1_e.extend(time_content1_elements)
        if self.calendar1 is not None:
            calendar1_e = self.calendar1.serialize_xml()
            time1_e.append(calendar1_e)
        duration_e.append(time1_e)
        # time 2
        time_content2_elements, time_content2_attrs = self.time_content2.serialize_xml()
        time2_e = E('time', **time_content2_attrs)
        time2_e.extend(time_content2_elements)
        if self.calendar2 is not None:
            calendar2_e = self.calendar2.serialize_xml()
            time2_e.append(calendar2_e)
        duration_e.append(time2_e)
        return duration_e


class Calendar(Component):
    """
    # structure of Calendar looks the same as GenericType (but not optional)
    calendar |=
        element xobis:calendar {
            linkAttributes,
            attribute set { xsd:anyURI },
            empty
        }
    """
    def __init__(self, link_attributes, set_ref):
        assert isinstance(link_attributes, LinkAttributes)
        self.link_attributes = link_attributes
        assert isinstance(set_ref, XSDAnyURI)
        self.set_ref = set_ref
    def serialize_xml(self):
        # Returns an Element.
        attrs = {}
        link_attributes = self.link_attributes.serialize_xml()
        attrs.update(link_attributes)
        set_ref_text = self.set_ref.serialize_xml()
        attrs['set'] = set_ref_text
        calendar_e = E('calendar', **attrs)
        return calendar_e



"""
    _year   |= element xobis:year { xsd:positiveInteger }   # <-- what about BCE? does this assume holocene?
    _month  |= element xobis:month { xsd:positiveInteger }
    _day    |= element xobis:day { xsd:positiveInteger }
    _hour   |= element xobis:hour { xsd:positiveInteger }
    _minute |= element xobis:minute { xsd:positiveInteger }
    _second |= element xobis:second { xsd:positiveInteger }
    _milliseconds |= element xobis:millisecs { xsd:positiveInteger }
    _tzHour |= element xobis:tzHour { xsd:integer }
    _tzMinute |= element xobis:tzMinute { xsd:integer }
"""

class TimePart(Component):
    def __init__(self, value, zf=2):
        assert is_non_negative_int(value)
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

class Millisecond(TimePart):
    def __init__(self, value):
        super().__init__(value, zf=0)
    def serialize_xml(self):
        return super().serialize_xml('millisecond')


class TZHour(Component):
    def __init__(self, value, is_negative=None, zf=2):
        assert isinstance(value, int) or value.isdigit()
        if is_negative is not None:
            # can have +0 and -0
            self.is_negative = is_negative
        else:
            self.is_negative = int(value) != abs(int(value))
        self.value  = '-' if self.is_negative else ''
        self.value += str(abs(int(value))).zfill(zf)
    def serialize_xml(self):
        # Returns an Element.
        e = E('tzHour')
        e.text = self.value
        return e

class TZMinute(Component):
    def __init__(self, value, zf=2):
        assert isinstance(value, int) or value.isdigit()
        self.value = str(abs(int(value))).zfill(zf)
    def serialize_xml(self):
        # Returns an Element.
        e = E('tzMinute')
        e.text = self.value
        return e
