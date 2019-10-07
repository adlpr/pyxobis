#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pymarc import Field

from pylmldb import LaneMARCRecord
from pylmldb.xobis_constants import *

from . import tf_common_methods as tfcm

from .Indexer import Indexer
from .NameParser import NameParser

from .RelationshipTransformerAut import RelationshipTransformerAut
from .RelationshipTransformerBib import RelationshipTransformerBib
from .RelationshipTransformerHdg import RelationshipTransformerHdg


class RelationshipTransformer:
    """
    Methods for extracting and building Relationship objects
    from pymarc Records.
    """
    def __init__(self):
        # subordinate Transformers
        self.reltaut = RelationshipTransformerAut(self)
        self.reltbib = RelationshipTransformerBib(self)
        self.relthdg = RelationshipTransformerHdg(self)

    def transform_relationships(self, record):
        """
        Delegate transformation to subordinate Transformer.
        """
        element_type = record.get_xobis_element_type()
        if element_type in (WORK_INST, OBJECT):
            return self.reltbib.transform_relationships(record)
        elif element_type == HOLDINGS:
            return self.relthdg.transform_relationships(record)
        return self.reltaut.transform_relationships(record)

    def get_relation_type(self, rel_name):
        rel_types = Indexer.lookup_rel_types(rel_name)
        if len(rel_types) == 1:
            return rel_types[0].lower()
        return None

    def build_ref_from_field(self, field, element_type):
        """
        Build a ref based on a parsable field and its element type.
        Returns a Ref object to serve as the target of a Relationship.
        """
        rb_class = tfcm.ref_builder_map.get(element_type)
        parse_name = NameParser.get_parser_for_element_type(element_type)
        assert rb_class and parse_name, f"invalid element type: {element_type}"
        rb = rb_class()
        # names/qualifiers
        ref_names_and_qualifiers = parse_name(field)
        for ref_name_or_qualifier in ref_names_and_qualifiers:
            if isinstance(ref_name_or_qualifier, dict):
                rb.add_name(**ref_name_or_qualifier)
            else:
                rb.add_qualifier(ref_name_or_qualifier)
        # link attrs
        if not (field.tag in ('700','710') and element_type == WORK_INST): # ignore author-title field works
            rb.set_link(*self.get_linking_info(field, element_type))
        # subdivisions
        if element_type in (CONCEPT, LANGUAGE) and not field.tag.endswith('80'):
            # ^vxyz should always be subdivisions in concept/language fields
            for code, val in field.get_subfields('v','x','y','z', with_codes=True):
                if code == 'x' and element_type == CONCEPT:
                    # CONCEPT ^x (MeSH qualifier) needs special Indexer treatment
                    val_href = Indexer.lookup(Field('650','  ',['x',val]), CONCEPT)
                else:
                    subdiv_element_type = {'v' : CONCEPT,
                                           'x' : LANGUAGE,
                                           'y' : TIME}.get(code, PLACE)
                    val_href = Indexer.simple_lookup(val, subdiv_element_type)
                rb.add_subdivision_link(val,
                                        content_lang = None,
                                        link_title = val,
                                        href_URI = val_href,
                                        substitute = None)
        return rb.build()


    link_field_w = ('130','510','530','730','760','762','765','767',
        '770','772','773','775','776','777','780','785','787','789',
        '830','963')
    link_field_0 = ('100','110','111','500','510','511','550','551',
        '555','580','582','600','610','611','650','651','653','655',
        '700','710','711','748','750','751','987')
    def get_linking_info(self, field, element_type):
        """
        Return a string representation of the authorized heading of the record
        the given field refers to, and the record's control number,
        if there is such a record (if not, generate a representation from the field).
        """
        ctrlno, id_subfs = None, None
        # first try looking up the control number given
        if field.tag in self.link_field_w:
            if 'w' in field:
                ctrlno = field['w']
                if not ctrlno.startswith('('):
                    ctrlno = "(CStL)" + ctrlno
                id_subfs = Indexer.reverse_lookup(ctrlno)
            elif '0' in field:
                ctrlno = field['0']
                if field.tag in self.link_field_0 and not ctrlno.startswith('('):
                    ctrlno = "(CStL)" + ctrlno
                id_subfs = Indexer.reverse_lookup(ctrlno)
        elif field.tag in self.link_field_0 and '0' in field:
            ctrlno = field['0']
            if not ctrlno.startswith('('):
                ctrlno = "(CStL)" + ctrlno
            id_subfs = Indexer.reverse_lookup(ctrlno)
        # if that's invalid, look it up based on the field and try again
        if ctrlno is None or id_subfs is None:
            ctrlno = ctrlno or Indexer.lookup(field, element_type)
            id_subfs = Indexer.reverse_lookup(ctrlno)
        # if still invalid, generate "heading" based on this field
        if ctrlno in (Indexer.UNVERIFIED, Indexer.CONFLICT) or id_subfs is None:
            id_from_field = LaneMARCRecord.get_identity_from_field(field, element_type, normalized=False)
            assert id_from_field, f"ID generation failed for field: {field}"
            id_subfs = id_from_field.split(LaneMARCRecord.UNNORMALIZED_SEP)
        # @@@ this part could be altered to use e.g. ISBD punctuation?
        id_repr = ' '.join(filter(None, id_subfs[1::2]))
        return id_repr, ctrlno


    def extract_enumeration(self, field):
        """
        Returns a StringRef representing an enumeration
        to pass into a RelationshipBuilder, or None.
        """
        enum = None
        if '1' in field:
            enum = str(int(''.join(d for d in field['1'] if d.isdigit())))
        elif field.tag in ('551','651') and '6' in field:
            enum = str(int(''.join(d for d in field['6'] if d.isdigit())))
        elif field.tag in ('100','110','111'):
            enum = '1'
        return tfcm.build_simple_ref(enum, STRING) if enum else None
