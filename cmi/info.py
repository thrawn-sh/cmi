# -*- coding: utf-8 -*-

from cmi.header import Header
from cmi.info import Info
from cmi.log_file import LogFile


class Info:
    def __init__(self, header: Header, log_files: LogFile) -> None:
        self.header = header
        self.log_files = log_files

    def export(self, f, encoding: str) -> None:
        self.header.export(f, encoding)
        f.write(b'\x00\x00\x00\x00')
        f.write(bytes('\r\n\r\n', encoding=encoding))

        for log_file in self.log_files:
            log_file.export(f, encoding)

    @classmethod
    def parse(cls, content: str, encoding: str) -> Info:
        array = content.split(b'\r\n')
        header = Header.parse(array, encoding)

        log_files = []
        for line in array[5:-1]:
            log_files.append(LogFile.parse(line, encoding))

        return Info(header, log_files)
