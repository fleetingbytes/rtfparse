#!/usr/bin/env python


import io
import re
import logging
from pyrtfparse import re_patterns


# Setup logging
logger = logging.getLogger(__name__)


class Rtf_Parser:
    probe_len = 42
    def matchseek(self, pattern: re.Pattern, file: io.BufferedReader) -> re.Match:
        if (match := pattern.match(file.read(self.probe_len))):
            logger.debug(f"{match = }")
            file.seek(match.span()[1])
            return match
    def parse_file(self, file: io.BufferedReader) -> None:
        logger.debug(f"Parsing file {file.name}")
        try:
            if (match := self.matchseek(re_patterns.group_start, file)):
                logger.debug(f"{match.span() = }")
        except Exception as err:
            logger.error(f"Error: {err}")
        finally:
            logger.debug(f"Parsing file {file.name} finished")


if __name__ == "__main__":
    pass
