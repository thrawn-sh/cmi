#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests

from cmi.info import Info
from cmi.info_h import InfoH
from cmi.event_group import EventGroup

CMI_DUMP = 'cmi-original'
CMI_EXPORT = 'cmi-export'


class Configuration:

    def __init__(self, host='cmi', port=80, user='cmi', password='', encoding='Windows-1252', debug=False):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.encoding = encoding
        self.debug = debug


class Data:

    def __init__(self, infoH: InfoH, info: Info, groups: list[EventGroup]):
        self.infoH = infoH
        self.info = Info
        self.groups = groups


class Extractor:

    @classmethod
    def __dump_content(cln, content, name: str):
        with open(f'{CMI_DUMP}/{name}', 'wb') as f:
            f.write(content)

    @classmethod
    def __get_info(cls, configuration, session, infoh: InfoH):
        folder = infoh.folder
        url = f'http://{configuration.host}:{configuration.port}/LOG/info{infoh.folder}.log'
        if configuration.debug:
            print(url)

        response = session.get(url)
        if configuration.debug:
            Extractor.__dump_content(response.content, f'info{folder}.log')
        info = Info.parse(response.content, configuration.encoding)
        if configuration.debug:
            with open(f'{CMI_EXPORT}/info{folder}.log', 'wb') as f:
                info.export(f, configuration.encoding)

        return info

    @classmethod
    def __get_infoh(cls, configuration, session):
        url = f'http://{configuration.host}:{configuration.port}/LOG/infoh.log'
        if configuration.debug:
            print(url)

        response = session.get(url)
        if configuration.debug:
            Extractor.__dump_content(response.content, 'infoh.log')
        infoh = InfoH.parse(response.content, configuration.encoding)

        if configuration.debug:
            with open(f'{CMI_EXPORT}/infoh.log', 'wb') as f:
                infoh.export(f, configuration.encoding)

        return infoh

    @classmethod
    def __get_event_groups(cls, configuration, session, infoh: InfoH, info: Info):
        groups = []
        for log_file in info.log_files:
            path = log_file.path
            url = f'http://{configuration.host}:{configuration.port}{path}'
            if configuration.debug:
                print(url)

            response = session.get(url)
            filename = f'LOG/{os.path.basename(path)}'
            if configuration.debug:
                Extractor.__dump_content(response.content, filename)

            group = EventGroup.parse(response.content, configuration.encoding)
            groups.append(group)
            if configuration.debug:
                with open(f'{CMI_EXPORT}/LOG/{filename}', 'wb') as f:
                    group.export(f, configuration.encoding)

        return groups

    @classmethod
    def process(cls, configuration: Configuration):
        session = requests.Session()
        session.auth = (configuration.user, configuration.password)
        session.headers.update({'Accept': '*/*'})
        session.headers.update({'User-Agent': 'Winsol/1.0'})

        infoh = Extractor.__get_infoh(configuration, session)
        info = Extractor.__get_info(configuration, session, infoh)
        return Extractor.__get_event_groups(configuration, session, infoh, info)
