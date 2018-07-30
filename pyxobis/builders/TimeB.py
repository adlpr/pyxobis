#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pyxobis.classes import *
from .common import PrincipalElementBuilder, PrincipalElementVariantBuilder, PrincipalElementRefBuilder


class TimeContentSingleBuilder:
    """
    Interface for constructing a TimeContentSingle datetime object
    for use within XOBIS Time elements.
    """
    # NO SUPER
    # METHODS: add_name, set_time_contents, set_type, set_certainty, set_quality
    def __init__(self):
        # Can either have a GenericName or be a numerical time entry.
        self.name_content = []   # NameContent objs (parts of named entry)
        self.time_content = []  # TimePart objs (parts of numerical entry)
        self.type = None
        self.certainty = None
        self.quality = None
    def add_name(self, name_text, lang=None, script=None, nonfiling=0):
        assert not self.time_content, "Time already has numerical contents"
        assert name_text, "Name must not be empty"
        self.name_content.append(
            NameContent(name_text, lang, script, nonfiling)
        )
    def set_time_contents(self, \
        year=None, month=None, day=None, hour=None, tz_hour=None, \
        minute=None, tz_minute=None, second=None, milliseconds=None):
        assert not self.name_content, "Time already has named contents"
        for class_, arg in  \
            zip((Year,Month,Day,Hour,TZHour, Minute,TZMinute, Second,Milliseconds),
                (year,month,day,hour,tz_hour,minute,tz_minute,second,milliseconds)):
            if arg is not None:
                self.time_content.append(class_(arg))
    def set_type(self, link_title, set_URI, href_URI=None):
        self.type = GenericType(
                        LinkAttributes(
                            link_title,
                            xlink_href = XSDAnyURI( href_URI ) \
                                         if href_URI else None
                        ),
                        set_ref = XSDAnyURI( set_URI ) \
                                     if set_URI else None
                    )
    def set_certainty(self, certainty):
        self.certainty = certainty
    def set_quality(self, quality):
        self.quality = quality
    def build(self):
        if self.name_content:
            name_content = self.name_content if len(self.name_content) > 1  \
                                             else self.name_content[0]
            return TimeContentSingle(GenericName(name_content),
                                    type_     = self.type,
                                    certainty = self.certainty,
                                    quality   = self.quality)
        else:
            return TimeContentSingle(self.time_content,
                                    type_     = self.type,
                                    certainty = self.certainty,
                                    quality   = self.quality)



class TimeBuilder(PrincipalElementBuilder):
    """
    Interface for constructing a XOBIS Time (instance) principal element.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_qualifier, set_type, set_role
    # ADDITIONAL: set_time_content, set_calendar
    def __init__(self):
        super().__init__()
        self.time_content = None
        self.calendar = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("Time element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("Time element does not have qualifiers")
    def set_type(self, *args, **kwargs):
        raise AttributeError("Time element does not have property 'type'")
    def set_role(self, *args, **kwargs):
        raise AttributeError("Time element does not have property 'role'")
    def set_time_content(self, time_content):
        self.time_content = time_content
    def set_calendar(self, link_title, set_URI, href_URI=None):
        self.calendar = Calendar(
                            LinkAttributes(
                                link_title,
                                xlink_href = XSDAnyURI( href_URI ) \
                                             if href_URI else None
                            ),
                            set_ref = XSDAnyURI( set_URI )
                        )
    def build(self):
        return Time(
                    TimeInstanceEntry(
                        self.time_content,
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
    Interface for constructing a XOBIS Time (duration) principal element.
    """
    #  METHODS DEVIATION FROM SUPER
    #  ALTERNATE: set_scheme
    #    MISSING: add_name, add_qualifier, set_type, set_role
    # ADDITIONAL: set_time_content1, set_time_content2,
    #             set_calendar, set_calendar1, set_calendar2
    def __init__(self):
        super().__init__()
        self.time_content1 = None
        self.scheme1 = None
        self.calendar1 = None
        self.time_content2 = None
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
    def set_time_content1(self, time_content1, time_content2=None):
        self.time_content1 = TimeContent(time_content1, time_content2)
    def set_time_content2(self, time_content1, time_content2=None):
        self.time_content2 = TimeContent(time_content1, time_content2)
    def set_scheme(self, scheme1, scheme2=""):
        if scheme2 == "":  # use None for no scheme on entry part 2
            scheme2 = scheme1
        self.scheme1, self.scheme2 = scheme1, scheme2
    def set_calendar(self, link_title, set_URI, href_URI=None):
        # Shorthand to set calendars 1 and 2 simultaneously
        self.set_calendar1(link_title, set_URI, href_URI)
        self.calendar2 = self.calendar1
    def set_calendar1(self, link_title, set_URI, href_URI=None):
        self.calendar1 = Calendar(
                             LinkAttributes(
                                 link_title,
                                 xlink_href = XSDAnyURI( href_URI ) \
                                              if href_URI else None
                             ),
                             set_ref = XSDAnyURI( set_URI )
                         )
    def set_calendar2(self, link_title, set_URI, href_URI=None):
        self.calendar2 = Calendar(
                             LinkAttributes(
                                 link_title,
                                 xlink_href = XSDAnyURI( href_URI ) \
                                              if href_URI else None
                             ),
                             set_ref = XSDAnyURI( set_URI )
                         )
    def build(self):
        return Time(
                   TimeDurationEntry(
                       TimeDurationEntryPart(
                           self.time_content1,
                           opt_scheme = OptScheme(self.scheme1),
                           calendar = self.calendar1
                       ),
                       TimeDurationEntryPart(
                           self.time_content2,
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
    #             set_substitute_attribute, add_note
    # ADDITIONAL: set_time_content, set_calendar
    def __init__(self):
        super().__init__()
        self.time_content = None
        self.calendar = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have qualifiers")
    def set_time_or_duration_ref(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not time/duration ref")
    def set_substitute_attribute(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have substitute attributes")
    def add_note(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have notes")
    def set_time_content(self, time_content):
        self.time_content = time_content
    def set_calendar(self, link_title, set_URI, href_URI=None):
        self.calendar = Calendar(
                            LinkAttributes(
                                link_title,
                                xlink_href = XSDAnyURI( href_URI ) \
                                             if href_URI else None
                            ),
                            set_ref = XSDAnyURI( set_URI )
                        )
    def build(self):
        return TimeVariant(
                   TimeInstanceEntry(
                       self.time_content,
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
    #             set_substitute_attribute, add_note
    # ADDITIONAL: set_time_content1, set_time_content1_link,
    #             set_time_content2, set_time_content2_link,
    #             set_calendar, set_calendar1, set_calendar2
    def __init__(self):
        super().__init__()
        self.time_content1_part1 = None
        self.time_content1_part2 = None
        self.time_content1_link_attributes = None
        self.scheme1 = None
        self.calendar1 = None
        self.time_content2_part1 = None
        self.time_content2_part2 = None
        self.time_content2_link_attributes = None
        self.scheme2 = None
        self.calendar2 = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have qualifiers")
    def set_time_or_duration_ref(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not time/duration ref")
    def set_substitute_attribute(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have substitute attributes")
    def add_note(self, *args, **kwargs):
        raise AttributeError("TimeVariant element does not have notes")
    def set_time_content1(self, time_content1, time_content2=None):
        self.time_content1_part1 = time_content1
        self.time_content1_part2 = time_content2
    def set_time_content1_link(self, link_title, href_URI=None):
        self.time_content1_link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
    def set_time_content2(self, time_content1, time_content2=None):
        self.time_content2_part1 = time_content1
        self.time_content2_part2 = time_content2
    def set_time_content2_link(self, link_title, href_URI=None):
        self.time_content2_link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
    def set_scheme(self, scheme1, scheme2=""):
        if scheme2 == "":      # use None for no scheme on entry part 2
            scheme2 = scheme1
        self.scheme1, self.scheme2 = scheme1, scheme2
    def set_calendar(self, link_title, set_URI, href_URI=None):
        # Shorthand to set calendars 1 and 2 simultaneously
        self.set_calendar1(link_title, set_URI, href_URI)
        self.calendar2 = self.calendar1
    def set_calendar1(self, link_title, set_URI, href_URI=None):
        self.calendar1 = Calendar(
                             LinkAttributes(
                                 link_title,
                                 xlink_href = XSDAnyURI( href_URI ) \
                                              if href_URI else None
                             ),
                             set_ref = XSDAnyURI( set_URI )
                         )
    def set_calendar2(self, link_title, set_URI, href_URI=None):
        self.calendar2 = Calendar(
                             LinkAttributes(
                                 link_title,
                                 xlink_href = XSDAnyURI( href_URI ) \
                                              if href_URI else None
                             ),
                             set_ref = XSDAnyURI( set_URI )
                         )
    def build(self):
        return DurationVariant(
                   TimeDurationEntry(
                       TimeDurationEntryPart(
                           TimeContent(self.time_content1_part1,
                                     self.time_content1_part2,
                                     self.time_content1_link_attributes),
                           opt_scheme = OptScheme(self.scheme1),
                           calendar = self.calendar1
                       ),
                       TimeDurationEntryPart(
                           TimeContent(self.time_content2_part1,
                                     self.time_content2_part2,
                                     self.time_content2_link_attributes),
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
    # ADDITIONAL: set_time_content, set_calendar
    def __init__(self):
        super().__init__()
        self.time_content1 = None
        self.time_content2 = None
        self.calendar = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("TimeRef element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("TimeRef element does not have qualifiers")
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("TimeRef element does not have subdivison")
    def set_time_content(self, time_content1, time_content2=None):
        self.time_content1 = time_content1
        self.time_content2 = time_content2
    def set_calendar(self, link_title, set_URI, href_URI=None):
        self.calendar = Calendar(
                            LinkAttributes(
                                link_title,
                                xlink_href = XSDAnyURI( href_URI ) \
                                             if href_URI else None
                            ),
                            set_ref = XSDAnyURI( set_URI )
                        )
    def build(self):
        return TimeRef(
                   TimeContent(self.time_content1,
                             self.time_content2,
                             self.link_attributes),
                   calendar = self.calendar
               )


class DurationRefBuilder(PrincipalElementRefBuilder):
    """
    Interface for constructing a DurationRef.
    """
    #  METHODS DEVIATION FROM SUPER
    #    MISSING: add_name, add_qualifier, add_subdivision_link
    # ADDITIONAL: set_time_content1, set_time_content1_link,
    #             set_time_content2, set_time_content2_link, set_calendar
    def __init__(self):
        super().__init__()
        self.time_content1_part1 = None
        self.time_content1_part2 = None
        self.time_content1_link_attributes = None
        self.calendar1 = None
        self.time_content2_part1 = None
        self.time_content2_part2 = None
        self.time_content2_link_attributes = None
        self.calendar2 = None
    def add_name(self, *args, **kwargs):
        raise AttributeError("DurationRef element does not have names")
    def add_qualifier(self, *args, **kwargs):
        raise AttributeError("DurationRef element does not have qualifiers")
    def add_subdivision_link(self, *args, **kwargs):
        raise AttributeError("DurationRef element does not have subdivision")
    def set_time_content1(self, time_content1, time_content2=None):
        self.time_content1_part1 = time_content1
        self.time_content1_part2 = time_content2
    def set_time_content1_link(self, link_title, href_URI=None):
        self.time_content1_link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
    def set_time_content2(self, time_content1, time_content2=None):
        self.time_content2_part1 = time_content1
        self.time_content2_part2 = time_content2
    def set_time_content2_link(self, link_title, href_URI=None):
        self.time_content2_link_attributes = LinkAttributes(
                                   link_title,
                                   XSDAnyURI(href_URI) if href_URI else None
                               )
    def set_calendar(self, link_title, set_URI, href_URI=None):
        # Shorthand to set calendars 1 and 2 simultaneously
        self.set_calendar1(link_title, set_URI, href_URI)
        self.calendar2 = self.calendar1
    def set_calendar1(self, link_title, set_URI, href_URI=None):
        self.calendar1 = Calendar(
                             LinkAttributes(
                                 link_title,
                                 xlink_href = XSDAnyURI( href_URI ) \
                                              if href_URI else None
                             ),
                             set_ref = XSDAnyURI( set_URI )
                         )
    def set_calendar2(self, link_title, set_URI, href_URI=None):
        self.calendar2 = Calendar(
                             LinkAttributes(
                                 link_title,
                                 xlink_href = XSDAnyURI( href_URI ) \
                                              if href_URI else None
                             ),
                             set_ref = XSDAnyURI( set_URI )
                         )
    def build(self):
        return DurationRef(
                   time_content1 = TimeContent(self.time_content1_part1,
                                           self.time_content1_part2,
                                           self.time_content1_link_attributes),
                   calendar1   = self.calendar1,
                   time_content2 = TimeContent(self.time_content2_part1,
                                           self.time_content2_part2,
                                           self.time_content2_link_attributes),
                   calendar2   = self.calendar2,
                   link_attributes = self.link_attributes
               )
