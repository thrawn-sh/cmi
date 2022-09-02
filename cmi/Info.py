# -*- coding: utf-8 -*-

import cmi


class Info:
    def __init__(self, header: cmi.Header, log_files: cmi.LogFile):
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
        header = cmi.Header.parse(array, encoding)

        log_files = []
        for line in array[5:-1]:
            log_files.append(cmi.LogFile.parse(line, encoding))

        return Info(header, log_files)
