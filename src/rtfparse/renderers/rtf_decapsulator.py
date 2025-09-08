#!/usr/bin/env python


import io
import logging

from rtfparse import entities, utils
from rtfparse.renderers import Renderer

# Setup logging
logger = logging.getLogger(__name__)

CRLF = "\r\n"
LF = "\n"


class Rtf_Decapsulator(Renderer):

    def __init__(self, preserve_ascii: bool = True, line_ending: str = LF) -> None:
        self.line_ending = line_ending
        self.preserve_ascii = preserve_ascii
        super().__init__()

    def render_group(self, group: entities.Group, file: io.TextIOWrapper) -> None:
        self.write(file, "{")
        if not group.structure or not isinstance(
            group.structure[0], entities.Control_Word
        ):
            if group.ignorable:
                self.write(file, group.ignorable.decode(group.encoding))
            self.write(file, group.name)

        for subitem in group.structure:
            self.render(subitem, file)

        self.write(file, "}")
        self.write(file, group.tail.decode(group.encoding))

    def write(self, file: io.TextIOWrapper, obj: str) -> int:

        if self.line_ending != CRLF and CRLF in obj:
            obj = obj.replace(CRLF, LF)

        return file.write(obj)

    def render(self, parsed: entities.Group, file: io.TextIOWrapper) -> None:
        if isinstance(parsed, entities.Group):
            self.render_group(parsed, file)
        elif isinstance(parsed, entities.Control_Word):
            self.write(
                file,
                f"\\{parsed.control_name}{parsed.parameter}{parsed.tail}{parsed.bindata.decode(parsed.encoding)}",
            )
        elif isinstance(parsed, entities.Control_Symbol):
            if parsed.is_ascii and self.preserve_ascii:
                self.write(file, f"\\'{parsed.char}")
            else:
                self.write(file, parsed.text)
        elif isinstance(parsed, entities.Plain_Text):
            self.write(file, parsed.text)
        else:
            pass


if __name__ == "__main__":
    pass
