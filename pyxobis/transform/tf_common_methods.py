#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Static methods to share across different types of Transformer objects
"""

import regex as re
from lxml import etree

from pylmldb import LaneMARCRecord
from pylmldb.xobis_constants import *

from ..builders import *

from .Indexer import Indexer
from .DateTimeParser import DateTimeParser


def xmlpp(element):
    """
    XML pretty print, for debug
    """
    print(etree.tounicode(element, pretty_print=True))


def concat_subfs(field, with_codes=True):
    """
    Concatenate subfields where strict subfield preservation desirable
    Cannot use \x1f (actual subf separator) due to "XML compatibility"
    """
    if with_codes:
        return ' '.join(f'‡{code} {val}' for code, val in zip(field.subfields[::2],field.subfields[1::2]))
    return ' '.join(field.subfields[1::2])



def get_field_chronology(field):
    """
    Extract chronology of variant type or relation from field (typically subfs 8/9).
    Returns a Time/Duration Ref object.
    """
    type_time_or_duration_ref = None

    # Time or Duration
    if field.tag not in ['150','180','450','480']:  # exceptions for MeSH style fields
        if field.tag in ['650','651','655'] and '7' in field:  # ^7 is start time rather than ID
            start_type_datetime, end_type_datetime = field['7'], field['8'] or field['9']
        else:
            start_type_datetime, end_type_datetime = field['8'], field['9']
        type_datetime = start_type_datetime + end_type_datetime  \
                        if start_type_datetime and end_type_datetime  \
                        else end_type_datetime or start_type_datetime
        if type_datetime:
            type_time_or_duration_ref = DateTimeParser.parse_as_ref(type_datetime, element_type=None)

    return type_time_or_duration_ref


def get_type_and_time_from_relator(field):
    """
    For both Variants and Being main entries, the ^e/^i "relator"
    and its time/duration qualifiers ^8 and ^9 aren't specifying an actual
    relationship, but rather a "type" of entry.

    Returns a Type kwarg dict and a Time/Duration Ref object,
    for use in a VariantBuilder or BeingBuilder.
    """
    type_kwargs = {}

    # Entry Type
    # Valid variant types include any Equivalence relationship concepts
    if field.tag in LaneMARCRecord.RELATOR_SUBF_i_TAGS:
        # exceptions where ^e has other uses
        entry_type = field['i']
    else:
        entry_type = field['e']
    if entry_type and not entry_type.startswith('Includes'):
        entry_type = entry_type.rstrip(':').strip()
        type_kwargs = { 'link_title' : entry_type,
                        'set_URI'    : Indexer.simple_lookup("Equivalence", CONCEPT),
                        'href_URI'   : Indexer.simple_lookup(entry_type, RELATIONSHIP) }

    return type_kwargs, get_field_chronology(field)


def normalize_place(placestring):
    """
    Normalize a Place string for lookup.
    """
    # Various preprocessing normalization
    # Punctuation
    ps = re.sub(r"\s*\)\s*\.+$", ')', placestring).rstrip("،,:;/ \t").strip()
    ps = re.sub(r"^[\s\(]+((?:[^\(\)]|\([^\(\)]*\))+)[\s\)]+$", r"\1", ps).strip()
    ps = re.sub(r"^[\(]((?:[^\(\)]|\([^\(\)]*\))+)$", r'\1', ps).strip()
    ps = re.sub(r"^((?:[^\(\)]|\([^\(\)]*\))+)[\)]$", r'\1', ps).strip()

    # Abbreviations
    ps = re.sub(r" +N\.?Y\.?([ ,;:/]|$)", r" New York\1", ps)
    ps = re.sub(r" +Calif\.?([ ,;:/]|$)", r" California\1", ps)
    ps = re.sub(r" +Wash\.?([ ,;:/]|$)", r" Washington\1", ps)

    # Misspellings
    ps = re.sub(r"Phillippines", r"Philippines", ps)

    # Qualifications
    ps = re.sub(r"New York, New York(?! \()", "New York, New York (State)", ps)

    return ps if ps else None


ref_builder_map = {
    WORK_INST    : WorkRefBuilder,
    WORK_AUT     : WorkRefBuilder,
    BEING        : BeingRefBuilder,
    CONCEPT      : ConceptRefBuilder,
    RELATIONSHIP : ConceptRefBuilder,
    EVENT        : EventRefBuilder,
    LANGUAGE     : LanguageRefBuilder,
    OBJECT       : ObjectRefBuilder,
    ORGANIZATION : OrganizationRefBuilder,
    PLACE        : PlaceRefBuilder,
    STRING       : StringRefBuilder
}
def build_simple_ref(name, element_type):
    """
    Build a ref based on only a single name string and its element type.
    """
    if element_type == TIME:
        # use DTP for time/duration instead
        return DateTimeParser.parse_as_ref(name)
    rb_class = ref_builder_map.get(element_type)
    assert rb_class, f"invalid element type: {element_type}"
    rb = rb_class()
    rb.set_link(name, Indexer.simple_lookup(name, element_type))
    rb.add_name(name)
    return rb.build()
