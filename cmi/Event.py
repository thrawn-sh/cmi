# -*- coding: utf-8 -*-

import struct

import cmi


class Event:
    def __init__(self, field: cmi.Field, value):
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
    def parse(cls, content: str, offset: int, field: cmi.Field, encoding: str):
        size = field.size
        if size == 0:
            return None

        if size == 1:
            value = bool(struct.unpack_from('<?', content, offset=offset))
            return Event(field, value)

        if size == 4:
            value = struct.unpack_from('<i', content, offset=offset)[0]
            return Event(field, value)
