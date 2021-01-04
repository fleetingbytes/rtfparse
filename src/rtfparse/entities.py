#!/usr/bin/env python


import io
import logging
import re
# Own modules
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
MAX_CW_LETTERS = 32 # As specified in RTF Spec
INTEGER_MAGNITUDE = 32 # As specified in RTF Spec
PLAIN_TEXT = CONTROL_WORD = BACKSLASH + MAX_CW_LETTERS + MINUS + len(str((1 << INTEGER_MAGNITUDE) // 2)) + DELIMITER


class Entity:
    def __init__(self) -> None:
        self.text = ""
    @classmethod
    def probe(cls, pattern: re_patterns.Bytes_Regex, file: io.BufferedReader) -> Bytestring_Type:
        logger.debug(f"Probing file at position {file.tell()}")
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
                    logger.debug(f"Reached unexpected end of file.")
                    result = Bytestring_Type.GROUP_END
                    break
                    # raise errors.UnexpectedEndOfFileError(f"at position {file.tell()}")
                continue
            break
        logger.debug(f"Probe {result = }")
        logger.debug(f"Probe leaving file at position {file.tell()}")
        return result


class Control_Word(Entity):
    def __init__(self, encoding: str, file: io.BufferedReader) -> None:
        super().__init__()
        self.encoding = encoding
        logger.debug(f"Reading Control Word at file position {file.tell()}")
        self.control_name = "missing"
        self.parameter = ""
        self.bindata = b""
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        probe = file.read(CONTROL_WORD)
        if (match := re_patterns.control_word.match(probe)):
            self.control_name = match.group("control_name").decode(self.encoding)
            logger.debug(f"Preliminary {self.control_name = }")
            parameter = match.group("parameter")
            if parameter is not None:
                self.parameter = int(parameter.decode(self.encoding))
                logger.debug(f"{self.parameter = }")
                self.control_name = self.control_name.removesuffix(str(self.parameter))
                logger.debug(f"Final {self.control_name = }")
            target_position = self.start_position + match.span()[1]
            if match.group("other"):
                logger.debug(f"Delimiter is {match.group('other').decode(self.encoding)}, len: {len(match.group('delimiter'))}")
                target_position -= len(match.group("delimiter"))
            file.seek(target_position)
            # handle \binN:
            if self.control_name == "bin":
               self.bindata = file.read(utils.twos_complement(self.parameter, INTEGER_MAGNITUDE))
        else:
            logger.warning(f"Missing Control Word")
            file.seek(self.start_position)
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.control_name}{self.parameter}>"


class Control_Symbol(Entity):
    def __init__(self, encoding: str, file: io.BufferedReader) -> None:
        super().__init__()
        self.encoding = encoding
        self.start_position = file.tell()
        logger.debug(f"Reading Symbol at file position {self.start_position}")
        self.char = ""
        self.text = chr(file.read(SYMBOL)[-1])
        if self.text == "'":
            self.char = file.read(SYMBOL).decode(self.encoding)
            self.text = bytes((int(self.char, base=16), )).decode(self.encoding)
            logger.debug(f"Encountered escaped ANSI character, read two more bytes: {self.char}, character: {self.text}")
            if self.text in "\\{}":
                file.seek(file.tell() - SYMBOL)
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.text}>"


class Plain_Text(Entity):
    def __init__(self, encoding: str, file: io.BufferedReader) -> None:
        super().__init__()
        self.encoding = encoding
        self.text = ""
        logger.debug(f"Constructing Plain_Text")
        while True:
            self.start_position = file.tell()
            read = file.read(PLAIN_TEXT)
            logger.debug(f"Read file from {self.start_position} to position {file.tell()}, read: {read}")
            # see if we have read all the plain text there is:
            if (match := re_patterns.plain_text.match(read)):
                logger.debug(f"This matches the plain text pattern")
                _text = match.group("text").decode(self.encoding)
                logger.debug(f"{_text = }")
                self.text = "".join((self.text, _text))
                logger.debug(f"{self.text = }")
                if len(_text) == PLAIN_TEXT:
                    continue
                else:
                    file.seek(self.start_position + len(_text))
                    break
            else:
                file.seek(self.start_position)
                break
        logger.debug(f"Returned to position {file.tell()}")
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.text}>"


class Group(Entity):
    def __init__(self, encoding: str, file: io.BufferedReader) -> None:
        super().__init__()
        logger.debug(f"Group.__init__")
        self.encoding = encoding
        self.known = False
        self.name = "unknown"
        self.ignorable = False
        self.structure = list()
        parsed_object = utils.what_is_being_parsed(file)
        logger.debug(f"Creating destination group from {parsed_object}")
        self.start_position = file.tell()
        logger.debug(f"Starting at file position {self.start_position}")
        probe = file.read(GROUP_START)
        logger.debug(f"Read file up to position {file.tell()}, read {probe = }")
        if (match := re_patterns.group_start.match(probe)):
            self.known = bool(match.group("group_start"))
            self.ignorable = bool(match.group("ignorable"))
            if not self.ignorable:
                file.seek(self.start_position + GROUP_START - IGNORABLE)
                logger.debug(f"Returned to position {file.tell()}")
        else:
            logger.warning(utils.warn(f"Expected a group but found no group start. Creating unknown group"))
            file.seek(self.start_position)
        while True:
            probed = self.probe(re_patterns.probe, file)
            if probed is Bytestring_Type.CONTROL_WORD:
                self.structure.append(Control_Word(self.encoding, file))
            elif probed is Bytestring_Type.GROUP_END:
                file.read(GROUP_END)
                break
            elif probed is Bytestring_Type.GROUP_START:
                self.structure.append(Group(self.encoding, file))
            elif probed is Bytestring_Type.CONTROL_SYMBOL:
                self.structure.append(Control_Symbol(self.encoding, file))
            else:
                self.structure.append(Plain_Text(self.encoding, file))
        # name the group like its first Control Word
        # this way the renderer will be able to ignore entire groups based on their first control word
        try:
            if isinstance(self.structure[0], Control_Word):
                self.name = self.structure[0].control_name
        except IndexError:
            pass
    def __repr__(self) -> str:
        return f"<Group {self.name}>"


if __name__ == "__main__":
    pass
