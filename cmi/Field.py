# -*- coding: utf-8 -*-

import struct

import cmi


class Field:
    def __init__(self, source: int, frame: int, can_id: int, device: int, count: int, type: cmi.FieldType, id3: int, unit: int, format: int, size: int, description: str):
        self.source = source
        self.frame = frame
        self.can_id = can_id
        self.device = device
        self.count = count
        self.type = type
        self.id3 = id3
        self.unit = unit
        self.format = format
        self.size = size
        self.description = description

    def export(self, f, encoding: str):
        encoded_description = bytes(self.description, encoding=encoding)
        packed = struct.pack('<BBBBBBBxBBBxxxxxxx62s', self.source, self.frame, self.can_id, self.device, self.count, self.type, self.id3, self.unit, self.format, self.size, encoded_description)
        f.write(packed)

    @classmethod
    def parse(cls, content: str, offset: int, encoding: str):
        source, frame, can_id, device, count, type, id3, unit, format, size, description = struct.unpack_from('<BBBBBBBxBBBxxxxxxx62s', content, offset=offset)
        description = description.decode(encoding)
        return Field(source, frame, can_id, device, count, type, id3, unit, format, size, description)
