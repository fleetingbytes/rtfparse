#!/usr/bin/env python


import io
import re
import logging
from collections import OrderedDict
from rtfparse import re_patterns
from rtfparse import entities


# Setup logging
logger = logging.getLogger(__name__)


class Rtf_Parser:
    probe_len = 42
    @classmethod
    def matchseek(cls, pattern: re.Pattern, file: io.BufferedReader) -> re.Match:
        original_position = file.tell()
        if (match := pattern.match(file.read(cls.probe_len))):
            logger.debug(f"{match = }")
            file.seek(original_position + match.span()[1])
            return match
    @staticmethod
    def start_group(match: re.Match) -> None:
        logger.debug(f"Starting group")
    @staticmethod
    def parse_cw(match: re.Match) -> None:
        logger.debug(f"Parsing control word")
    @staticmethod
    def parse_cs(match: re.Match) -> None:
        logger.debug(f"Parsing control symbol")
    @staticmethod
    def parse_text(match: re.Match) -> None:
        logger.debug(f"Parsing control symbol")
    @staticmethod
    def end_group(match: re.Match) -> None:
        logger.debug(f"Ending group")
    @staticmethod
    def probe(file: io.BufferedReader) -> None:
        original_position = file.tell()
        probed = file.read(cls.probe_len)
        file.seek(original_position)
    action_dict = OrderedDict(
        zip(
            (
                re_patterns.group_start,
                re_patterns.control_word,
                re_patterns.control_symbol,
                re_patterns.group_end,
                re_patterns.plain_text,
            ),
            (
                start_group,
                parse_cw,
                parse_cs,
                end_group,
                parse_text,
            ),
           )
    )
    def __init__(self) -> None:
        self.parsed = None
    def parse_file(self, file: io.BufferedReader) -> None:
        logger.debug(f"Parsing file {file.name}")
        try:
            self.parsed = entities.Destination_Group(file)
        except Exception as err:
            logger.error(f"Error: {err}")
        finally:
            logger.debug(f"Parsing file {file.name} finished")


if __name__ == "__main__":
    pass
