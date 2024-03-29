#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import datetime

from cmi.extractor import Configuration, Extractor
from cmi.filter import Filter


def main() -> None:
    now = datetime.date.today()
    parser = argparse.ArgumentParser(description='export data from C.M.I. to CSV', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--encoding', default='Windows-1252', type=str, help='file encoding')
    parser.add_argument('--file', default='cmi.csv', type=str, help='output file name')
    parser.add_argument('--host', default='cmi', type=str, help='C.M.I. hostname')
    parser.add_argument('--port', default=80, type=int, help='C.M.I. port')
    parser.add_argument('--user', default='winsol', type=str, help='Username to authenticate with')
    parser.add_argument('--password', default='data', type=str, help='Password to authenticate with')
    parser.add_argument('--after', default='1970-01-01', type=str, help='only import data that was created after (YYYY-MM-DD)')
    parser.add_argument('--before', default=now.strftime('%Y-%m-%d'), type=str, help='only import data that was created before (YYYY-MM-DD)')
    parser.add_argument('--unique', action=argparse.BooleanOptionalAction, help='only export events if any values have changed')
    parser.add_argument('--min-delta', default=1, type=int, help='minimum number of seconds between 2 events to configer both of them for export')

    arguments = parser.parse_args()
    before = datetime.datetime.fromisoformat(arguments.before).date()
    after = datetime.datetime.fromisoformat(arguments.after).date()
    delta = datetime.timedelta(seconds=arguments.min_delta)
    data = Extractor.process(Configuration(arguments.host, arguments.port, arguments.user, arguments.password, arguments.encoding, after, before, False))

    with open(arguments.file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        original = None
        for group in data.groups:
            for event in group.events:
                row = [event.time]
                for value in event.values:
                    row.append(value.value)

                if arguments.unique and not Filter.changed(original, row):
                    continue
                if Filter.within_delta(original, row, delta):
                    continue

                original = row
                writer.writerow(row)


if __name__ == '__main__':
    main()
