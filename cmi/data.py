# -*- coding: utf-8 -*-

import datetime
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
    def __init__(self, header: Header, lines: list, folder):
        self.header = header
        self.lines = lines
        self.folder = folder

    def export(self, f, encoding: str):
        self.header.export(f, encoding)
        for line in self.lines:
            f.write(line)
        f.write(bytes('\r\n', encoding=encoding))
        f.write(bytes(f'{self.folder}\r\n', encoding=encoding))

    @classmethod
    def parse(cls, content: str, encoding: str):
        array = content.split(b'\r\n')
        header = Header.parse(array, encoding)

        # FIXME parse data
        lines = array[3:-3]

        folder = array[-2].decode(encoding)
        return InfoH(header, lines, folder)
