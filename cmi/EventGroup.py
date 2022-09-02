# -*- coding: utf-8 -*-

import struct

import cmi


class EventGroup:
    def __init__(self, id: str, fields: list[cmi.Field], events: list[cmi.Event]):
        self.id = id
        self.fields = fields
        self.events = events

    def export(self, f, encoding: str):
        f.write(self.id)
        f.write(bytes('\r\n', encoding=encoding))

        analog = 0
        digital = 0
        for field in self.fields:
            if field.type == cmi.FieldType.ANALOG:
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

        offset = 0
        payload = array[1]
        analog, digital = struct.unpack_from('<HH', payload, offset=offset)
        offset = offset + 4

        fields = []
        for i in range(analog + digital):
            field = cmi.Field.parse(payload, offset, encoding)
            fields.append(field)
            offset = offset + 80

        events = []
        index = 1
        for data in array[2:-1]:
            index = index + 1
            length = len(data)

            offset = 0
            for field in fields:
                size = field.size
                if (offset + size) > length:
                    print(f'skipping [{index}/{len(array)}] @{offset} ({size}) / {length}')
                    continue

                event = cmi.Event.parse(data, offset, field, encoding)
                offset = offset + size
                if event is not None:
                    events.append(event)

        return EventGroup(array[0], fields, events)
