# Utilities for Voyager LMS

## Working with Characters in the Supplementary Planes

```zsh
voyager$ ./supplementary_planes.py -h
usage: supplementary_planes.py [-h] -i INPUT [-m MODE] [-r] [-d] [-b] [-z] [-t] [-x]

Convert CESU-8 encoded MARC records with SMP characters to UTF-8. Repair and convert MARC-8 records with Adlam and Hanifi Rohingya.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        File to be converted.
  -m MODE, --mode MODE  Mode used for processing the MARC record. Values are cesu-8 and marc-8
  -r, --reverse         Reverse (convert UTF-8 to CESU-8)
  -d, --debug           Display 880 field during processing.
  -b, --bibframe        Output a Bibframe 2 RDF XML file.
  -z, --rdfturtle       Output a Bibframe 2 RDF Turtle file.
  -t, --text            Output a text MARC file.
  -x, --xml             Output a MARCXML file.
````