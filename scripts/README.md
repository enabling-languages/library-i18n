# Miscellaneous python scripts

## Unicode normalisation

## Voyager &ndash; working with characters in the Unicode supplementary planes

In Oracle, SQL `CHAR` data type columns use the database character set, while SQL `NCHAR` data type columns use the national character set. The `supplementary_planes.py` script was developed for Voyager installations where the Oracle database's database character set is `US7ASCII` and the national character set is `UTF8`. It is important to note that the Oracle character set `UTF8` is the `CESU-8` character encoding.

For characters in the Basic Multilingual Plane (BMP) the byte sequences for BMP characters are the same (1 to 3 bytes). For UTF-8 characters in the supplementary planes are represented by four bytes, while `CESU-8` uses surrogate pairs (with each character represented by 2 × 3 bytes).

MARC records exported from Voyager will be in the CESU-8 character encodings. Software designed for MARC21 records will assume records are either encoded in UTF-8 or MARC-8. MARC records containing only characters in the BMP will be processed without errors, but records containing characters from the supplementary planes will generate encoding errors.

The `supplementary_planes.py` will read in a CESU-8 encoded binary MARC record and write a UTF-8 encoded version of the MARC record.

### Installation

### Usage

To convert a CESU-8 MARC record:

```sh
$ ./supplementary_planes.py -i sample_record.mrc
```
### `supplementary_planes.py` inline help

```zsh
$ ./supplementary_planes.py -h
usage: supplementary_planes.py [-h] -i INPUT [-m MODE] [-r] [-d] [-t] [-x] [-b] [-f RDFFORMAT]

Convert CESU-8 encoded MARC records with SMP characters to UTF-8. Repair and convert MARC-8 records with
Adlam and Hanifi Rohingya.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        File to be converted.
  -m MODE, --mode MODE  Mode used for processing the MARC record. Valid values: cesu-8, marc-8
  -r, --reverse         Reverse (convert UTF-8 to CESU-8)
  -d, --debug           Display 880 field during processing.
  -t, --text            Output a text MARC (*.mrk) file.
  -x, --xml             Output a MARCXML file (*.mrx).
  -b, --bibframe        Output a Bibframe 2 RDF XML file (*.rdf).
  -f RDFFORMAT, --rdfformat RDFFORMAT
                        Specify RDF serialisation format for Bibframe 2 file. Valid values: turtle, nt,
                        nquads, json-ld, n3, trix.
````