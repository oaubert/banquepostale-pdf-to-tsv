# banquepostale_to_tsv

La Banque Postale provides its e-accounting data in PDF, which has to
be processed in order to become useful.

This project started as fixes for
[https://github.com/wizmer/banquepostale-pdf-to-csv](`banquepostale_to_csv`),
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
