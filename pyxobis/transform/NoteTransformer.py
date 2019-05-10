#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from .tf_constants import *

from .NoteTransformerAut import NoteTransformerAut
from .NoteTransformerBib import NoteTransformerBib

class NoteTransformer:
    """
    Methods for extracting and building Note objects from pymarc Records.
    """
    def __init__(self):
        # subordinate Transformers
        self.ntaut = NoteTransformerAut()
        self.ntbib = NoteTransformerBib()

    def transform_notes(self, record):
        """
        Delegate transformation to subordinate Transformer.
        """
        if record.get_xobis_element_type() in (WORK_INST, OBJECT):
            return self.ntbib.transform_notes(record)
        return self.ntaut.transform_notes(record)
