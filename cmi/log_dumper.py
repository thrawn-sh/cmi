#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import os
import requests
import shutil
import struct

from cmi.header      import Header
from cmi.info        import Info
from cmi.info_h      import InfoH
from cmi.event_group import EventGroup

CMI_DUMP = 'cmi-original'
CMI_EXPORT = 'cmi-export'


def __dump_content(content, name: str):
    with open(f'{CMI_DUMP}/{name}', 'wb') as f:
        f.write(content)


def __get_info(arguments, session, infoh: InfoH):
    folder = infoh.folder
    url = f'http://{arguments.host}:{arguments.port}/LOG/info{infoh.folder}.log'
    if arguments.debug:
        print(url)

    response = session.get(url)
    if arguments.debug:
        __dump_content(response.content, f'info{folder}.log')
    info = Info.parse(response.content, arguments.encoding)
    if arguments.debug:
        with open(f'{CMI_EXPORT}/info{folder}.log', 'wb') as f:
            info.export(f, arguments.encoding)

    return info


def __get_infoh(arguments, session):
    url = f'http://{arguments.host}:{arguments.port}/LOG/infoh.log'
    if arguments.debug:
        print(url)

    response = session.get(url)
    if arguments.debug:
        __dump_content(response.content, 'infoh.log')
    infoh = InfoH.parse(response.content, arguments.encoding)

    if arguments.debug:
        with open(f'{CMI_EXPORT}/infoh.log', 'wb') as f:
            infoh.export(f, arguments.encoding)

    return infoh


def __get_events(arguments, session, infoh: InfoH, info: Info):
    events = []
    for log_file in info.log_files:
        path = log_file.path
        url = f'http://{arguments.host}:{arguments.port}{path}'
        if arguments.debug:
            print(url)

        response = session.get(url)
        filename = os.path.basename(path)
        if arguments.debug:
           __dump_content(response.content, filename)
        
        group = EventGroup.parse(response.content, arguments.encoding)
        if arguments.debug:
            with open(f'{CMI_EXPORT}/{filename}', 'wb') as f:
                group.export(f, arguments.encoding)
        return None # TODO

    # FIXME
    return events


def main():
    parser = argparse.ArgumentParser(description='query data from C.M.I', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', default=False, type=bool, help='Generate debug output and file', action=argparse.BooleanOptionalAction)
    parser.add_argument('--encoding', default='Windows-1252', type=str, help='file encoding')
    parser.add_argument('--host', default='cmi', type=str, help='C.M.I. hostname')
    parser.add_argument('--port', default=80, type=int, help='C.M.I. port')
    parser.add_argument('--user', default='winsol', type=str, help='Username to authenticate with')
    parser.add_argument('--password', default='data', type=str, help='Password to authenticate with')

    arguments = parser.parse_args()

    shutil.rmtree(f'{CMI_DUMP}', ignore_errors=True)
    shutil.rmtree(f'{CMI_EXPORT}', ignore_errors=True)
    if arguments.debug:
        os.mkdir(f'{CMI_DUMP}')
        os.mkdir(f'{CMI_EXPORT}')

    session = requests.Session()
    session.auth = (arguments.user, arguments.password)
    session.headers.update({'Accept': '*/*'})
    session.headers.update({'User-Agent': 'Winsol/1.0'})

    infoh = __get_infoh(arguments, session)
    info = __get_info(arguments, session, infoh)
    events = __get_events(arguments, session, infoh, info)


if __name__ == '__main__':
    main()
