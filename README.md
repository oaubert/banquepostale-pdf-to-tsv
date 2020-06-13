# banquepostale_to_tsv

La Banque Postale provides its bank statements data in PDF, which has
to be processed in order to become useful.

This project started as fixes for
[`banquepostale_to_csv`](https://github.com/wizmer/banquepostale-pdf-to-csv),
but eventually became a full rewrite, hence the separate name to
facilitate fixes in either branch.

# Requirements

This application depends on `pdftotext`, which is available on
Debian/Ubuntu in the `poppler-utils` package.

# Output format

The application outputs records as text, one per line. The record data
is tab-separated, so it can be redirected to a .tsv file and imported
in any spreadsheet application. You can also use `grep` on its output
(to filter against account number for instance).

# License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

# Author

Olivier Aubert <contact@olivieraubert.net>

