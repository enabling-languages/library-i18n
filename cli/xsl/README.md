# marc2bibframe2

To use the convert a MARC21 record to a Bibframe RDF file, the [marc2bibframe2](https://github.com/lcnetdev/marc2bibframe2/tree/master/xsl) XSL files are required. Open the `scripts/xsl` directory in your terminal and issue the following command:

```sh
wget -O - https://github.com/lcnetdev/marc2bibframe2/archive/master.tar.gz | tar -xz --strip=2 "marc2bibframe2-master/xsl"
```

This will download the [marc2bibframe2](https://github.com/lcnetdev/marc2bibframe2/tree/master/xsl) archive, and extract all the necessary XSL files from [marc2bibframe2](https://github.com/lcnetdev/marc2bibframe2/tree/master/xsl) into your current directory.