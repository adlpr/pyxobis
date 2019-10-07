#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from pylmldb.xobis_constants import *

from .NoteTransformerAut import NoteTransformerAut
from .NoteTransformerBib import NoteTransformerBib
from .NoteTransformerHdg import NoteTransformerHdg

class NoteTransformer:
    """
    Methods for extracting and building Note objects from pymarc Records.
    """
    def __init__(self):
        # subordinate Transformers
        self.ntaut = NoteTransformerAut()
        self.ntbib = NoteTransformerBib()
        self.nthdg = NoteTransformerHdg()

    def transform_notes(self, record):
        """
        Delegate transformation to subordinate Transformer.
        """
        element_type = record.get_xobis_element_type()
        if element_type in (WORK_INST, OBJECT):
            return self.ntbib.transform_notes(record)
        elif element_type == HOLDINGS:
            return self.nthdg.transform_notes(record)
        return self.ntaut.transform_notes(record)
