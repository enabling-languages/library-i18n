# JSON configuration file

Template for JSON configuration file:

```json
{
    "normalisation":"NFD",
    "file_types":["mrc"],
    "thai_lao":null,
    "cyrillic":false,
    "fields":["880"],
    "to_bibframe":{
        "baseuri":"",
        "idfield":"",
        "idsource":"",
        "localfields":false,
        "pGenerationDatestamp":"",
        "serialization":""
        }
}
```

__normalisation:__ _(string)_ Default normalisation form used by library, either _NFC_, _NFD_, or _NFM21_. _NFM21_ is a custom normalisation form where most character sequences are decomposed and canonically ordered (_NFD_), with a small number of Latin, Cyrillic and Arabic, and all Hangul used composed forms (_NFC_) in order to conform to the MARC21 character repertoire.

__file_types:__ _(array)_ output file formats

- _mrc_ &ndash; binary MARC21 file
- _mrk_ &ndash; text-based representation of a MARC21 file
- _marcxml_ &ndash; MARCXML file
- _rdfxml_ &ndash; Bibframe2 records in a RDF/XML file
- _ttl_ &ndash; Bibframe2 records in a Turtle file
- _nt_ &ndash; Bibframe2 records in a N-Triples file

__thai_lao:__ _(null or number)_ normalise Thai and Lao transliteration. Valid values are _null_ (no changes), _1997_ (use U+031C COMBINING LEFT HALF RING BELOW) or _2011_ (use U+0328 COMBINING OGONEK).

__cyrillic:__ _(boolean)_ convert half-form diacritics (U+FE20 and U+FE21) to double spanning ligature tie (U+0361). Valid values are _true_ or _false_.

__fields:__ _(array)_ MARC fields that contain native script data, rather than transliterated data.

__to_bibframe:__ _(object)_ Marc2Bibframe2 parameters: 

- _baseuri:_ &ndash; the URI stem for generated entities.
- _idfield:_ &ndash; the field of the MARC record that contains the record ID. Default is `001`.
- _idsource:_ &ndash;  a URI used to identify the source of the Local identifier derived from the `idfield`
- _localfields:_ &ndash; if _true_, apply special local processing.
- _pGenerationDatestamp:_ &ndash; a value to be used as the datestamp for the bf:generationProcess property for the Work AdminMetadata.
- _serialization:_ &ndash; `rdfxml`.

Refer to [lcnetdev/marc2bibframe2](https://github.com/lcnetdev/marc2bibframe2/blob/master/README.md#converter-parameters) documentation.