# CLI tools

## intl-bib-clean.py

A CLI Python tool for cleaning internationalisation issues in records in MARC21 binary files. Script accepts both MARC-8 and UTF-8 encoded MARC files. Current functionality includes:

* Repairing Voyager CESU-8 encoded data (use MARC-8 files as input).
* Applying a Unicode Normalisation Form (NFC or NFD) to data, or normalise to MARC21 Character repertoire.
* Normalise Thai and Lao romanisation based on differing interpretations of 1997 and 2011 romanisation tables.
* Normalise half-marks in Cyrillic romanisations to double spanning diacritic (ligature tie).
* Output file to UTF-8 encoded binary MARC21 file (*.mrc), text file (*.mrk), and/or MARCXML file (*.xml).

Bibframe support will be integrated into the tool, using [marc2bibframe2](https://github.com/lcnetdev/marc2bibframe2) xslt stylesheets. See the [README](https://github.com/enabling-languages/library-i18n/tree/main/cli) file for _marc2bibframe2_ installation instructions.

```
usage: intl_bib_clean.py [-h] -i INPUT [-o OPTIONS] [-e EXLIBRIS_VOYAGER_SMP [EXLIBRIS_VOYAGER_SMP ...]]
                         [-n {NFC,NFD,NFM21}] [-c {True,False}] [-t {1997,2011,None}] [-f FIELDS [FIELDS ...]]
                         [-s SCRIPT_FIELDS [SCRIPT_FIELDS ...]] [-v] [-m MODES [MODES ...]]

Repair and clean internationalisation issues in MARC21 records.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        MARC file to be normalised and cleaned. File can be either MARC-8 or UTF-8 encoded file
                        containinf one or more records.
  -o OPTIONS, --options OPTIONS
                        Custom configuration file. Overrides default configuration file.
  -e EXLIBRIS_VOYAGER_SMP [EXLIBRIS_VOYAGER_SMP ...], --exlibris_voyager_smp EXLIBRIS_VOYAGER_SMP [EXLIBRIS_VOYAGER_SMP ...]
                        Space seperated list of SMP scripts to be repaired. Use lowercase ISO 15924 script codes.
                        Requires input file be a MARC-8 encoded file.
  -n {NFC,NFD,NFM21}, --normalisation {NFC,NFD,NFM21}
                        Apply Unicode Normalisation Form to the record (NFC, NFD, NFM21). Overides configuration file.
  -c {True,False}, --cyrillic {True,False}
                        Diacritic normalisation (half marks to double diacritic (Tree or False). Overides
                        configuration file.
  -t {1997,2011,None}, --thailao {1997,2011,None}
                        Specify interpretation to use for Lao and Thai romanisation (1997 or 2011). Use None to turn
                        off. Overides configuration file.
  -f FIELDS [FIELDS ...], --fields FIELDS [FIELDS ...]
                        Space seperated list of fields in MARC record to process and clean. Should include all fields
                        where you have native language strings in either romanised or native script. Overrides default
                        configuration file.
  -s SCRIPT_FIELDS [SCRIPT_FIELDS ...], --script_fields SCRIPT_FIELDS [SCRIPT_FIELDS ...]
                        Fields where native script strings occur. Overrides default configuration file.
  -v, --verbose         Print out configuartaion used
  -m MODES [MODES ...], --modes MODES [MODES ...]
```