# CLI tools

## Internationalisation bibliographic cleaner (intl-bib-clean.py)

A CLI Python tool for cleaning internationalisation issues in records in MARC21 binary files. Script accepts both MARC-8 and UTF-8 encoded MARC files. Current functionality includes:

* ~~Repairing Voyager CESU-8 encoded data (use MARC-8 files as input).~~
* Applying a Unicode Normalisation Form (NFC or NFD) to data or normalise to MARC21 character repertoire.
* Normalise Thai and Lao romanisation based on differing interpretations of 1997 and 2011 romanisation tables.
* Normalise half-marks in Cyrillic romanisations to double spanning diacritic (ligature tie).
* Output file to UTF-8 encoded binary MARC21 file (*.mrc), text file (*.mrk), and/or MARCXML file (*.xml).

### Installation

1. Install software dependencies
2. Clone or download Github repository
3. Create a Python virtual environment
4. Install required python packages

### Basic usage

The _internationalisation bibliographic cleaner_ uses a [json configuration](configuration.md) file to control default values for the tool. Edit [config.json](config.json) as required. 

The use the tool, specify the binary MARC21 file to be processed:

```py
intl_bib_clean.py -i /path/to/original_file.mrc
```

Configuration settings can be overridden by specifying an alternative configuration file, by command line parameters, or both, with the command line parameters taking precedence.

To specify an alternative configuration file:

```py
intl_bib_clean.py -i /path/to/original_file.mrc -o /path/to/alt_config.json
```

### Command line parameters

__-i (--input)__: MARC21 file to be processed. This can be either a MARC-8 or UTF-8 encoded binary MARC file. The file can contain one or more records. Generated file is UTF-8.

__-o (--options)__: Specify an alternative [configuration file](configuration.md) to control file processing and override default values.


---

```plaintext
usage: intl_bib_clean.py [-h] -i INPUT [-o OPTIONS] [-n {NFC,NFD,NFM21}] [-c {True,False}] [-t {1997,2011,None}] [-f FIELDS [FIELDS ...]] [-v] [-vt]
                         [-ft FILE_TYPES [FILE_TYPES ...]]

Repair and clean internationalisation issues in MARC21 records.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        MARC file to be normalised and cleaned. File containing one or more records, Where records can be either MARC-8 or UTF-8 encoded
                        records.
  -o OPTIONS, --options OPTIONS
                        Custom configuration file. Overrides default configuration file.
  -n {NFC,NFD,NFM21}, --normalisation {NFC,NFD,NFM21}
                        Apply Unicode Normalisation Form to the record (NFC, NFD, NFM21). Overrides configuration file.
  -c {True,False}, --cyrillic {True,False}
                        Diacritic normalisation (half marks to double diacritic (True or False). Overrides configuration file.
  -t {1997,2011,None}, --thailao {1997,2011,None}
                        Specify interpretation to use for Lao and Thai romanisation (1997 or 2011). Use None to turn off. Overrides configuration file.
  -f FIELDS [FIELDS ...], --fields FIELDS [FIELDS ...]
                        Fields where native script strings occur. Overrides default configuration file.
  -v, --verbose         Print out configuration used
  -vt, --verbose_terminal
                        Print out configuration used, out put records to STDOUT. No files generated.
  -ft FILE_TYPES [FILE_TYPES ...], --file_types FILE_TYPES [FILE_TYPES ...]
                        File formats to output: mrc (Binary MARC), mrk (MARC text), marcxml (MARCXML), rdfxml (bibframe2), ttl (Turtle), nt (N-Triples)
```

### Todo

1. Bibframe2 support will be integrated into the tool, using [marc2bibframe2](https://github.com/lcnetdev/marc2bibframe2) xslt stylesheets. See the [README](https://github.com/enabling-languages/library-i18n/tree/main/cli) file for _marc2bibframe2_ installation instructions. Support for RDF+XML, Tuples and N-Triples will be added.
2. Check for occurrence of the Unicode Replacement Character (U+FFFD), Unicode bidirectional formatting characters, etc.
