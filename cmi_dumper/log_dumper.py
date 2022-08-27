#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import requests
import shutil

CMI_DUMP = 'cmi-original'
CMI_EXPORT  = 'cmi-export'
ENCODING = 'ASCII'

def decode(data: str):
    return data.decode(ENCODING)


def parse_header(data: list):
    logger = decode(data[0])
    version = decode(data[1]).split(' ')
    storekrit = decode(data[2]).split(' ')
    return {
        'logger': logger,
        'version': {
            'firmware': version[0],
            'bootsector': version[1],
            'format': version[2],
            'revision': version[4]
        },
        'storekrit': storekrit[1]
    }


def export_header(header, f):
    f.write(bytes(f'{header["logger"]}\r\n', encoding=ENCODING))
    version = header['version']
    f.write(bytes(f'{version["firmware"]} {version["bootsector"]} {version["format"]} Revision: {version["revision"]}\r\n', encoding=ENCODING))
    f.write(bytes(f'storekrit: {header["storekrit"]}\r\n', encoding=ENCODING))


def parse_info(content: str):
    array = content.split(b'\r\n')
    header = parse_header(array)

    files = []
    for file in array[5:-1]:
        parts = decode(file).split(' ')
        files.append({
            'path': parts[0],
            'size': int(parts[1])
        })

    return {
        'header': header,
        'files': files
    }


def export_info(info, name: str):
    with open(f'{CMI_EXPORT}/{name}', 'wb') as f:
        export_header(info['header'], f)
        f.write(b'\x00\x00\x00\x00')
        f.write(bytes('\r\n\r\n', encoding=ENCODING))

        for file in info["files"]:
            f.write(bytes(f'{file["path"]} {file["size"]}\r\n', encoding=ENCODING))


def parse_infoh(content: str):
    array = content.split(b'\r\n')
    header = parse_header(array)

    # FIXME parse data
    lines = array[3:-3]

    folder = decode(array[-2])
    return {
        'header': header,
        'lines': lines,
        'folder': folder
    }


def export_infoh(infoh, name: str):
    with open(f'{CMI_EXPORT}/{name}', 'wb') as f:
        export_header(infoh['header'], f)
        for line in infoh['lines']:
            f.write(line)
        f.write(bytes('\r\n', encoding=ENCODING))
        f.write(bytes(f'{infoh["folder"]}\r\n', encoding=ENCODING))



def parse_log(content: str):
    array = content.split(b'\r\n')
    print(len(array))
    return array


def dump_content(content, name: str):
    with open(f'{CMI_DUMP}/{name}', 'wb') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description='query data from C.M.I', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', default=False, type=bool, help='Generate debug output and file', action=argparse.BooleanOptionalAction)
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

    url = f'http://{arguments.host}:{arguments.port}/LOG/infoh.log'
    if arguments.debug: print(url)
    response = session.get(url)
    if arguments.debug: dump_content(response.content, 'infoh.log')
    infoh = parse_infoh(response.content)
    if arguments.debug: export_infoh(infoh, 'infoh.log')

    url = f'http://{arguments.host}:{arguments.port}/LOG/info{infoh["folder"]}.log'
    if arguments.debug: print(url)
    response = session.get(url)
    if arguments.debug: dump_content(response.content, f'info{infoh["folder"]}.log')
    info = parse_info(response.content)
    if arguments.debug: export_info(info, f'info{infoh["folder"]}.log')

    for file in info['files']:
        url = f'http://{arguments.host}:{arguments.port}{file["path"]}'
        if arguments.debug: print(url)

        response = session.get(url)
        filename = os.path.basename(file["path"])
        if arguments.debug: dump_content(response.content, filename)
        log = parse_log(response.content)
        #if arguments.debug: export_log(log, filename)


if __name__ == '__main__':
    main()
