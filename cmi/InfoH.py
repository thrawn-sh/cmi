# -*- coding: utf-8 -*-

import struct

import cmi


class InfoH:
    def __init__(self, header: cmi.Header, fields: list[cmi.Field], folder):
        self.header = header
        self.fields = fields
        self.folder = folder

    def export(self, f, encoding: str):
        self.header.export(f, encoding)

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
        f.write(bytes(f'{self.folder}\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, encoding: str):
        array = content.split(b'\r\n')
        header = cmi.Header.parse(array, encoding)

        offset = 0
        payload = array[3]
        analog, digital = struct.unpack_from('<HH', payload, offset=offset)
        offset = offset + 4

        fields = []
        for i in range(analog + digital):
            fields.append(cmi.Field.parse(payload, offset, encoding))
            offset = offset + 80

        folder = array[-2].decode(encoding)
        return InfoH(header, fields, folder)
