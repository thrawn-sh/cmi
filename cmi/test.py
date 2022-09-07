#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import os
import pathlib
import shutil

from cmi.extractor import Configuration, Extractor

def dump(content: str, file: str) -> None:
    with open(file, 'wb') as f:
        f.write(content)

def main() -> None:
    now = datetime.date.today()
    parser = argparse.ArgumentParser(description='query data from C.M.I', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--encoding', default='Windows-1252', type=str, help='file encoding')
    parser.add_argument('--host', default='cmi', type=str, help='C.M.I. hostname')
    parser.add_argument('--port', default=80, type=int, help='C.M.I. port')
    parser.add_argument('--user', default='winsol', type=str, help='Username to authenticate with')
    parser.add_argument('--password', default='data', type=str, help='Password to authenticate with')
    parser.add_argument('--after', default='1970-01-01', type=str, help='only import data that was created after (YYYY-MM-DD)')
    parser.add_argument('--before', default=now.strftime('%Y-%m-%d'), type=str, help='only import data that was created before (YYYY-MM-DD)')
    parser.add_argument('--output', default='dump', type=str, help='folder to write data dump to')

    arguments = parser.parse_args()
    before = datetime.datetime.fromisoformat(arguments.before).date()
    after = datetime.datetime.fromisoformat(arguments.after).date()
    print(f'preparing output folder "{arguments.output}"')
    shutil.rmtree(arguments.output, ignore_errors=True)
    pathlib.Path(f'{arguments.output}/LOG').mkdir(parents=True, exist_ok=True)

    print('loading data')
    data = Extractor.process(Configuration(arguments.host, arguments.port, arguments.user, arguments.password, arguments.encoding, after, before, True))

    print('dumping infoH raw')
    dump(data.infoH.raw, f'{arguments.output}/infoh.log')

    print('dumping info raw')
    dump(data.info.raw, f'{arguments.output}/info.log')
    

if __name__ == '__main__':
    main()
