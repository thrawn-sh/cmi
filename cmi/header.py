# -*- coding: utf-8 -*-

from cmi.version import Version


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
    def parse(cls, data: list[str], encoding: str):
        logger = data[0].decode(encoding)
        version = Version.parse(data[1], encoding)
        storekrit = data[2].decode(encoding).split(' ')
        return Header(logger, version, storekrit[1])
