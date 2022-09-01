# -*- coding: utf-8 -*-

import datetime
import enum
import struct


class Version:
    def __init__(self, firmware: str, bootsector: str, file_format: str, revision: str):
        self.firmware = firmware
        self.bootsector = bootsector
        self.file_format = file_format
        self.revision = revision

    def export(self, f, encoding: str):
        f.write(bytes(f'{self.firmware} {self.bootsector} {self.file_format} Revision: {self.revision}\r\n', encoding=encoding))

    @classmethod
    def parse(cls, data: str, encoding: str):
        version = data.decode(encoding).split(' ')
        return Version(version[0], version[1], version[2], version[4])


class Header:
    def __init__(self, logger: str, version: Version, storekrit: str):
        self.logger = logger
        self.version = version
        self.storekrit = storekrit

    def export(self, f, encoding: str):
        f.write(bytes(f'{self.logger}\r\n', encoding=encoding))
        self.version.export(f, encoding)
        f.write(bytes(f'storekrit: {self.storekrit}\r\n', encoding=encoding))

    @classmethod
    def parse(cls, data: list, encoding: str):
        logger = data[0].decode(encoding)
        version = Version.parse(data[1], encoding)
        storekrit = data[2].decode(encoding).split(' ')
        return Header(logger, version, storekrit[1])


class Entry:
    def __init__(self, time: datetime, analog: list, digital: list):
        self.time = time
        self.analog = analog
        self.digital = digital


class LogFile:
    def __init__(self, path: str, size: int):
        self.path = path
        self.size = size

    def export(self, f, encoding: str):
        f.write(bytes(f'{self.path} {self.size}\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, encoding: str):
        parts = content.decode(encoding).split(' ')
        return LogFile(parts[0], int(parts[1]))


class Info:
    def __init__(self, header: Header, log_files: LogFile):
        self.header = header
        self.log_files = log_files

    def export(self, f, encoding: str):
        self.header.export(f, encoding)
        f.write(b'\x00\x00\x00\x00')
        f.write(bytes('\r\n\r\n', encoding=encoding))

        for log_file in self.log_files:
            log_file.export(f, encoding)

    @classmethod
    def parse(cls, content: str, encoding: str):
        array = content.split(b'\r\n')
        header = Header.parse(array, encoding)

        log_files = []
        for line in array[5:-1]:
            log_files.append(LogFile.parse(line, encoding))

        return Info(header, log_files)


class InfoH:
    def __init__(self, header: Header, fields: list, folder):
        self.header = header
        self.fields = fields
        self.folder = folder

    def export(self, f, encoding: str):
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
        f.write(bytes(f'{self.folder}\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, encoding: str):
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

        folder = array[-2].decode(encoding)
        return InfoH(header, fields, folder)


class FieldType(enum.IntEnum):
    ANALOG = 0
    DIGITAL = 1


class Field:
    def __init__(self, source: int, frame: int, can_id: int, device: int, count: int, type: FieldType, id3: int, unit: int, format: int, size: int, description: str):
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
