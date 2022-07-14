#!/usr/bin/env python3

##########################################
#
# supplementary_planes.py
#
#   This script has been developed to facilitate importing and exporting
#   MARC21 records to or from Voyager systems where the Oracle database
#   is using CESU-8.
#
#   The script is only needed when characters outside the Basic Multilingual Plane
#   are present in the exported records.
#
#   The script converts MARC records from CESU-8 to UTF-8 after exporting records, or
#   from UTF-8 to CESU-8 before importing records.
#
#   Batch exports from Voyager will be in the encoding used in the Oracle DB.
#
# Copyright 2021 Enabling Languages
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##########################################

import argparse, os, sys, html, json
from pymarc import MARCReader, TextWriter, exceptions as exc
try:
    import regex as re
except ImportError:
    import re
import rdflib
from lxml import etree
SCRIPT_DIR = os.path.dirname(os.path.abspath("./normalise_conf.py"))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import normalise_conf

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def main():
    # Command line arguments
    parser = argparse.ArgumentParser(description='Apply a normalisation form to a MARC file.')
    # Input file (Binary MARC file *.mrc) to be converted
    parser.add_argument('-i', '--input', type=str, required=True, help='File to be normalised.')
    # Parse the argument, minimal debugging information on conversion of 880 fields.
    parser.add_argument('-d', '--debug', action="store_true", required=False, help='Display dotted forms of 100 and 245 fields during processing.')
    # Output formats
    parser.add_argument('-t', '--text', action="store_true", required=False, help='Output a text MARC (*.mrk) file.')

    # Parse the argument
    args = parser.parse_args()


    # Process CLI arguments
    debug = False
    if args.debug:
        debug = True

    in_file = os.path.abspath(args.input)
    filename, file_extension = os.path.splitext(in_file)

    out_mrc_file = filename + "_norm" + ".mrc"
    if args.text:
        out_txt_file = filename + "_norm" + ".mrk"

    converted_marc_records = []
    with open('data/vi1.mrc', 'rb') as fh:
        reader = MARCReader(fh)
        for record in reader:
            if record:
                # consume the record:
                for record_field in record.get_fields(*TARGET_FIELDS):
                    if record_field['a']:
                        req_subfield = "a"
                        req_subfields = ["a", "b", "c"]
                        for sf in req_subfields:
                            if record_field[sf]:
                                # record_field[sf] =  elu.add_dotted_circle(elu.normalise(NORMALISATION_FORM, record_field[sf]))
                                record_field[sf] = elu.normalise(NORMALISATION_FORM, record_field[sf])
            elif isinstance(reader.current_exception, exc.FatalReaderError):
                # data file format error
                # reader will raise StopIteration
                print(reader.current_exception)
                print(reader.current_chunk)
            else:
                # fix the record data, skip or stop reading:
                print(reader.current_exception)
                print(reader.current_chunk)
                # break/continue/raise
                continue
            converted_marc_records.append(record)


        if debug:
            print(record.leader)
            if record['100']:
                print(record['100'])

        converted_marc_records.append(r)

    with open(out_mrc_file , 'wb') as data:
        for record in converted_marc_records:
            data.write(record.as_marc())

    #
    # Convert to a text MARC file (.mrk)
    #

    if args.text:
        reader3 = MARCReader(open(out_mrc_file, 'rb'), force_utf8=False, to_unicode=True)
        writer3 = TextWriter(open(out_txt_file,'wt'))
        for record in reader3:
            #print(record)
            writer3.write(record)
        writer3.close()
        reader3.close()

if __name__ == '__main__':
    main()
