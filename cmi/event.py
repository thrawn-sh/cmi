# -*- coding: utf-8 -*-

import datetime
import struct

from cmi.event_value import EventValue
from cmi.field       import Field


class Event:
    def __init__(self, time: datetime.datetime, values: EventValue):
        self.time = time
        self.values = values

    def export(self, f, encoding:str):
        # FIXME
        f.write(bytes('\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, fields: list[Field], encoding: str):
        offset = 0
        # parse timestamp
        day, month, year, second, minute, hour = struct.unpack_from('<BBBBBBxx', content, offset=offset)
        offset = offset + 8
        time = datetime.datetime.strptime(f'{2000+year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}', '%Y-%m-%d %H:%M:%S')

        values = []
        for field in fields:
            value = EventValue.parse(content, offset, field, encoding)
            offset = offset + field.size
            if value is not None:
                values.append(value)

        return Event(time, values)
