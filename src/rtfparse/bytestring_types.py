#!/usr/bin/env python


"""
Control Word Types
"""


from rtfparse import re_patterns


class Plain_Text:
    pass


class Group_Start:
    pass


class Group_End:
    pass


class Cwtype:
    default_delimiter = " "


class Flag(Cwtype):
    native_pattern = re_patterns.control_word
    def __init__(self, pattern: str) -> None:
        self.something = self.native_pattern.pattern.match((pattern + self.default_delimiter).encode("ascii"))


if __name__ == "__main__":
    pass
