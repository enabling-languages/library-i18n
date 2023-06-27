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

def main():

    parser = argparse.ArgumentParser(description='Repair and clean internationalisation issues in MARC21 records.')
    parser.add_argument('-i', '--input', type=str, required=True, help='MARC file to be normalised and cleaned. File can be either MARC-8 or UTF-8 encoded file containinf one or more records.')
    parser.add_argument('-o', '--options', type=str, help='Custom configuration file. Overrides default configuration file.')
    parser.add_argument('-e', '--exlibris_voyager_smp', type=str, nargs='+', required=False, help='Space separated list of SMP scripts to be repaired. Use lowercase ISO 15924 script codes. Requires input file be a MARC-8 encoded file.')
    parser.add_argument('-n', '--normalisation', type=str, required=False, choices=("NFC", "NFD", "NFM21"), help='Apply Unicode Normalisation Form to the record (NFC, NFD, NFM21). Overides configuration file.')
    parser.add_argument('-c', '--cyrillic', type=str, required=False, choices=('True','False'), help='Diacritic normalisation (half marks to double diacritic (Tree or False). Overides configuration file.')
    parser.add_argument('-t', '--thailao', type=str, choices=['1997', '2011', 'None'], required=False, help='Specify interpretation to use for Lao and Thai romanisation (1997 or 2011). Use None to turn off. Overides configuration file.')
    parser.add_argument('-f', '--fields', type=str, nargs='+', required=False, help='Fields where native script strings occur. Overrides default configuration file.')
    parser.add_argument('-v', '--verbose', action="store_true", required=False, help='Print out configuration used')
    parser.add_argument('-vt', '--verboseterminal', action="store_true", required=False, help='Print out configuration used, out put records to STDOUT. No files generated.')
    parser.add_argument('-m', '--modes', type=str, nargs='+', required=False, help='File formats to output: mrc (Binary MARC), mrk (MARC text), marcxml (MARCXML), rdfxml (bibframe2)')
    args = parser.parse_args()

    input_file = Path(args.input).resolve()
    mrc_output_file = input_file.parent / (input_file.stem + '_clean' + input_file.suffix)
    mrk_output_file = input_file.parent / (input_file.stem + '_clean.mrk')
    marcxml_output_file = input_file.parent / (input_file.stem + '_clean.xml')
    rdf_output_file = input_file.parent / (input_file.stem + '_clean.rdf')

    # Set file names and file formats

    output_formats = ["mrc"]
    if args.modes:
        output_formats = args.modes

    # Set constants and variables
    scripts_to_repair = []
    if args.exlibris_voyager_smp:
        scripts_to_repair = args.exlibris_voyager_smp

    # Read configuration file
    if args.options:
        config_file = Path(args.options).resolve()
    else:
        config_file = Path(__file__).parent.joinpath('default_config.json')
    with open(config_file.as_posix(), "r") as cf:
        jconfig = cf.read()
        config = json.loads(jconfig)

    # Set Unicode normalisation form
    NORMALISE_DEFAULT = config["normalisation"]
    if args.normalisation:
         NORMALISE_DEFAULT = args.normalisation

    # Set Thai/Lao romanisation preferences
    if config['thai_lao']:
        if config['thai_lao'] == '1997' or '2011':
            THAI_LAO_ROM = config['thai_lao']
        elif config['thai_lao'] == 'None':
            THAI_LAO_ROM = None
    else:
        THAI_LAO_ROM = None

    if args.thailao:
        if args.thailao in ['1997', '2011']:
            THAI_LAO_ROM = int(args.thailao)
        elif args.thailao == 'None':
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

    if args.verbose or args.verboseterminal:
        print("\nSettings:\n")
        print(f"Normalisation form: {NORMALISE_DEFAULT}")
        print(f"Cyrillic corrections: {CYRILLIC_ROM}")
        print(f"Thai/Lao corrections: {THAI_LAO_ROM}")
        print(f"Native script fields: {native_fields}")

    # Process the records:
    marc_records = []
    with input_file.open('rb') as i_f:
        reader = MARCReader(i_f, to_unicode=True)
        for record in reader:
            if args.verbose or args.verboseterminal:
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
                        field.subfields[i] = Subfield(field.subfields[i].code, eli.clean_marc_subfield(field.subfields[i].value, record_lang, NORMALISE_DEFAULT, THAI_LAO_ROM, CYRILLIC_ROM))
            marc_records.append(record)
            if args.verboseterminal:
                print(record)

    #
    # Write output file(s)
    #
    if not args.verboseterminal:
        for mode in output_formats:
            if mode in ['mrc', 'mrk', 'marcxml', 'rdfxml']:
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
                elif mode == "rdfxml":
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

                    bibframe_contents = eli.xsl_transformation(xslfile=xslfile, xmlfile=memory)
                    # print(bibframe_contents)
                    with open(rdf_output_file, 'w') as doc:
                        doc.write(etree.tostring(bibframe_contents, pretty_print = True, encoding='Unicode'))

if __name__ == '__main__':
    main()
