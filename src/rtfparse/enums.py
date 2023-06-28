#!/usr/bin/env python


from enum import Enum, auto, unique


@unique
class Bytestring_Type(Enum):
    GROUP_START = auto()
    GROUP_END = auto()
    CONTROL_WORD = auto()
    CONTROL_SYMBOL = auto()
    PLAIN_TEXT = auto()


if __name__ == "__main__":
    pass
