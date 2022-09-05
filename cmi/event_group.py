# -*- coding: utf-8 -*-

import struct

from cmi.event import Event
from cmi.field import Field, FieldType


class EventGroup:
    def __init__(self, id: str, fields: list[Field], events: list[Event]):
        self.id = id
        self.fields = fields
        self.events = events

    def export(self, f, encoding: str):
        f.write(self.id)
        f.write(bytes('\r\n', encoding=encoding))

        analog = 0
        digital = 0
        for field in self.fields:
            if field.type == FieldType.ANALOG:
                analog = analog + 1
            else:
                digital = digital + 1
        f.write(struct.pack('<HH', analog, digital))

        for field in self.fields:
            field.export(f, encoding)
        f.write(bytes('\r\n\r\n', encoding=encoding))

        for event in self.events:
            event.export(f, encoding)
            f.write(bytes('\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, encoding: str):
        id, analog, digital = struct.unpack_from('<8sxxHH', content, offset=0)
        offset = 14 # id(8) + \r\n(2) + counts(4)

        fields = []
        event_size = 14 # timestamp(6) + values(?) + checksum(6) + \r\n(2)
        for i in range(analog + digital):
            field = Field.parse(content, offset, encoding)
            event_size = event_size + field.size
            fields.append(field)
            offset = offset + 80

        offset = offset + 4 # \r\n\r\n(4)

        total_size = len(content)
        events = []
        while (offset + event_size) <= len(content):
            event = Event.parse(content, fields, offset, encoding)
            events.append(event)
            offset = offset + event_size

        return EventGroup(id, fields, events)
