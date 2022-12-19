# -*- coding: utf-8 -*-

from cmi.header import Header
from cmi.log_file import LogFile


class Info:
    def __init__(self, folder: str, header: Header, log_files: list[LogFile], raw: str = None) -> None:
        self.folder = folder
        self.header = header
        self.log_files = log_files
        self.raw = raw

    def export(self, f, encoding: str) -> None:
        self.header.export(f, encoding)
        f.write(b'\x00\x00\x00\x00')
        f.write(bytes('\r\n\r\n', encoding=encoding))

        for log_file in self.log_files:
            log_file.export(f, encoding)

    @classmethod
    def parse(cls, folder: str, content: str, encoding: str, store: bool):
        array = content.split(b'\r\n')
        header = Header.parse(array, encoding)

        log_files = []
        for line in array[5:-1]:
            log_files.append(LogFile.parse(line, encoding))

        if store:
            return Info(folder, header, log_files, content)
        return Info(folder, header, log_files)
