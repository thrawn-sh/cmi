# -*- coding: utf-8 -*-

import struct

from cmi.field import Field


class EventValue:
    def __init__(self, field: Field, value):
        self.field = field
        self.value = value

    def export(self, f, encoding: str):
        size = self.field.size
        if size == 0:
            return

        if size == 1:
            f.write(struct.pack('<?', self.value))
            return

        if size == 4:
            f.write(struct.pack('<i', self.value))
            return

    @classmethod
    def parse(cls, content: str, offset: int, field, encoding: str):
        size = field.size
        if size == 0:
            return None

        if size == 1:
            value = bool(struct.unpack_from('<?', content, offset=offset)[0])
            return EventValue(field, value)

        if size == 4:
            value = int(struct.unpack_from('<i', content, offset=offset)[0])
            return EventValue(field, value)
