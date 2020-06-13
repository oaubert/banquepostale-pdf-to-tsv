#! /usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

import re
import subprocess
import sys

months = { month: i + 1 for i, month in enumerate([ 'janvier', 'février', 'mars', 'avril',
                                                    'mai', 'juin', 'juillet', 'août',
                                                    'septembre', 'octobre', 'novembre', 'décembre']) }

class Record:
    """If a record has a date, then it is an account movement.
    Else is is some other metadata (total, etc)
    """
    def __init__(self, date=None, title="", details="", amount=0, account=None):
        self.date = date
        self.title = title
        self.details = details
        self.amount = amount
        self.account = account

    def __str__(self):
        return "\t".join(str(v) for v in (self.date or "Metadata", self.amount, self.account, self.details))

def data_lines(lines):
    """Output Records
    """
    current_account = None
    publication_date = None
    current_record = None
    reference_line = None

    for l in lines:
        if re.search('^\s*Date\s+Opérations.+Débit.+Crédit', l):
            reference_line = l
            continue

        m = re.search(r'Relevé édité le (?P<day>\d\d) (?P<month>\w+) (?P<year>\d\d\d\d)', l)
        if m:
            # In this order so that we can compare date tuples
            publication_date = ( int(m.group('year')),
                                 months[m.group('month')],
                                 int(m.group('day')) )
            continue

        m = re.search('.+n° (?P<account>[\w\d ]+)\s*', l)
        if m:
            current_account = m.group('account').replace(' ', '')
            continue

        m = re.search('^\s+(?P<label>(Ancien|Nouveau) solde)\sau\s+(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<value>\d{,3}(?: \d{3})*(?:,\d+)?)\s*$', l)
        if m:
            if current_record is not None:
                yield current_record
            amount = float(m.group('value').replace(" ", "").replace(",", "."))
            yield Record(title=m.group('label'),
                         details=f"{m.group('label')} {m.group('date')}",
                         amount=amount,
                         account=current_account)
            current_record = None
            continue

        if re.search('^\s{,2}(?P<date>\d{2}/\d{2})\s', l):
            if publication_date < (2017, 3, 1):
                # Before 1st march 2017, there is an extra column with the price in
                # francs
                m = re.match(r'\s*(?P<day>\d{2})\/(?P<month>\d{2})(?P<title>.*?)(?P<cents>\d{,3}(?: \d{3})*(,\d+)?) +(<?Pfrancs>(?:-|\+ )\d{,3}(?: \d{3})*(?:,\d+)?)$', l)
                value = float(m.group('value').replace(' ', '').replace(',', '.'))
                value = -value if m.group('francs')[0] == '-' else value
                date = f"{m.group('month')}/{m.group('day')}"
                title = m.group('title')
            else:
                m = re.search('^\s*(?P<date>\d{2}/\d{2})\s+(?P<title>.+?)\s+(?P<value>\d{,3}(?: \d{3})*(?:,\d+)?)\s*$', l)
                amount = float(m.group('value').replace(" ", "").replace(",", "."))
                if len(l) < len(reference_line) - 12:
                    amount = -amount
                # Add year
                date = m.group('date')
                date = f"{date[-2:]}/{date[:2]}"
                title = m.group('title')

            year = publication_date[0]
            if date[:2] == "12" and publication_date[1] == 1:
                year = year - 1

            if current_record is not None:
                yield current_record
            current_record = Record(date=f"{year}/{date}",
                                    title=title,
                                    details=title,
                                    amount=amount,
                                    account=current_account)
            continue

        m = re.search('^\s*(?P<label>Total des opérations).+?(?P<debit>\d{,3}(?: \d{3})*(?:,\d+))\s+(?P<credit>\d{,3}(?: \d{3})*(?:,\d+)?)\s*$', l)
        if m:
            if current_record is not None:
                yield current_record
            debit = float(m.group('debit').replace(" ", "").replace(",", "."))
            credit = float(m.group('credit').replace(" ", "").replace(",", "."))
            yield Record(title='Crédit total', details='Crédit total', amount=debit, account=current_account)
            yield Record(title='Débit total', details='Débit total', amount=credit, account=current_account)
            current_record = None

        # End of record: empty line
        if not l.strip():
            if current_record is not None:
                yield current_record
            current_record = None

        if current_record is not None:
            current_record.details = " ".join((current_record.details, l))

    if current_record is not None:
        yield current_record

def pdf_to_tsv(filename):
    txt = str(subprocess.check_output(['pdftotext', '-layout', filename, "-"]), 'utf-8')
    solde = None
    credit = None
    debit = None
    for record in data_lines(txt.splitlines()):
        print(record)
        if record.title == 'Ancien solde':
            solde = record.amount
            credit = 0
            debit = 0
        elif record.title == 'Nouveau solde':
            if abs(solde - record.amount) > 1e-6:
                logger.error(f"Solde mismatch {solde} - {record.amount} = {solde-record.amount} [ {credit} / {debit} ]")
        elif record.date is not None:
            solde = solde + record.amount
            if record.amount > 0:
                credit += record.amount
            else:
                debit += record.amount

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} *.pdf')
        sys.exit(1)
    for pdf in sys.argv[1:]:
        pdf_to_tsv(pdf)
