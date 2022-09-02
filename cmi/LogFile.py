# -*- coding: utf-8 -*-

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
