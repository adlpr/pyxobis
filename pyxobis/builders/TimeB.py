#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class TimeEntryContentBuilder:
    """
    Interface for constructing a TimeEntryContent datetime object
    for use within XOBIS Time elements.
    """
    # NO SUPER
    # METHODS: add_name, set_time_contents, set_type, set_certainty
    def __init__(self):
        # Can either have a GenericName or be a numerical time entry.
        self.name_content = []   # NameContent objs (parts of named entry)
        self.time_content = []  # TimePart objs (parts of numerical entry)
        self.type = Type()
        self.certainty = None
    def add_name(self, name_text, lang=None, translit=None, nonfiling=0):
        assert not self.time_content, "Time already has numerical contents"
        self.name_content.append(
            NameContent(name_text, lang, translit, nonfiling)
        )
    def set_time_contents(self, \
        year=None, month=None, day=None, hour=None, tz_hour=None, \
        minute=None, tz_minute=None, second=None, milliseconds=None):
        assert not self.name_content, "Time already has named contents"
        for class_, arg in  \
            zip((Year,Month,Day,Hour,TZHour, Minute,TZMinute, Second,Milliseconds),
                (year,month,day,hour,tz_hour,minute,tz_minute,second,milliseconds)):
            if arg:
                self.time_content.append(class_(arg))
    def set_type(self, link_title, role_URI, href_URI=None):
        self.type = Type(
                        LinkAttributes(
                            link_title,
                            xlink_href = XSDAnyURI( href_URI ) \
                                         if href_URI else None
                        ),
                        xlink_role = XSDAnyURI( role_URI ) \
                                     if role_URI else None
                    )
    def set_certainty(self, certainty):
        self.certainty = certainty
    def build(self):
        time_contents = GenericName(self.name_content)  \
                        if self.name_content else self.time_content
        return TimeEntryContent(time_contents,
                                type_     = self.type,
                                certainty = self.certainty)



class TimeBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Time (instance) element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_qualifier, set_type, set_role
    # ADDITIONAL: set_time_entry_content, set_calendar
    def __init__(self):
        super().__init__()
        self.time_entry_content = None
        self.calendar = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("Time element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("Time element does not have qualifiers")
    def set_type(self, *args, **kwargs):
        raise AttributeError("Time element does not have property 'type'")
    def set_role(self, *args, **kwargs):
        raise AttributeError("Time element does not have property 'role'")
    def set_time_entry_content(self, new_time_entry_content):
        # assert isinstance(time_entry_content, TimeEntryContent)
        self.time_entry_content = new_time_entry_content
    def set_calendar(self, calendar):
        self.calendar = calendar
    def add_variant(self, variant):
        # input should be an TimeVariant
        # (containing a TimeInstanceEntry type entry, though this is not verified!).
        # use TimeVariantBuilder to build.
        assert isinstance(variant, TimeVariant)
        super().add_variant(variant)
    def build(self):
        return Time(
                    TimeInstanceEntry(
                        self.time_entry_content,
                        opt_scheme = OptScheme(self.scheme),
                        calendar = self.calendar
                    ),
                    opt_class = OptClass(self.class_),
                    usage     = self.usage,
                    variants  = self.variants,
                    opt_note_list = OptNoteList(self.note_list)
                )


class DurationBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Time (duration) element.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: set_scheme
    #    MISSING: add_name, add_qualifier, set_type, set_role
    # ADDITIONAL: set_time_entry1, set_time_entry2, set_calendar
    def __init__(self):
        super().__init__()
        self.time_entry1 = None
        self.scheme1 = None
        self.calendar1 = None
        self.time_entry2 = None
        self.scheme2 = None
        self.calendar2 = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("Time element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("Time element does not have qualifiers")
    def set_type(self, *args, **kwargs):
        raise AttributeError("Time element does not have property 'type'")
    def set_role(self, *args, **kwargs):
        raise AttributeError("Time element does not have property 'role'")
    def set_time_entry1(self, time_entry_content1, time_entry_content2=None):
        self.time_entry1 = TimeEntry(time_entry_content1, time_entry_content2)
    def set_time_entry2(self, time_entry_content1, time_entry_content2=None):
        self.time_entry2 = TimeEntry(time_entry_content1, time_entry_content2)
    def set_scheme(self, scheme1, scheme2=""):
        if scheme2 == "":  # use None for no scheme on entry part 2
            scheme2 = scheme1
        self.scheme1, self.scheme2 = scheme1, scheme2
    def set_calendar(self, calendar1, calendar2=""):
        if calendar2 == "":  # use None for no calendar on entry part 2
            calendar2 = calendar1
        self.calendar1, self.calendar2 = calendar1, calendar2
    def add_variant(self, variant):
        # input should be an TimeVariant
        # (containing a TimeDurationEntry type entry, though this is not verified!).
        # use TimeVariantBuilder to build.
        assert isinstance(variant, TimeVariant)
        super().add_variant(variant)
    def build(self):
        return Time(
                   TimeDurationEntry(
                       TimeDurationEntryPart(
                           self.time_entry1,
                           opt_scheme = OptScheme(self.scheme1),
                           calendar = self.calendar1
                       ),
                       TimeDurationEntryPart(
                           self.time_entry2,
                           opt_scheme = OptScheme(self.scheme2),
                           calendar = self.calendar2
                       )
                   ),
                   opt_class = OptClass(self.class_),
                   usage     = self.usage,
                   variants  = self.variants,
                   opt_note_list = OptNoteList(self.note_list)
               )



class TimeVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a TimeVariant.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_qualifier, set_time_or_duration_ref,
    #             set_substitute_attribute_type, add_note
    # ADDITIONAL: set_time_entry_content, set_calendar
    def __init__(self):
        super().__init__()
        self.time_entry_content = None
        self.calendar = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have qualifiers")
    def set_time_or_duration_ref(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not time/duration ref")
    def set_substitute_attribute_type(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have substitute attributes")
    def add_note(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have notes")
    def set_time_entry_content(self, new_time_entry_content):
        # assert isinstance(time_entry_content, TimeEntryContent)
        self.time_entry_content = new_time_entry_content
    def set_calendar(self, calendar):
        self.calendar = calendar
    def build(self):
        return TimeVariant(
                   TimeInstanceEntry(
                       self.time_entry_content,
                       opt_scheme = OptScheme(self.scheme),
                       calendar = self.calendar
                   ),
                   type_ = self.type
               )


class DurationVariantBuilder(PrincipalElementVariantBuilder):
    """
    Interface for constructing a DurationVariant.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: set_scheme
    #    MISSING: add_name, add_qualifier, set_time_or_duration_ref,
    #             set_substitute_attribute_type, add_note
    # ADDITIONAL: set_time_entry1, set_time_entry2, set_calendar
    def __init__(self):
        super().__init__()
        self.time_entry1 = None
        self.scheme1 = None
        self.calendar1 = None
        self.time_entry2 = None
        self.scheme2 = None
        self.calendar2 = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have qualifiers")
    def set_time_or_duration_ref(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not time/duration ref")
    def set_substitute_attribute_type(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have substitute attributes")
    def add_note(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have notes")
    def set_time_entry1(self, time_entry_content1, time_entry_content2=None):
        self.time_entry1 = TimeEntry(time_entry_content1, time_entry_content2)
    def set_time_entry2(self, time_entry_content1, time_entry_content2=None):
        self.time_entry2 = TimeEntry(time_entry_content1, time_entry_content2)
    def set_scheme(self, scheme1, scheme2=""):
        if scheme2 == "":  # use None for no scheme on entry part 2
            scheme2 = scheme1
        self.scheme1, self.scheme2 = scheme1, scheme2
    def set_calendar(self, calendar1, calendar2=""):
        if calendar2 == "":  # use None for no calendar on entry part 2
            calendar2 = calendar1
        self.calendar1, self.calendar2 = calendar1, calendar2
    def build(self):
        return DurationVariant(
                   TimeDurationEntry(
                       TimeDurationEntryPart(
                           self.time_entry1,
                           opt_scheme = OptScheme(self.scheme1),
                           calendar = self.calendar1
                       ),
                       TimeDurationEntryPart(
                           self.time_entry2,
                           opt_scheme = OptScheme(self.scheme2),
                           calendar = self.calendar2
                       )
                   ),
                   type_ = self.type
               )



class TimeRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a TimeRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_qualifier, add_subdivision_link
    # ADDITIONAL: set_time_entry_content, set_calendar
    def __init__(self):
        super().__init__()
        self.time_entry_content = None
        self.calendar = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("TimeRef element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("TimeRef element does not have qualifiers")
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("TimeRef element does not have subdivison")
    def set_time_entry_content(self, new_time_entry_content):
        # can be TimeEntryContent *or* XSDDateTime.
        # if not the former, assumes input is a string to convert to the latter
        if not isinstance(time_entry_content, TimeEntryContent):
            new_time_entry_content = XSDDateTime(new_time_entry_content)
        self.time_entry_content = new_time_entry_content
    def set_calendar(self, calendar):
        self.calendar = calendar
    def build(self):
        return TimeRef(
                   self.time_entry_content,
                   calendar = self.calendar,
                   link_attributes = self.link_attributes
               )


class DurationRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a DurationRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_qualifier, add_subdivision_link
    # ADDITIONAL: set_time_entry1, set_time_entry2, set_calendar
    def __init__(self):
        super().__init__()
        self.time_entry1 = None
        self.calendar1 = None
        self.time_entry2 = None
        self.calendar2 = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("DurationRef element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("DurationRef element does not have qualifiers")
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("DurationRef element does not have subdivision")
    def set_time_entry1(self, time_entry_content1, time_entry_content2=None):
        self.time_entry1 = TimeEntry(time_entry_content1, time_entry_content2)
    def set_time_entry2(self, time_entry_content1, time_entry_content2=None):
        self.time_entry2 = TimeEntry(time_entry_content1, time_entry_content2)
    def set_calendar(self, calendar1, calendar2=""):
        if calendar2 == "":  # use None for no calendar on time entry 2
            calendar2 = calendar1
        self.calendar1, self.calendar2 = calendar1, calendar2
    def build(self):
        return DurationRef(
                   time_entry1 = self.time_entry1,
                   calendar1   = self.calendar1,
                   time_entry2 = self.time_entry2,
                   calendar2   = self.calendar2,
                   link_attributes = self.link_attributes
               )
