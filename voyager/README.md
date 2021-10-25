# Utilities for Voyager LMS

## Working with Characters in the Supplementary Planes

```zsh
voyager$ ./supplementary_planes.py -h
usage: supplementary_planes.py [-h] -i INPUT [-o OUTPUT] [-m MODE] [-r] [-d] [-t] [-x]

Convert MARC records with SMP characters in MARC-8 and CESU-8 to UTF-8. Currently only supports repaing and convering Adlam and Hanifi Rohingya MARC-8 records.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        File to be converted.
  -m MODE, --mode MODE  Mode used for processing the MARC record. Values are cesu-8 and marc-8
  -r, --reverse         Reverse (convert UTF-8 to CESU-8)
  -d, --debug           Display 880 field during processing.
  -t, --text            Output a text MARC file.
  -x, --xml             Output a MARCXML file.
````