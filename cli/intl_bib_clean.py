#!/usr/bin/env python3

import el_internationalisation as eli
from pymarc import MARCReader, Subfield, TextWriter, XMLWriter
import regex as re
from pathlib import Path
# import html
import json
import argparse
from io import BytesIO
import rdflib
from lxml import etree
import unicodedata as ud
import icu

problem_chars_pattern = re.compile(r'[\p{Bidi_Control}\p{Cs}\p{Co}\p{Cn}\u0333\u3013\uFFFD]')
# problem_chars_pattern = re.compile(r'[\p{Cf}\p{Cs}\p{Co}\p{Cn}\u0333\u3013\uFFFD]')
problem_chars = ['\u0333', '\u3013', '\uFFFD']
problem_chars.extend(list(icu.UnicodeSet(r'\p{Bidi_Control}')))
# problem_chars.extend(list(icu.UnicodeSet(r'\p{Cf}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Cs}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Co}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Cn}')))

def detect_anomalies(text: str) -> set[str]:
    problematic = set()
    if re.search(problem_chars_pattern, text):
        for char in problem_chars:
            if char in text:
                problematic.add(f"{eli.cp(char)} ({ud.name(char)})")
    return problematic

def register_anomalies(sub_field: str):
    check = detect_anomalies(sub_field)
    if check:
        print(*sorted(check), sep="\n", end="\n\n")
    return None

# https://lxml.de/4.4/xpathxslt.html#xslt
# def xsl_transformation(xslfile=None, xmlfile=None, xmlstring=None, transform_attributes={}):
#     xslt_tree = etree.parse(xslfile)
#     transform = etree.XSLT(xslt_tree)
#     xml_contents = xmlstring
#     if not xml_contents:
#         if xmlfile:
#             xml_contents = etree.parse(xmlfile)
#     result = transform(xml_contents, **transform_attributes)
#     return result

def main():

    parser = argparse.ArgumentParser(description='Repair and clean internationalisation issues in MARC21 records.')
    parser.add_argument('-i', '--input', type=str, required=True, help='MARC file to be normalised and cleaned. File containing one or more records, Where records can be either MARC-8 or UTF-8 encoded records.')
    parser.add_argument('-o', '--options', type=str, help='Custom configuration file. Overrides default configuration file.')
    parser.add_argument('-s', '--scripts', type=str, nargs='+', required=False, help='Space separated list of SMP scripts to be repaired. Use lowercase ISO 15924 script codes. Requires input file be a MARC-8 encoded file.')
    parser.add_argument('-n', '--normalisation', type=str, required=False, choices=("NFC", "NFD", "NFM21"), help='Apply Unicode Normalisation Form to the record (NFC, NFD, NFM21). Overrides configuration file.')
    parser.add_argument('-c', '--cyrillic', type=str, required=False, choices=('True','False'), help='Diacritic normalisation (half marks to double diacritic (True or False). Overrides configuration file.')
    parser.add_argument('-t', '--thailao', type=str, choices=['1997', '2011', 'None'], required=False, help='Specify interpretation to use for Lao and Thai romanisation (1997 or 2011). Use None to turn off. Overrides configuration file.')
    parser.add_argument('-f', '--fields', type=str, nargs='+', required=False, help='Fields where native script strings occur. Overrides default configuration file.')
    parser.add_argument('-v', '--verbose', action="store_true", required=False, help='Print out configuration used')
    parser.add_argument('-vt', '--verbose_terminal', action="store_true", required=False, help='Print out configuration used, out put records to STDOUT. No files generated.')
    parser.add_argument('-ft', '--file_types', type=str, nargs='+', required=False, help='File formats to output: mrc (Binary MARC), mrk (MARC text), marcxml (MARCXML), rdfxml (bibframe2), ttl (Turtle), nt (N-Triples)')
    args = parser.parse_args()

    input_file = Path(args.input).resolve()
    mrc_output_file = input_file.parent / (input_file.stem + '_clean' + input_file.suffix)  # Binary MARC21 file
    mrk_output_file = input_file.parent / (input_file.stem + '_clean.mrk')                  # Text MARC21 file
    marcxml_output_file = input_file.parent / (input_file.stem + '_clean.xml')              # MARCXML
    rdf_output_file = input_file.parent / (input_file.stem + '_clean.rdf')                  # RDF/XML
    ttl_output_file = input_file.parent / (input_file.stem + '_clean.ttl')                  # Turtle
    nt_output_file = input_file.parent / (input_file.stem + '_clean.nt')                    # N-Triples

    # Set constants and variables
    scripts_to_repair = []
    if args.scripts:
        scripts_to_repair = args.scripts

    # Read configuration file
    if args.options:
        config_file = Path(args.options).resolve()
    else:
        config_file = Path(__file__).parent.joinpath('config.json')
    with open(config_file.as_posix(), "r") as cf:
        jconfig = cf.read()
        config = json.loads(jconfig)

    # Set Unicode normalisation form
    NORMALISE_DEFAULT = config["normalisation"]
    if args.normalisation:
         NORMALISE_DEFAULT = args.normalisation

    # Set file names and file formats
    # output_formats = ["mrc"]
    output_formats = config["file_types"]
    if args.file_types:
        output_formats = args.file_types

    # Set Thai/Lao romanisation preferences
    if config['thai_lao']:
        # if config['thai_lao'] == '1997' or '2011':
        #     THAI_LAO_ROM = config['thai_lao']
        # elif config['thai_lao'] == None:
        #     THAI_LAO_ROM = None
        THAI_LAO_ROM = config['thai_lao']
    else:
        THAI_LAO_ROM = None

    if args.thailao:
        if args.thailao in ['1997', '2011']:
            THAI_LAO_ROM = int(args.thailao)
        elif args.thailao.lower() == 'none':
            THAI_LAO_ROM = None

    # Set Cyrillic normalisation flag
    if config['cyrillic'] == True:
        CYRILLIC_ROM = True
    elif config['cyrillic'] == False:
        CYRILLIC_ROM = False

    if args.cyrillic:
        if args.cyrillic == 'True':
            CYRILLIC_ROM = True
        elif args.cyrillic == 'False':
            CYRILLIC_ROM = False

    # Specify which fields contain native script data
    native_fields = config['fields'] if config['fields'] else ['880']
    if args.fields:
        native_fields = args.fields

    # Set up paramaters for marc 2 bibframe transformation (read from configuration file)
    bf_params = {}
    for k, v in config['to_bibframe'].items():
        if v:
            bf_params[k] = v

    if args.verbose or args.verbose_terminal:
        print("\nSettings:\n")
        print(f"Normalisation form: {NORMALISE_DEFAULT}")
        print(f"Output file formats: {output_formats}")
        print(f"Cyrillic corrections: {CYRILLIC_ROM}")
        print(f"Thai/Lao corrections: {THAI_LAO_ROM}")
        print(f"Native script fields: {native_fields}")
        print("\nBibframe2 parameters:\n")
        for k, v in bf_params.items():
            print(f"{k}: {v}")

    # Process the records:
    marc_records = []
    with input_file.open('rb') as i_f:
        reader = MARCReader(i_f, to_unicode=True)
        for record in reader:
            # if args.verbose or args.verbose_terminal:
            #     print(f"\nProcessing:\t{record['001'].value()}\n")
            print(f"\nProcessing:\t{record['001'].value()}\n")
            try:
                record_lang = record['041']['a']
            except KeyError:
                record_lang = record['008'].value()[35:38]
            if scripts_to_repair:
                for script in scripts_to_repair:
                    if script.lower() in eli.REPAIRABLE_SCRIPTS:
                        for field in record.get_fields(*native_fields):
                            for i in range(len(field.subfields)):
                               field.subfields[i] = Subfield(field.subfields[i].code, eli.repair_smp(field.subfields[i].value, script.lower()))
            record_fields = record.get_fields()
            # print(record_fields)
            for field in record_fields:
                if not field.is_control_field():
                    for i in range(len(field.subfields)):
                        # if args.verbose or args.verbose_terminal:
                        #     register_anomalies(i)
                        register_anomalies(i)
                        field.subfields[i] = Subfield(field.subfields[i].code, eli.clean_marc_subfield(field.subfields[i].value, record_lang, NORMALISE_DEFAULT, THAI_LAO_ROM, CYRILLIC_ROM))
            marc_records.append(record)
            if args.verbose_terminal:
                print(record)

    #
    # Write output file(s)
    #
    if not args.verbose_terminal:
        for mode in output_formats:
            if mode in ['mrc', 'mrk', 'marcxml', 'rdfxml', 'ttl', 'nt']:
                if mode == "mrc":
                    with mrc_output_file.open('wb') as o:
                        for record in marc_records:
                            o.write(record.as_marc())
                elif mode == "mrk":
                    text_writer = TextWriter(open(mrk_output_file,'wt'))
                    for record in marc_records:
                        text_writer.write(record)
                    text_writer.close()
                elif mode == "marcxml":
                    marcxml_writer = XMLWriter(open(marcxml_output_file,'wb'))
                    for record in marc_records:
                        marcxml_writer.write(record)
                    marcxml_writer.close()
                elif mode in ["rdfxml", "ttl", "nt"]:
                    memory = BytesIO()
                    rdf_writer = XMLWriter(memory)
                    for record in marc_records:
                        # print(record)
                        rdf_writer.write(record)
                    rdf_writer.close(close_fh=False)
                    # print(memory.getvalue())
                    xslfile = 'xsl/marc2bibframe2.xsl'
                    # marc2bibframe2 = etree.XSLT(etree.parse(xslfile))

                    memory.seek(0)

                    bibframe_contents = eli.xsl_transformation(xslfile, memory, None, bf_params)
                    raw_contents = etree.tostring(bibframe_contents)
                    # print(type(raw_contents))
                    # print(raw_contents)
                    if mode == "rdfxml":
                        with open(rdf_output_file, 'w') as doc:
                            doc.write(etree.tostring(bibframe_contents, pretty_print = True, encoding='Unicode'))
                    elif mode in ["ttl", "nt"]:
                        graph = rdflib.Graph()
                        graph.parse(data=raw_contents, format='xml')
                        if mode == "ttl":
                           # print(graph.serialize(format="ttl"))
                            with open(ttl_output_file, 'w') as doc:
                                doc.write(graph.serialize(format="ttl"))
                        if mode == "nt":
                            with open(nt_output_file, 'w') as doc:
                                doc.write(graph.serialize(format="nt"))

if __name__ == '__main__':
    main()
