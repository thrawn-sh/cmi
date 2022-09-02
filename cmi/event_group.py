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
        f.write(bytes('\r\n\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, encoding: str):
        array = content.split(b'\r\n')

        id = array[0]

        offset = 0
        payload = array[1]
        analog, digital = struct.unpack_from('<HH', payload, offset=offset)
        offset = offset + 4

        fields = []
        for i in range(analog + digital):
            field = Field.parse(payload, offset, encoding)
            fields.append(field)
            offset = offset + 80

        events = []
        for data in array[3:-1]:
            events.append(Event.parse(data, fields, encoding))

        return EventGroup(array[0], fields, events)
