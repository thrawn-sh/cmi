# -*- coding: utf-8 -*-

import enum
import struct


class FieldType(enum.IntEnum):
    ANALOG = 0
    DIGITAL = 1


class FieldUnit(enum.IntEnum):
    CELCIUS = 1
    VOLT = 13
    BOOLEAN = 43


class Field:
    def __init__(self, source: int, frame: int, can_id: int, device: int, count: int, type: FieldType, id3: int, unit: FieldUnit, format: int, size: int, description: str) -> None:
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

    def export(self, f, encoding: str) -> None:
        description = self.description
        description = '\x00'.join(description[i:i+1] for i in range(0, len(description), 1))
        description = bytes(description, encoding=encoding)
        packed = struct.pack('<BBBBBBBxBBBxxxxxxx62s', self.source, self.frame, self.can_id, self.device, self.count, self.type, self.id3, self.unit, self.format, self.size, description)
        f.write(packed)

    @classmethod
    def parse(cls, content: str, offset: int, encoding: str):
        source, frame, can_id, device, count, type, id3, unit, format, size, description = struct.unpack_from('<BBBBBBBxBBBxxxxxxx62s', content, offset=offset)
        description = description.decode(encoding)
        description = description.replace('\x00', '')
        return Field(source, frame, can_id, device, count, type, id3, unit, format, size, description)
