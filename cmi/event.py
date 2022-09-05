# -*- coding: utf-8 -*-

import datetime
import struct

from cmi.event_value import EventValue
from cmi.field import Field


class Event:
    def __init__(self, time: datetime.datetime, values: EventValue, checksum: int):
        self.time = time
        self.values = values
        self.checksum = checksum

    def export(self, f, encoding: str):
        time = self.time
        f.write(struct.pack('<BBBBBBxx', time.day, time.month, (time.year - 2000), time.second, time.minute, time.hour))
        for value in self.values:
            value.export(f, encoding)
        f.write(struct.pack('<I', self.checksum))

    @classmethod
    def parse(cls, content: str, fields: list[Field], offset: int, encoding: str):
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

        checksum = int(struct.unpack_from('<I', content, offset=offset)[0])

        return Event(time, values, checksum)
