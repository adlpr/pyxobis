#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re

class EntryStringFormatter:
    """
    Methods for constructing the canonical plaintext form of a transformed
    record entry, to server as a human-readable identifier for that record.

    [originally ported from xsl transformations written for lmldbx]
    """

    @classmethod
    def format_entry_str(cls, entry_tag):
        entry_str_segments = []

        if entry_tag.parent.name in ['time','duration']:
            # <time> or <duration> <entry>
            """
            <!-- Time/Duration main entry -->
            <xsl:template match="/xobis:record/xobis:time/xobis:entry">
              <h1><xsl:call-template name="time-entry"/></h1>
            </xsl:template>

            <xsl:template match="/xobis:record/xobis:duration/xobis:entry">
              <h1><xsl:call-template name="duration-entry"/></h1>
            </xsl:template>
            """
            ...
            ...
            ...
        elif entry_tag.find_all('name', recursive=False):
            # print("entry with child name")
            # <entry> with typical <name>
            for child in entry_tag.children:
                if child.name == 'name':
                    entry_str_segments.append(cls.format_name_str(child))
                else:
                    entry_str_segments.append(cls.format_qualifiers_str(child))
                entry_str_segments.append('·')
        else:
            # print("entry without child name")
            # no <name> indicates a <work> <entry> with interleaved <part>s and <qualifers>s
            for child in entry_tag.children:
                if child.name == 'part':
                    entry_str_segments.append(child.get_text().strip())
                else:
                    entry_str_segments.append(cls.format_qualifiers_str(qualifiers))
                entry_str_segments.append('·')

        entry_str = re.sub(r'\s\s+', ' ', ' '.join(entry_str_segments).strip(' ·'))

        print(entry_str)

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
        return ' · '.join(cls.format_ref_element(ref_tag) for ref_tag in qualifiers_tag.children)


    @classmethod
    def format_ref_element(cls, ref_tag):
        return '...'
