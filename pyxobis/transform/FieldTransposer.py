#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# import re

import pickle, time

from tqdm import tqdm
from loguru import logger

from pymarc import Field, Record

from pylmldb import LMLDB, LaneMARCRecord

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
            #   { LaneMARCRecord.BIB : { target_record_ctrlno : [pymarc Field, Field, ...], ... },
            #     LaneMARCRecord.AUT : [pymarc Record, Record, ...] }
            self.map = {}
            with LMLDB() as db:
                self.__generate_hdgs_from_auts(db)
                self.__add_hdgs_fields_from_bibs(db)
            with self.FIELD_TRANSPOSER_MAP_FILE.open('wb') as outf:
                pickle.dump(self.map, outf)


    def __add_hdgs_fields_from_bibs(self, db):
        logger.info("generating fields to transpose from bib to hdgs")
        self.map[LaneMARCRecord.BIB] = {}
        # for each bib
        hdg_ctrlnos_all = []
        bib_fields_to_move_map = {}
        logger.info("pulling fields and holdings IDs from bibs")
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
        logger.info("reading hdgs types")
        hdgs_type_map = {}
        for hdg_ctrlno, hdg_record in tqdm(db.get_hdgs(hdg_ctrlnos_all)):
            hdgs_type_map[hdg_ctrlno] = hdg_record.get_holdings_type()

        # finally, match each field to the appropriate hdg id it should move to
        logger.info("aligning bib fields to hdgs")
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
                if hdg_ctrlno_prefixed not in self.map[LaneMARCRecord.BIB]:
                    self.map[LaneMARCRecord.BIB][hdg_ctrlno_prefixed] = []
                # callno_and_alt_id_fields : all alt ID fields ok for all associated hdgs
                self.map[LaneMARCRecord.BIB][hdg_ctrlno_prefixed].extend(callno_and_alt_id_fields)
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
                if hdg_type != LaneMARCRecord.DIGITAL:
                    self.map[LaneMARCRecord.BIB][hdg_ctrlno_prefixed].extend(note_title_level_data_fields)


    def __generate_hdgs_from_auts(self, db):
        logger.info("generating ad-hoc hdgs linked to (Work) auts")
        self.map[LaneMARCRecord.AUT] = []
        for aut_ctrlno, aut_record in tqdm(db.get_auts()):
            fields_to_move = [field for field in aut_record.get_fields('856') if field.indicator2 in '01']
            has_url = any(fields_to_move)
            fields_to_move.extend(aut_record.get_fields('907'))
            if not any(fields_to_move):
                continue
            fields_to_move.append(Field('001',data=f"Z{aut_ctrlno}"))
            fields_to_move.append(Field('004',data=f"Z{aut_ctrlno}"))
            now = time.strftime('%Y%m%d%H%M%S.0')
            fields_to_move.append(Field('005',data=now))
            fields_to_move.append(Field('008',data=f'{now[2:8]}uu    8   0000uuund0000000'))
            fields_to_move.append(Field('852','  ',['b','EDATA' if has_url else 'NOITEM']))
            hdg_record = Record()
            hdg_record.add_field(*fields_to_move)
            self.map[LaneMARCRecord.AUT].append(hdg_record)


    def get_transposed_fields(self, target_record_ctrlno):
        return self.map[LaneMARCRecord.BIB].get(target_record_ctrlno, [])

    def get_ad_hoc_hdgs(self, batch_size=0):
        if batch_size > 0:
            for i in range(0, len(self.map[LaneMARCRecord.AUT]), batch_size):
                yield [(record['001'].data, record) for record in self.map[LaneMARCRecord.AUT][i:i+batch_size]]
        else:
            for record in self.map[LaneMARCRecord.AUT]:
                yield record['001'].data, record
