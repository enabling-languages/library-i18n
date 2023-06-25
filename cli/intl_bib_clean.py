#!/usr/bin/env python3

import el_internationalisation as eli
from pymarc import MARCReader, Subfield, TextWriter, XMLWriter
import regex as re
from pathlib import Path
import html
import el_internationalisation as eli
import json
import argparse

# From CLI: python -m json.tool config.json

# def open_marc_record(input_file):
#     in_f = Path(input_file).resolve()
#     out_f = in_f.parent / (in_f.stem + '_cleaned' + in_f.suffix)

# def repair_smp(text: str, script: str) -> str:
#     """Repair SMP characters in MARC-8 encoded records exported from Voyager LMS
# 
#     Supported scripts:
#         adlm: Adlam - U+1E900–U+1E95F
#         bamu: Bamum - U+A6A0–U+A6FF, U+16800–U+16A3F   ??
#         bass: Bassa Vah - U+16AD0-U+16AFF              ??
#         hmng: Pahawh Hmong - U+16B00-U+16B8F           ??
#         mend: Mende - U+1E800-1E8DF                    ??
#         palm: Palmyrene - U+10860-U+1087F
#         rohg: Rohingya - U+10D00–U+10D3F
#         xsux: Cuneiform - U+12000-U+123FF, U+12400-U+1247F, U+12480–U+1254F
#         yezi: Yezidi - U+10E8D-U+10EBF                 ??
#         
#     Unsupported:
#         shaw: Shavian - Voyager converts Shavian characters to U+FFFD (Replacement Character)
# 
#     Args:
#         text (str): Subfield value to be repaired
#         script (str): Writing system (script)
# 
#     Returns:
#         str: Repaired subfield value, if it can be repaired, else original subfield value.
#     """
#     repair_data = {
#         "adlm": (r'&#x[eE]9[0-5][0-9a-fA-F];', r'&#x[eE]9', r'&#x1e9'),
#         "bamu": (r'&#x6[8-9Aa][0-9A-Fa-f][0-9A-Fa-f];', r'&#x6', r'&#x16'),
#         "bass": (r'&#x6[aA][D-Fd-f][0-9A-Fa-f];', r'&#x6a', r'&#x16a'),
#         "hmng": (r'&#x6[bB][0-8][0-9A-Fa-f];', r'&#x6[bB]' r'&#x16b'),
#         "mend": (r'&#x[eE]8[0-9A-Da-d][0-9A-Fa-f];', r'&#x[eE]8', r'&#x1e8'),
#         "palm": (r'&#x08[6-7][0-9A-Fa-f];', r'&#x08', r'&#x108'),
#         "rohg": (r'&#x0[dD][0-3][0-9a-fA-F];', r'&#x0[dD]', r'&#x10d'),
#         "xsux": (r'&#x2[0-5][0-9a-fA-F][0-9a-fA-F];', r'&#x2', r'&#x12'),
#         "yezi": (r'&#x0[eE][8-9A-Ba-b][0-9A-Fa-f];', r'&#x0[eE]', r'&#x10e')
#         
#     }
#     try:
#         if re.match(repair_data[script][0], text):
#             return re.sub(repair_data[script][1], repair_data[script][2], text)
#         else:
#             return text
#     except KeyError:
#         return text
# repairable_scripts = ["adlm", "bamu", "bass", "hmng", "mend", "palm", "rohg", "xsux", "yezi"]

def main():
    
    parser = argparse.ArgumentParser(description='Repair and clean internationalisation issues in MARC21 records.')
    parser.add_argument('-i', '--input', type=str, required=True, help='MARC file to be normalised and cleaned. File can be either MARC-8 or UTF-8 encoded file containinf one or more records.')
    parser.add_argument('-o', '--options', type=str, help='Custom configuration file. Overrides default configuration file.')
    parser.add_argument('-e', '--exlibris_voyager_smp', type=str, nargs='+', required=False, help='Space seperated list of SMP scripts to be repaired. Use lowercase ISO 15924 script codes. Requires input file be a MARC-8 encoded file.')
    parser.add_argument('-n', '--normalisation', type=str, required=False, choices=("NFC", "NFD", "NFM21"), help='Apply Unicode Normalisation Form to the record (NFC, NFD, NFM21). Overides configuration file.')
    parser.add_argument('-c', '--cyrillic', type=str, required=False, choices=('True','False'), help='Diacritic normalisation (half marks to double diacritic (Tree or False). Overides configuration file.')
    parser.add_argument('-t', '--thailao', type=str, choices=['1997', '2011', 'None'], required=False, help='Specify interpretation to use for Lao and Thai romanisation (1997 or 2011). Use None to turn off. Overides configuration file.')
    parser.add_argument('-f', '--fields', type=str, nargs='+', required=False, help='Space seperated list of fields in MARC record to process and clean. Should include all fields where you have native language strings in either romanised or native script. Overrides default configuration file.')
    parser.add_argument('-s', '--script_fields', type=str, nargs='+', required=False, help='Fields where native script strings occur. Overrides default configuration file.')
    parser.add_argument('-v', '--verbose', action="store_true", required=False, help='Print out configuartaion used')
    parser.add_argument('-m', '--modes', type=str, nargs='+', required=False, help='')
    args = parser.parse_args()

    input_file = Path(args.input).resolve()
    mrc_output_file = input_file.parent / (input_file.stem + '_clean' + input_file.suffix) 
    mrk_output_file = input_file.parent / (input_file.stem + '_clean.mrk') 
    marcxml_output_file = input_file.parent / (input_file.stem + '_clean.xml') 
    
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
    
    # Set MARC21 fields to process
    required_fields = config['fields']
    if args.fields:
        required_fields = args.fields
    
    # Specify which fields contan native script data
    native_fields = config['native_fields']  if config['native_fields'] else []
    if args.script_fields:
        native_fields = args.script_fields
       
    if args.verbose:
        print("Settings: ")
        print(f"Normalisation form: {NORMALISE_DEFAULT}")
        print(f"Cyrillic corrections: {CYRILLIC_ROM}")
        print(f"Thai/Lao corrections: {THAI_LAO_ROM}")
        print(f"Required fields: {required_fields}")
        print(f"Native script fields: {native_fields}")

    # Process the records:
    marc_records = []
    with input_file.open('rb') as i_f:
        reader = MARCReader(i_f, to_unicode=True)
        if args.verbose:
            print(f"\nProcessing:")
        for record in reader:
            if args.verbose:
                print(f"\t{record['001'].value()}")
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
            record_fields = record.get_fields(*required_fields)
            for field in record_fields:
                for i in range(len(field.subfields)):
                    field.subfields[i] = Subfield(field.subfields[i].code, eli.clean_marc_subfield(field.subfields[i].value, record_lang, NORMALISE_DEFAULT, THAI_LAO_ROM, CYRILLIC_ROM))
            marc_records.append(record)

    #
    # Write output file(s)
    #

    for mode in output_formats:
        if mode in ['mrc', 'mrk', 'marcxml']:
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
                pass    
            
            
            
    # records = open_marc_record(args.input)

if __name__ == '__main__':
    main()
