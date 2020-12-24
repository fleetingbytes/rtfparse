#!/usr/bin/env python


import io
import logging
import re
from rtfparse import re_patterns
from rtfparse import utils
from rtfparse.enums import Bytestring_Type


# Setup logging
logger = logging.getLogger(__name__)


# Constants, number of bytes to read when creating entities
CHARACTER = BACKSLASH = len(b"\\")
IGNORABLE = BACKSLASH + len(rb"*")
GROUP_START = len(rb"x") + IGNORABLE # x = "}" cannot have a rogue brace for vim's auto-indent's sake
DELIMITER = len(rb" ")
MAX_CW_LETTERS = 32
INTEGER_MAGNITUDE = 32
CONTROL_WORD = BACKSLASH + MAX_CW_LETTERS + len(rb"-") + len(str((1 << INTEGER_MAGNITUDE) // 2)) + DELIMITER


class Entity:
    @classmethod
    def probe(cls, pattern: re_patterns.Bytes_Regex, file: io.BufferedReader) -> Bytestring_Type:
        logger.debug(f"in Entity.probed")
        original_position = file.tell()
        probed = file.read(len(re_patterns.probe_pattern))
        logger.debug(f"{probed = }")
        file.seek(original_position - len(probed))
        if (match := re_patterns.group_start.match(probed)):
            result = Bytestring_Type.GROUP_START
        elif (match := re_patterns.group_end.match(probed)):
            result = Bytestring_Type.GROUP_END
        elif (match := re_patterns.control_word.match(probed)):
            result = Bytestring_Type.CONTROL_WORD
        elif (match := re_patterns.control_symbol.match(probed)):
            result = Bytestring_Type.CONTROL_SYMBOL
        else:
            result = Bytestring_Type.PLAIN_TEXT
        logger.debug(f"{result = }")
        return result


class Control_Word(Entity):
    def __init__(self, file: io.BufferedReader) -> None:
        logger.debug(f"Control_Word.__init__")
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        probe = file.read(CONTROL_WORD)
        if (match := re_patterns.control_word.match(probe)):
            self.control_name = match.group("control_name")
            logger.debug(f"{self.control_name = }")
            self.parameter = match.group("parameter")
            file.seek(self.start_position + match.span()[1])


class Destination_Group(Entity):
    def __init__(self, file: io.BufferedReader) -> None:
        logger.debug(f"Destination_Group.__init__")
        logger.debug(f"Creating destination group from {file.name}")
        self.known = False
        self.name = "unknown"
        self.ignorable = False
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        probe = file.read(GROUP_START)
        logger.debug(f"Read file up to position {file.tell()}")
        if (match := re_patterns.group_start.match(probe)):
            self.known = bool(match.group("group_start"))
            self.ignorable = bool(match.group("ignorable"))
            if not self.ignorable:
                file.seek(-IGNORABLE, io.SEEK_CUR)
                logger.debug(f"Returned to position {file.tell()}")
            self.cw = Control_Word(file)
            self.name = self.cw.control_name
        else:
            logger.warning(utils.warn(f"Expected group has no start. Creating unknown group"))
        probed = self.probe(re_patterns.probe, file)
        self.content = list()


if __name__ == "__main__":
    pass
