#!/usr/bin/env python3

from pymarc import MARCReader
import regex as re
from pathlib import Path
import argparse

def main():

    parser = argparse.ArgumentParser(description='Repair and clean internationalisation issues in MARC21 records.')
    parser.add_argument('-i', '--input', type=str, required=True, help='MARC file to be normalised and cleaned. File can be either MARC-8 or UTF-8 encoded file containing one or more records.')
    args = parser.parse_args()

    input_file = Path(args.input).resolve()

    # Process the records:
    with input_file.open('rb') as i_f:
        reader = MARCReader(i_f, to_unicode=True)
        for record in reader:
            # output_file = f"{record['001'].value()}"
            output_file = input_file.parent / f"{record['001'].value()}.mrc"
            # marc_records.append(record)
            with output_file.open('wb') as o:
                o.write(record.as_marc())

if __name__ == '__main__':
    main()
