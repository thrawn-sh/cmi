#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv

from cmi.extractor import Configuration, Extractor


def main():
    parser = argparse.ArgumentParser(description='query data from C.M.I', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', default=False, type=bool, help='Generate debug output and file', action=argparse.BooleanOptionalAction)
    parser.add_argument('--encoding', default='Windows-1252', type=str, help='file encoding')
    parser.add_argument('--host', default='cmi', type=str, help='C.M.I. hostname')
    parser.add_argument('--port', default=80, type=int, help='C.M.I. port')
    parser.add_argument('--user', default='winsol', type=str, help='Username to authenticate with')
    parser.add_argument('--password', default='data', type=str, help='Password to authenticate with')

    arguments = parser.parse_args()
    data = Extractor.process(Configuration(arguments.host, arguments.port, arguments.user, arguments.password, arguments.encoding, arguments.debug))

    with open('cmi.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        for group in data.groups:
            for event in group.events:
                row = [event.time]
                for value in event.values:
                    row.append(value.value)
                writer.writerow(row)


if __name__ == '__main__':
    main()
