#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re

class EntryStringFormatter:
    """
    Methods for constructing the canonical plaintext form of a transformed
    record entry, to server as a human-readable identifier for that record.

    ** Expects BeautifulSoup4 Tag elements as input!! **

    (can't this be rewritten to accept tf'd Record obj instead??)

    [originally ported from xsl transformations written for lmldbx]
    """

    @classmethod
    def format_entry_str(cls, entry_tag):
        entry_str_segments = []
        if entry_tag.parent.name == 'time':
            # <time> <entry>
            entry_str_segments.append(cls.format_time_content_single_str(entry_tag))
            # optional calendar
            calendar = entry_tag.find('calendar')
            if calendar:
                entry_str_segments.append(calendar.get_text())
        elif entry_tag.parent.name == 'duration':
            # there are none of these getting converted from the MARC
            # and also this is currently undefined in the xsl...
            ...
            ...
            ...
        elif entry_tag.parent.name == 'holdings':
            # entry-level work/obj + concept, and qualifiers
            for child in entry_tag.children:
                if child.name == 'qualifiers':
                    entry_str_segments.append(cls.format_qualifiers_str(child))
                else:
                    # work or concept
                    entry_str_segments.append(cls.format_ref_element_str(child))
                entry_str_segments.append('·')
        elif entry_tag.find_all('name', recursive=False):
            # <entry> with typical <name>
            for child in entry_tag.children:
                if child.name in ('name','pos'):
                    entry_str_segments.append(cls.format_name_str(child))
                else:
                    entry_str_segments.append(cls.format_qualifiers_str(child))
                entry_str_segments.append('·')
        else:
            # no <name> indicates a <work> <entry> with interleaved <part>s and <qualifers>s
            for child in entry_tag.children:
                if child.name == 'part':
                    entry_str_segments.append(child.get_text().strip())
                else:
                    entry_str_segments.append(cls.format_qualifiers_str(child))
                entry_str_segments.append('·')
        entry_str = re.sub(r'\s\s+', ' ', ' '.join(entry_str_segments).strip(' ·'))
        return entry_str

    @staticmethod
    def format_name_str(name_tag):
        parts = name_tag.find_all('part')

        # simple <name>
        if not parts:
            return name_tag.get_text().strip()

        # name with <part>s
        name_part_strs = []
        for i, part in enumerate(parts):
            part_str = part.get_text().strip()
            # if first part, and a surname, append a comma
            if i==0 and part['type'] == 'surname':
                part_str += ','
            # put parens around expansions
            elif part['type'] == 'expansion':
                part_str = f'({part_str})'
            name_part_strs.append(part_str)
        name_str = re.sub(r'\s\s+', ' ', ' '.join(name_part_strs).strip())
        return name_str


    @classmethod
    def format_qualifiers_str(cls, qualifiers_tag):
        return ' · '.join(cls.format_ref_element_str(ref_tag) for ref_tag in qualifiers_tag.children)


    @classmethod
    def format_ref_element_str(cls, ref_tag):
        ref_str_segments = []
        if ref_tag.name == 'time':
            # time
            parts = ref_tag.find_all('part')
            if parts:
                # dual date separated by slash
                ref_str_segments.append('/'.join(cls.format_time_content_single_str(part) for part in parts))
            else:
                # single time content
                ref_str_segments.append(cls.format_time_content_single_str(ref_tag))
            # calendar
            calendar = ref_tag.find('calendar')
            if calendar:
                ref_str_segments.append(calendar.get_text())
        elif ref_tag.name == 'duration':
            # duration
            # just two Time Refs separated by an en dash
            time_ref_1, time_ref_2 = ref_tag.find_all('time')
            return f"{cls.format_ref_element_str(time_ref_1)}–{cls.format_ref_element_str(time_ref_2)}"
        else:
            # other
            for child_tag in ref_tag.children:
                if child_tag.name in ('name','part'):
                    ref_str_segments.append(cls.format_name_str(child_tag))
                else:
                    ref_str_segments.append(cls.format_qualifiers_str(child_tag))
                ref_str_segments.append('·')
        ref_str = re.sub(r'\s\s+', ' ', ' '.join(ref_str_segments).strip(' ·'))
        return ref_str

    @classmethod
    def format_time_content_single_str(cls, time_content_single):
        if time_content_single.name:
            return cls.format_name_str(time_content_single)

        # tcs_str_segments = []
        # tcs_str = re.sub(r'\s\s+', ' ', ''.join(tcs_str_segments).strip())

        tcs_str = ''

        year = time_content_single.find('year')
        month = time_content_single.find('month')
        day = time_content_single.find('day')
        hour = time_content_single.find('hour')
        minute = time_content_single.find('minute')
        second = time_content_single.find('second')
        millisecond = time_content_single.find('millisecond')
        tzHour = time_content_single.find('tzHour')
        tzMinute = time_content_single.find('tzMinute')

        if year:
            tcs_str += year.get_text()
        elif month or day:
            tcs_str += '-'
        if month:
            tcs_str += '-' + month.get_text().strip().zfill(2)
            if day:
                tcs_str += '-' + day.get_text().strip().zfill(2)
        elif day:
            tcs_str += '-' + day.get_text().strip().zfill(3)
        if any((hour, minute, second, millisecond, tzHour, tzMinute)):
            tcs_str += 'T'
            if hour:
                tcs_str += hour.get_text().strip().zfill(2)
            if any((minute, second, millisecond)):
                tcs_str += ':'
                if minute:
                    tcs_str += minute.get_text().strip().zfill(2)
                if second or millisecond:
                    tcs_str += ':'
                    if second:
                        tcs_str += second.get_text().strip().zfill(2)
                    if millisecond:
                        tcs_str += '.' +  millisecond.get_text().strip().zfill(3)
            if tzHour and tzMinute and tzHour.get_text().strip()==tzMinute.get_text().strip()=='0':
                tcs_str += 'Z'
            else:
                if tzHour:
                    tzHour_str = tzHour.get_text().strip()
                    if tzHour_str.startswith('-'):
                        tcs_str += tzHour_str.zfill(3)
                    else:
                        tcs_str += '+' + tzHour_str.zfill(2)
                    if tzMinute:
                        tcs_str += ':' + tzMinute.get_text().strip().zfill(2)
                elif tzMinute:
                    tcs_str += '+00:' +  tzMinute.get_text().strip().zfill(3)

        certainty = time_content_single['certainty']
        if certainty == 'implied':
            tcs_str = f"[{tcs_str}]"
        elif certainty == 'estimated':
            tcs_str = f"{tcs_str}?"
        elif certainty == 'approximate':
            tcs_str = f"approximately {tcs_str}"

        return tcs_str
