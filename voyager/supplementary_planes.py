#!/usr/bin/env python

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
#   Batch exports from Voyager wll be in the encoding used in the Oracle DB.
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

import pymarc, argparse, os, sys, html, json
try:
    import regex as re
except ImportError:
    import re
import rdflib
from lxml import etree
import codecs
SCRIPT_DIR = os.path.dirname(os.path.abspath("./cesu8.py"))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import cesu8

def xsl_transformation(xslfile, xmlfile = None, xmlstring = None, params={}):
    xslt_tree = etree.parse(xslfile)
    transform = etree.XSLT(xslt_tree)
    xml_contents = xmlstring
    if not xml_contents:
        if xmlfile:
            xml_contents = etree.parse(xmlfile)
    result = transform(xml_contents, **params)
    return result

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

# Supported RDF file formats.
# Dictionary key is format value accepted by value is a 
# tuple consisting of file extension, mimetype and label 
# for the format.
rdf_formats = {
    "turtle": (".ttl", "text/turtle", "Turtle"),
    "nt": (".nt", "application/n-triples", "N-Triples"),
    "nquads": (".nq", "application/n-quads", "N-Quads"),
    "json-ld": (".jsonld", "application/ld+jso", "JSON-LD"),
    "n3": (".n3", "text/n3;charset=utf-8", "Notation3"),
    "trix": (".xml", "text/xml", "TriX (Triples in XML) ")
}

def main():
    # Command line arguments
    parser = argparse.ArgumentParser(description='Convert CESU-8 encoded MARC records with SMP characters to UTF-8. Repair and convert MARC-8 records with Adlam and Hanifi Rohingya.')
    # Input file (Binary MARC file *.mrc) to be converted
    parser.add_argument('-i', '--input', type=str, required=True, help='File to be converted.')
    # Mode: use CESU-8 (default) or MARC-8 processing
    parser.add_argument('-m', '--mode', type=str, required=False, help='Mode used for processing the MARC record. Valid values: cesu-8, marc-8')
    # Reverse (read in a UTF-8 file, output a CESU-8 file. ONly available for CESU-8 mode.)
    parser.add_argument('-r', '--reverse', action="store_true", required=False, help='Reverse (convert UTF-8 to CESU-8)')
    # Parse the argument, minimal debugging information on conversion of 880 fields.
    parser.add_argument('-d', '--debug', action="store_true", required=False, help='Display 880 field during processing.')
    # Output formats
    parser.add_argument('-t', '--text', action="store_true", required=False, help='Output a text MARC (*.mrk) file.')
    parser.add_argument('-x', '--xml', action="store_true", required=False, help='Output a MARCXML file (*.mrx).')
    parser.add_argument('-b', '--bibframe', action="store_true", required=False, help='Output a Bibframe 2 RDF XML file (*.rdf).')
    parser.add_argument('-f', '--rdfformat', type=str, required=False, help='Specify RDF serialisation format for Bibframe 2 file. Valid values: turtle, nt, nquads, json-ld, n3, trix.')
    
    # Parse the argument
    args = parser.parse_args()

    jconfigfile = os.path.abspath("conf.json")
    if os.path.isfile(configfile):
        with open(jconfigfile, "r") as f:
            jconfig = f.read()
        config = json.loads(jconfig)

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

    bfout = ""
    if config and "bfout" in config:
            bfout = config["bfout"]
    else:
        bfout = "individual"

    if config:
        params = removekey(config, "bfout")
        if not bool(params):
            params = {}

    if bfout == "collection" and (args.bibframe or args.rdfformat) and not args.xml:
        args.xml = True

    in_file = os.path.abspath(args.input)
    filename, file_extension = os.path.splitext(in_file)
    if reverse == True:
        out_mrc_file = filename + "_cesu8" + ".mrc"
    else:
        out_mrc_file = filename + "_utf8" + ".mrc"
        if args.xml:
            out_xml_file=filename + "_utf8" + ".mrx"
        if args.text:
            out_txt_file = filename + "_utf8" + ".mrk"
        if args.bibframe:
            out_rdf_file = filename + "_utf8" + ".rdf"
        
    if mode == "cesu-8":
        reader = pymarc.MARCReader(open(in_file, 'rb'), force_utf8=False, to_unicode=False)
    else:
        reader = pymarc.MARCReader(open(in_file, 'rb'), force_utf8=False, to_unicode=True)

    if args.rdfformat and args.rdfformat in rdf_formats:
            rdf_format = args.rdfformat
    else:
        rdf_format = ''

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
            rhg = True if "rhg" or "inc" in lang else False
            ara = True if "ara" in lang else False
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
            if ara:
                for f in r.get_fields('880'):
                    if f['a'] and ("&#x2" in f['a']):
                        f['a'] = re.sub(r'&#x2', '&#x12', f['a'])
                        f['a'] = html.unescape(f['a'])
                    if f['b'] and ("&#x2" in f['b']):
                        f['b'] = re.sub(r'&#x2', '&#x12', f['b'])
                        f['b'] = html.unescape(f['b'])
                    if f['c'] and ("&#x2" in f['c']):
                        f['c'] = re.sub(r'&#x2', '&#x12', f['c'])
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

    with open(out_mrc_file , 'wb') as data:
        for record in converted_marc_records:
            data.write(record.as_marc())

    #
    # Convert to MARCXML file
    #
    if args.xml:
        reader2 = pymarc.MARCReader(open(out_mrc_file, 'rb'), force_utf8=False, to_unicode=True)
        writer2 = pymarc.XMLWriter(open(out_xml_file,'wb'))
        for record in reader2:
            #print(record)
            writer2.write(record)
        writer2.close()
        reader2.close()

    #
    # Convert to a text MARC file (.mrk)
    #

    if args.text:
        reader3 = pymarc.MARCReader(open(out_mrc_file, 'rb'), force_utf8=False, to_unicode=True)
        writer3 = pymarc.TextWriter(open(out_txt_file,'wt'))
        for record in reader3:
            #print(record)
            writer3.write(record)
        writer3.close()
        reader3.close()

    #
    # Convert to Bibframe2 RDF documents
    #    http://knowledgelinks.io/presentations/introduction-to-bibcat/topic/marc2bibframe2.html
    #

    if args.bibframe or args.rdfformat:
        xslfile = 'xsl/marc2bibframe2.xsl'
        if os.path.isfile(xslfile):
            reader4 = pymarc.MARCReader(open(out_mrc_file, 'rb'), force_utf8=False, to_unicode=True)
            marc_records = []
            for record in reader4:
                marc_records.append(record)
            marc2bibframe2 = etree.XSLT(etree.parse(xslfile))
            if bfout == "individual":
                for i in range(len(marc_records)):
                    raw_xml = pymarc.record_to_xml(marc_records[i], namespace=True)
                    marc_xml = etree.XML(raw_xml)
                    bf_rdf_xml = marc2bibframe2(marc_xml)
                    if args.bibframe:
                        if len(marc_records) == 1:
                            out_rdf_file = filename + "_utf8" + ".rdf"
                        else:
                            out_rdf_file = filename + "_" + str(i) + "_utf8" + ".rdf"
                        with open(out_rdf_file, 'w') as doc:
                            bibframe_file = etree.tostring(bf_rdf_xml, pretty_print = True,encoding="Unicode")
                            #bibframe_file = html.unescape(bibframe_file)
                            doc.write(bibframe_file)
                    if rdf_format:
                        if len(marc_records) == 1:
                            out_ttl_file = filename + "_utf8" + rdf_formats[rdf_format][0]
                        else:
                            out_ttl_file = filename + "_" + str(i) + "_utf8" + rdf_formats[rdf_format][0]
                        raw_rdf_xml = etree.tostring(bf_rdf_xml)
                        bf_rdf = rdflib.Graph()
                        bf_rdf.parse(data=raw_rdf_xml, format='xml')
                        with open(out_ttl_file, 'w') as doc:
                            doc.write(bf_rdf.serialize(format=rdf_format))
            elif bfout == "collection" and os.path.isfile(out_xml_file):
                bibframe_file = xsl_transformation(xslfile=xslfile, xmlfile=out_xml_file)
                #bibframe_file = html.unescape(bibframe_file)
                with open(out_rdf_file, 'w') as doc:
                    doc.write(etree.tostring(bibframe_file, pretty_print = True, encoding='Unicode'))
            reader4.close()
        else:
            print("Marc2bibframe2 support unavailable. Add marc2bibframe2 to xsl directory.")

# Usage:
#   To convert a CESU-8 encoded MARC file to an UTF-8 MARC file:
#       ./supplementary_planes.py -i test_files/13155553-Bulk_Export.mrc
#
#   To generate a UTF-8 MARCXML file and an UTF-8 MARC file:
#       ./supplementary_planes.py -x -i test_files/13155553-Bulk_Export.mrc
#
#   To generate a Bibframe2 RDF/XML file and an UTF-8 MARC file:
#       ./supplementary_planes.py -xb -i test_files/13155553-Bulk_Export.mrc

if __name__ == '__main__':
    main()
