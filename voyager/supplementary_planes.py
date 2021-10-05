#!/usr/bin/env python

##########################################
#
# supplementary_planes.py
#
#   This script has been developed to facilitate importing and exporting
#   MARC21 records to or from Voyager systems where the Oracle database
#   set is UTF8, using the encoding CESU-8.
#
#   The script is only needed when characters outside the Basic Multilingual Plane
#   are present in any of the exported records.
#
#   The script converts MARC records from CESU-8 to UTF-8 after exporting records, or
#   from UTF-8 to CESU-8 before importing records.
#
#   Batch exports from Voyager wll be in the encoding used in the Oracle DB.
#
# Usage:
#   To convert a CESU-8 file to UTF-8
#     ./supplementary_planes.py -i Bulk_Export.mrc -o Bulk_Export_utf8.mrc
#
#   To convert an UTF-8 file to CESU-8
#     ./supplementary_planes.py -i Bulk_Import.mrc -o Bulk_Import_cesu8.mrc -r
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

import pymarc, argparse, os, sys, html
try:
    import regex as re
except ImportError:
    import re
import codecs
SCRIPT_DIR = os.path.dirname(os.path.abspath("./cesu8.py"))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import cesu8

def main():
    # Command line arguments
    parser = argparse.ArgumentParser(description='Convert MARC records with SMP characters in MARC-8 and CESU-8 to UTF-8. Currently only supports ADlam in records.')

    # Input file ot be converted
    parser.add_argument('-i', '--input', type=str, required=True, help='File to be converted.')
    # Outputfile
    parser.add_argument('-o', '--output', type=str, required=False, help='Output file.')
    # Mode: use CESU-8 (default) or MARC-8 processing
    parser.add_argument('-m', '--mode', type=str, required=False, help='Mode used for processing the MARC record. Values are cesu-8 and marc-8')
    # Reverse (read in a UTF-8 file, output a CESU-8 file. ONly available for CESU-8 mode.)
    parser.add_argument('-r', '--reverse', action="store_true", required=False, help='Reverse (convert UTF-8 to CESU-8)')
    # Parse the argument
    parser.add_argument('-d', '--debug', action="store_true", required=False, help='Display 880 field during processing.')
    # Parse the argument
    args = parser.parse_args()

    # Process arguments
    debug = False
    if args.debug:
        debug = True

    reverse = False
    if args.reverse:
        reverse = True
    if args.mode:
        mode = args.mode
    else:
        mode = "cesu-8"

    in_file = os.path.abspath(args.input)

    if args.output:
        out_file = os.path.abspath(args.output)
    else:
        filename, file_extension = os.path.splitext(in_file)
        if reverse == True:
            out_file = filename + "_cesu8" + file_extension
        else:
            out_file = filename + "_utf8" + file_extension
    if mode == "cesu-8":
        reader = pymarc.MARCReader(open(in_file, 'rb'), force_utf8=False, to_unicode=False)
    else:
        reader = pymarc.MARCReader(open(in_file, 'rb'), force_utf8=False, to_unicode=True)

    converted_marc_records = []

    for r in reader:
        if debug:
            print("\n")
            print(r.leader)
            if r['880']:
                print(r['880'])
            print("\n")
        if mode == "cesu-8" and reverse == False:
            for f in r.get_fields('880'):
                if f['a']:
                    f['a'] = f['a'].decode("cesu-8").encode("utf-8")
                if f['b']:
                    f['b'] = f['b'].decode("cesu-8").encode("utf-8")
                if f['c']:
                    f['c'] = f['c'].decode("cesu-8").encode("utf-8")
        elif mode == "cesu-8" and reverse == True:
            for f in r.get_fields('880'):
                if f['a']:
                    f['a'] = f['a'].decode("utf-8").encode("cesu-8")
                if f['b']:
                    f['b'] = f['b'].decode("utf-8").encode("cesu-8")
                if f['c']:
                    f['c'] = f['c'].decode("utf-8").encode("cesu-8")
        elif mode == "marc-8":
            r.leader = r.leader[:9] + 'a' + r.leader[10:]
            lang = [r['008'].value()[35:38]]
            if r["041"]:
                for s in r['041'].get_subfields('a', 'h', 'j'):
                    lang.append(s)
            ful = True if "ful" in lang else False
            rhg = True if "rhg" in lang else False
            if ful:
                for f in r.get_fields('880'):
                    if f['a'] and ("&#xe" in f['a']):
                        f['a'] = re.sub(r'&#xe', '&#x1e', f['a'])
                        f['a'] = html.unescape(f['a'])
                    if f['b'] and ("&#xe" in f['b']):
                        f['b'] = re.sub(r'&#xe', '&#x1e', f['b'])
                        f['b'] = html.unescape(f['b'])
                    if f['c'] and ("&#xe" in f['c']):
                        f['c'] = re.sub(r'&#xe', '&#x1e', f['c'])
                        f['c'] = html.unescape(f['c'])
            if rhg:
                for f in r.get_fields('880'):
                    if f['a'] and ("&#x0d" in f['a']):
                        f['a'] = re.sub(r'&#x0d', '&#x10d', f['a'])
                        f['a'] = html.unescape(f['a'])
                    if f['b'] and ("&#x0d" in f['b']):
                        f['b'] = re.sub(r'&#x0d', '&#x10d', f['b'])
                        f['b'] = html.unescape(f['b'])
                    if f['c'] and ("&#x0d" in f['c']):
                        f['c'] = re.sub(r'&#x0d', '&#x10d', f['c'])
                        f['c'] = html.unescape(f['c'])

        if debug:
            print(r.leader)
            if r['880']:
                print(r['880'])
            if mode == "cesu-8" and reverse == False:
                if r['880']['a']:
                    print(r['880']['a'].decode("utf-8"))
                if r['880']['b']:
                    print(r['880']['b'].decode("utf-8"))
                if r['880']['c']:
                    print(r['880']['c'].decode("utf-8"))
            elif mode == "cesu-8" and reverse == True:
                if r['880']['a']:
                    print(r['880']['a'].decode("cesu-8"))
                if r['880']['b']:
                    print(r['880']['b'].decode("cesu-8"))
                if r['880']['c']:
                    print(r['880']['c'].decode("cesu-8"))

        converted_marc_records.append(r)

    with open(out_file , 'wb') as data:
        for record in converted_marc_records:
            data.write(record.as_marc())


# Usage:
#     ./supplementary_planes.py -i smp_records.mrc -o smp+records_utf8.mrc

if __name__ == '__main__':
    main()
