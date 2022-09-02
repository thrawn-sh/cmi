# -*- coding: utf-8 -*-

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
