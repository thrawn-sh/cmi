# -*- coding: utf-8 -*-

import datetime


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

    @classmethod
    def older(cls, original: list, current: list) -> bool:
        if original is None:
            return False

        return current[0] < original[0]

    @classmethod
    def within_delta(cls, original: list, current: list, delta: datetime.timedelta) -> bool:
        if original is None:
            return False

        return (current[0] - original[0]) < delta
