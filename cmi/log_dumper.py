#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import os
import requests
import shutil
import struct

import cmi

CMI_DUMP = 'cmi-original'
CMI_EXPORT = 'cmi-export'


def parse_log(content: str, fields: list, encoding: str):
    array = content.split(b'\r\n')

    entries = []
    for entry in array[3:]:
        if len(entry) != 98:
            continue

        offset = 0
        # parse timestamp
        day, month, year, second, minute, hour = struct.unpack_from('<BBBBBBxx', entry, offset=offset)
        offset = offset + 8
        time = datetime.datetime.strptime(f'{2000+year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}', '%Y-%m-%d %H:%M:%S')

        # parse analog
        analog = []
        for i in range(16):
            value = struct.unpack_from('<hxx', entry, offset=offset)
            analog.append(value)
            offset = offset + 4

        # parse digial
        digital = []

        entries.append(cmi.Entry(time, analog, digital))

    return entries


def __dump_content(content, name: str):
    with open(f'{CMI_DUMP}/{name}', 'wb') as f:
        f.write(content)


def __get_info(arguments, session, infoh: cmi.InfoH):
    folder = infoh.folder
    url = f'http://{arguments.host}:{arguments.port}/LOG/info{infoh.folder}.log'
    if arguments.debug:
        print(url)

    response = session.get(url)
    if arguments.debug:
        __dump_content(response.content, f'info{folder}.log')
    info = cmi.Info.parse(response.content, arguments.encoding)
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
    infoh = cmi.InfoH.parse(response.content, arguments.encoding)

    if arguments.debug:
        with open(f'{CMI_EXPORT}/infoh.log', 'wb') as f:
            infoh.export(f, arguments.encoding)

    return infoh


def __get_events(arguments, session, infoh: cmi.InfoH, info: cmi.Info):
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
        
        group = cmi.EventGroup.parse(response.content, arguments.encoding)
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
