#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import datetime

from cmi.info import Info
from cmi.info_h import InfoH
from cmi.event_group import EventGroup

CMI_DUMP = 'cmi-original'
CMI_EXPORT = 'cmi-export'


class Configuration:

    def __init__(self, host: str = 'cmi', port: int = 80, user: str = 'cmi', password: str = '', encoding: str = 'Windows-1252', after: datetime.date = datetime.date(1970, 1, 1), before: datetime.date = datetime.date.today(), debug: bool = False) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.encoding = encoding
        self.after = after
        self.before = before
        self.debug = debug


class Data:

    def __init__(self, infoH: InfoH, info: Info, groups: list[EventGroup]) -> None:
        self.infoH = infoH
        self.info = Info
        self.groups = groups


class Extractor:

    @classmethod
    def __basename_to_date(cls, basename: str) -> datetime.date:
        return datetime.datetime.strptime(basename, 'data_%Y_%m_%d_%H_%M_%S.log').date()

    @classmethod
    def __dump_content(cln, content, name: str) -> None:
        with open(f'{CMI_DUMP}/{name}', 'wb') as f:
            f.write(content)

    @classmethod
    def __get_info(cls, configuration, session, infoh: InfoH) -> Info:
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
    def __get_infoh(cls, configuration, session) -> InfoH:
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
    def __get_event_groups(cls, configuration, session, infoh: InfoH, info: Info) -> list[EventGroup]:
        groups = []
        for log_file in info.log_files:
            path = log_file.path
            basename = os.path.basename(path)
            date = Extractor.__basename_to_date(basename)
            if configuration.after > date:
                continue
            if configuration.before < date:
                continue

            url = f'http://{configuration.host}:{configuration.port}{path}'
            if configuration.debug:
                print(url)

            url = f'http://{configuration.host}:{configuration.port}{path}'
            response = session.get(url)
            filename = f'LOG/{basename}'
            if configuration.debug:
                Extractor.__dump_content(response.content, filename)

            group = EventGroup.parse(response.content, configuration.encoding)
            groups.append(group)
            if configuration.debug:
                with open(f'{CMI_EXPORT}/LOG/{filename}', 'wb') as f:
                    group.export(f, configuration.encoding)

        return groups

    @classmethod
    def process(cls, configuration: Configuration) -> Data:
        session = requests.Session()
        session.auth = (configuration.user, configuration.password)
        session.headers.update({'Accept': '*/*'})
        session.headers.update({'User-Agent': 'Winsol/1.0'})

        infoh = Extractor.__get_infoh(configuration, session)
        info = Extractor.__get_info(configuration, session, infoh)
        groups = Extractor.__get_event_groups(configuration, session, infoh, info)
        return Data(infoh, info, groups)
