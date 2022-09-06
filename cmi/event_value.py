# -*- coding: utf-8 -*-

import struct

from cmi.field import Field, FieldUnit


class EventValue:
    def __init__(self, field: Field, value):
        self.field = field
        self.value = value

    def export(self, f, encoding: str):
        size = self.field.size
        if size == 0:
            return

        format = ''
        if size == 1:
            format = '<b'
        if size == 4:
            format = '<i'

        value = self.value
        if self.field.unit == FieldUnit.BOOLEAN:
            value = int(value)
        if self.field.unit == FieldUnit.CELCIUS:
            value = value * 10
        if self.field.unit == FieldUnit.VOLT:
            value = value * 100

        f.write(struct.pack(format, value))

    @classmethod
    def parse(cls, content: str, offset: int, field, encoding: str):
        size = field.size
        if size == 0:
            return None

        format = ''
        if size == 1:
            format = '<b'
        if size == 4:
            format = '<i'

        value = struct.unpack_from(format, content, offset=offset)[0]
        if field.unit == FieldUnit.BOOLEAN:
            return EventValue(field, bool(value))
        if field.unit == FieldUnit.CELCIUS:
            return EventValue(field, int(value) / 10)
        if field.unit == FieldUnit.VOLT:
            return EventValue(field, int(value) / 100)
