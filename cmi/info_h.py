# -*- coding: utf-8 -*-

import struct

from cmi.field import Field, FieldType
from cmi.header import Header


class InfoH:
    def __init__(self, header: Header, fields: list[Field], folders: list[str], raw: str = None) -> None:
        self.header = header
        self.fields = fields
        self.folders = folders
        self.raw = raw

    def export(self, f, encoding: str) -> None:
        self.header.export(f, encoding)

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

        for folder in self.folders:
            f.write(bytes(f'{folder}\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, encoding: str, store: bool):
        array = content.split(b'\r\n')
        header = Header.parse(array, encoding)

        offset = 0
        payload = array[3]
        analog, digital = struct.unpack_from('<HH', payload, offset=offset)
        offset = offset + 4

        fields = []
        for i in range(analog + digital):
            fields.append(Field.parse(payload, offset, encoding))
            offset = offset + 80

        folders = array[5:-1]
        for i, element in enumerate(folders):
            folders[i] = element.decode(encoding)

        if store:
            return InfoH(header, fields, folders, content)
        return InfoH(header, fields, folders)
