#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# import re

import pickle
from tqdm import tqdm

from lmldb import LMLDB, LaneMARCRecord

from .Indexer import Indexer

class FieldTransposer:
    """
    Carries fields between records (specifically from bib/aut to hdg)
    """

    # file path for pickle
    FIELD_TRANSPOSER_MAP_FILE = Indexer.INDEX_DIR / "field_transposer_map.pickle"

    def __init__(self):
        try:
            with self.FIELD_TRANSPOSER_MAP_FILE.open('rb') as inf:
                self.map = pickle.load(inf)
        except:
            # with access to LMLDB, creates dict of format:
            #   { target_record_ctrlno : [Field, Field, ...], ... }
            self.map = {}
            with LMLDB() as db:
                self.__add_hdgs_fields_from_bibs(db)
            with self.FIELD_TRANSPOSER_MAP_FILE.open('wb') as outf:
                pickle.dump(self.map, outf)

    def __add_hdgs_fields_from_bibs(self, db):
        print("generating fields to transpose from bib to hdgs")
        # for each bib
        hdg_ctrlnos_all = []
        bib_fields_to_move_map = {}
        print("pulling fields and holdings IDs from bibs")
        for bib_ctrlno, bib_record in tqdm(db.get_bibs()):
            # does it have fields to move?
            callno_and_alt_id_fields = bib_record.get_fields('050','060','086')
            # note_unknown_fields = bib_record.get_fields('506','905')
            note_unknown_fields = []
            # note_serhold_fields = bib_record.get_fields('953')
            note_title_level_data_fields = bib_record.get_fields('992','993')
            field_sets_to_move = (callno_and_alt_id_fields, note_unknown_fields, note_title_level_data_fields)
            # field_sets_to_move = (callno_and_alt_id_fields, note_unknown_fields, note_serhold_fields, note_title_level_data_fields)
            if not any(field_sets_to_move):
                continue
            # get holdings control numbers to look up
            hdg_ctrlnos = Indexer.get_hdgs_for_bib(bib_ctrlno)
            # for looking up holdings types all at once
            hdg_ctrlnos_all.extend(hdg_ctrlnos)
            # add fields to temporary map
            bib_fields_to_move_map[bib_ctrlno] = (hdg_ctrlnos, field_sets_to_move)

        # map holdings IDs to types
        print("reading hdgs types")
        hdgs_type_map = {}
        for hdg_ctrlno, hdg_record in tqdm(db.get_hdgs(hdg_ctrlnos_all)):
            hdgs_type_map[hdg_ctrlno] = hdg_record.get_holdings_type()

        # finally, match each field to the appropriate hdg id it should move to
        print("aligning bib fields to hdgs")
        for bib_ctrlno, bib_data in tqdm(bib_fields_to_move_map.items()):
            hdg_ctrlnos, field_sets_to_move = bib_data
            callno_and_alt_id_fields, note_unknown_fields, note_title_level_data_fields = field_sets_to_move
            # callno_and_alt_id_fields, note_unknown_fields, note_serhold_fields, note_title_level_data_fields = field_sets_to_move
            # categorize serhold notes by format in $f
            # note_serhold_fields_format_none, note_serhold_fields_format_phys, note_serhold_fields_format_digi = [], [], []
            # for note_serhold_field in note_serhold_fields:
            #     # Format: print = ta; text = tu; digital = cr (2 char) (NR)
            #     if 'f' not in note_serhold_field:
            #         note_serhold_fields_format_none.append(note_serhold_field)
            #     elif note_serhold_field['f'].startswith('c'):
            #         note_serhold_fields_format_digi.append(note_serhold_field)
            #     else:
            #         note_serhold_fields_format_phys.append(note_serhold_field)
            for hdg_ctrlno in hdg_ctrlnos:
                hdg_type = hdgs_type_map.get(hdg_ctrlno)
                hdg_ctrlno_prefixed = f'(CStL)H{hdg_ctrlno}'
                if hdg_ctrlno_prefixed not in self.map:
                    self.map[hdg_ctrlno_prefixed] = []
                # callno_and_alt_id_fields : all alt ID fields ok for all associated hdgs
                self.map[hdg_ctrlno_prefixed].extend(callno_and_alt_id_fields)
                # note_unknown_fields : ?????????
                ...
                ...
                ...
                # note_serhold_fields : depends on hdg format
                # self.map[hdg_ctrlno_prefixed].extend(note_serhold_fields_format_none)
                # if hdg_type == LaneMARCRecord.DIGITAL:
                #     self.map[hdg_ctrlno_prefixed].extend(note_serhold_fields_format_digi)
                # else:
                #     self.map[hdg_ctrlno_prefixed].extend(note_serhold_fields_format_phys)
                # note_title_level_data_fields : physical only
                if hdg_type == LaneMARCRecord.PHYSICAL:
                    self.map[hdg_ctrlno_prefixed].extend(note_title_level_data_fields)


    def get_transposed_fields(self, target_record_ctrlno):
        return self.map.get(target_record_ctrlno, [])
