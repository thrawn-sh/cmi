# -*- coding: utf-8 -*-

class Filter:

    @classmethod
    def changed(cls, original: list, current: list) -> bool:
        if original is None:
            return True

        # skip timestamp
        length = len(original)
        for index in range(1, length):
            if original[index] != current[index]:
                return True
        return False
