#!/usr/bin/env python3

import argparse
import os
from datetime import date, datetime, timedelta

from cmi.extractor import Configuration, Extractor
from cmi.field import FieldType, FieldUnit


def main() -> None:
    parser = argparse.ArgumentParser(description='generate sql schema from C.M.I.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--encoding', default='Windows-1252', type=str, help='file encoding')
    parser.add_argument('--host', default='cmi', type=str, help='C.M.I. hostname')
    parser.add_argument('--port', default=80, type=int, help='C.M.I. port')
    parser.add_argument('--user', default='winsol', type=str, help='Username to authenticate with')
    parser.add_argument('--password', default='data', type=str, help='Password to authenticate with')
    parser.add_argument('--file', default='cmi.sql', type=str, help='output file for sql schema')

    tomorrow = date.today() + timedelta(days=1)
    arguments = parser.parse_args()
    data = Extractor.process(Configuration(arguments.host, arguments.port, arguments.user, arguments.password, arguments.encoding, tomorrow, tomorrow, False))

    new_line = os.linesep
    with open(arguments.file, 'w') as sqlfile:
        sqlfile.write(f'-- schema for CMI ({arguments.host}) generated at {datetime.now()}{new_line}')
        sqlfile.write(f'CREATE TABLE IF NOT EXISTS cmi ({new_line}')
        sqlfile.write(f'\ttime\t\tTIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP(0),{new_line}')

        for field in data.infoH.fields:
            if field.size == 0:
                continue

            space = None
            type = None
            if field.unit == FieldUnit.BOOLEAN:
                type = 'BOOLEAN'
                space = ' '
            else:
                if field.size == 4:
                    type = 'REAL'
                    space = '    '

            name = None
            if field.type == FieldType.ANALOG:
                name = f'analog_{field.count:02}'
            else:
                name = f'digital_{field.count:02}'

            sqlfile.write(f'\t{name}\t{type},{space}-- {field.description}{new_line}')
        sqlfile.write(f'\tUNIQUE\t\t(time){new_line}')
        sqlfile.write(f');{new_line}')


if __name__ == '__main__':
    main()
