#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import datetime

from cmi.info import Info
from cmi.info_h import InfoH
from cmi.event_group import EventGroup


class Configuration:

    def __init__(self, host: str = 'cmi', port: int = 80, user: str = 'cmi', password: str = '', encoding: str = 'Windows-1252', after: datetime.date = datetime.date(1970, 1, 1), before: datetime.date = datetime.date.today(), store_raw: bool = False) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.encoding = encoding
        self.after = after
        self.before = before
        self.store_raw = store_raw


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
    def __get_info(cls, configuration, session, infoh: InfoH) -> Info:
        url = f'http://{configuration.host}:{configuration.port}/LOG/info{infoh.folder}.log'
        response = session.get(url)
        return Info.parse(response.content, configuration.encoding, configuration.store_raw)

    @classmethod
    def __get_infoh(cls, configuration, session) -> InfoH:
        url = f'http://{configuration.host}:{configuration.port}/LOG/infoh.log'
        response = session.get(url)
        return InfoH.parse(response.content, configuration.encoding, configuration.store_raw)

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
            response = session.get(url)

            group = EventGroup.parse(response.content, configuration.encoding, configuration.store_raw)
            groups.append(group)
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
