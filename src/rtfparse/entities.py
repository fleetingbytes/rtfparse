#!/usr/bin/env python


import io
import logging
import re
from itertools import count
from rtfparse import re_patterns
from rtfparse import utils
from rtfparse import errors
from rtfparse.enums import Bytestring_Type


# Setup logging
logger = logging.getLogger(__name__)


# Constants, number of bytes to read when creating entities
CHARACTER = BACKSLASH = DELIMITER = MINUS = GROUP_END = len(b"\\")
SYMBOL = IGNORABLE = BACKSLASH + CHARACTER
GROUP_START = BACKSLASH + IGNORABLE
MAX_CW_LETTERS = 32
INTEGER_MAGNITUDE = 32
PLAIN_TEXT = CONTROL_WORD = BACKSLASH + MAX_CW_LETTERS + MINUS + len(str((1 << INTEGER_MAGNITUDE) // 2)) + DELIMITER


class Entity:
    @classmethod
    def probe(cls, pattern: re_patterns.Bytes_Regex, file: io.BufferedReader) -> Bytestring_Type:
        logger.debug(f"in Entity.probed")
        original_position = file.tell()
        while True:
            probed = file.read(len(re_patterns.probe_pattern))
            logger.debug(f"{probed = }")
            file.seek(original_position)
            logger.debug(f"Probe returned to position {file.tell()}")
            if (match := re_patterns.group_start.match(probed)):
                result = Bytestring_Type.GROUP_START
            elif (match := re_patterns.group_end.match(probed)):
                result = Bytestring_Type.GROUP_END
            elif (match := re_patterns.control_word.match(probed)):
                result = Bytestring_Type.CONTROL_WORD
            elif (match := re_patterns.control_symbol.match(probed)):
                result = Bytestring_Type.CONTROL_SYMBOL
            elif (match := re_patterns.plain_text.match(probed)):
                result = Bytestring_Type.PLAIN_TEXT
            else:
                logger.debug(f"This does not match anything, it's probably a newline, moving on")
                original_position += 1
                file.seek(original_position)
                logger.debug(f"Probe moved to position {file.tell()}")
                if not probed:
                    logger.warning(f"Reached unexpected end of file.")
                    raise errors.UnexpectedEndOfFileError(f"at position {file.tell()}")
                continue
            break
        logger.debug(f"{result = }")
        logger.debug(f"Probe leaving file at position {file.tell()}")
        return result


class Control_Word(Entity):
    def __init__(self, file: io.BufferedReader) -> None:
        logger.debug(f"Control_Word.__init__")
        self.control_name = "missing"
        self.parameter = ""
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        probe = file.read(CONTROL_WORD)
        if (match := re_patterns.control_word.match(probe)):
            self.control_name = match.group("control_name").decode("ascii")
            logger.debug(f"{self.control_name = }")
            parameter = match.group("parameter")
            if parameter:
                self.parameter = int(parameter.decode("ascii"))
                logger.debug(f"{self.parameter = }")
            target_position = self.start_position + match.span()[1]
            if match.group("other"):
                logger.debug(f"Delimiter is {match.group('other').decode('ascii')}, len: {len(match.group('delimiter'))}")
                target_position -= len(match.group("delimiter"))
            file.seek(target_position)
        else:
            logger.warning(f"Missing Control Word")
            file.seek(self.start_position)
    def __repr__(self) -> str:
        name = self.control_name
        return f"<{self.__class__.__name__}: {name}{self.parameter}>"


class Control_Symbol(Entity):
    def __init__(self, file: io.BufferedReader) -> None:
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        self.text = file.read(SYMBOL)[-1].decode("ascii")
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.text}>"


class Plain_Text(Entity):
    def __init__(self, file: io.BufferedReader) -> None:
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        self.text = ""
        while True:
            read = file.read(PLAIN_TEXT)
            logger.debug(f"Read file up to position {file.tell()}")
            logger.debug(f"Read: {read}")
            # see if we have read all the plain text there is:
            if (match := re_patterns.plain_text.match(read)):
                logger.debug(f"This matches the plain text pattern")
                _text = match.group("text").decode("ascii")
                logger.debug(f"{_text = }")
                self.text = "".join((self.text, _text))
                logger.debug(f"{self.text = }")
                if len(_text) == PLAIN_TEXT:
                    continue
                else:
                    file.seek(self.start_position + len(self.text))
                    logger.debug(f"Returned to position {file.tell()}")
                    break
            else:
                break
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.text}>"


class Destination_Group(Entity):
    def __init__(self, file: io.BufferedReader) -> None:
        logger.debug(f"Destination_Group.__init__")
        self.known = False
        self.name = "unknown"
        self.ignorable = False
        self.structure = list()
        logger.debug(f"Creating destination group from {file.name}")
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        probe = file.read(GROUP_START)
        logger.debug(f"Read file up to position {file.tell()}, read {probe = }")
        if (match := re_patterns.group_start.match(probe)):
            self.known = bool(match.group("group_start"))
            self.ignorable = bool(match.group("ignorable"))
            if not self.ignorable:
                file.seek(-IGNORABLE, io.SEEK_CUR)
                logger.debug(f"Returned to position {file.tell()}")
        else:
            logger.warning(utils.warn(f"Expected a group but found no group start. Creating unknown group"))
            file.seek(self.start_position)
        self.cw = Control_Word(file)
        self.name = self.cw.control_name
        while True:
            probed = self.probe(re_patterns.probe, file)
            if probed is Bytestring_Type.CONTROL_WORD:
                self.structure.append(Control_Word(file))
            elif probed is Bytestring_Type.GROUP_END:
                file.read(GROUP_END)
                break
            elif probed is Bytestring_Type.GROUP_START:
                self.structure.append(Destination_Group(file))
            elif probed is Bytestring_Type.CONTROL_SYMBOL:
                self.structure.append(Control_Symbol(file))
            else:
                self.structure.append(Plain_Text(file))
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.cw.control_name}{self.cw.parameter}>"


if __name__ == "__main__":
    pass
