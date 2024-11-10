#!/usr/bin/env python


import io
import logging

from rtfparse import entities, utils
from rtfparse.renderers import Renderer

# Setup logging
logger = logging.getLogger(__name__)


class HTML_Decapsulator(Renderer):
    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.ignore_rtf = False
        self.render_word_func = dict(
            (
                ("par", self.newline),
                ("line", self.newline),
                ("tab", self.tab),
                ("fromhtml", self.check_fromhtml),
                ("htmlrtf", self.ignore_rtf_toggle),
            )
        )
        self.ignore_groups = (
            "fonttbl",
            "colortbl",
            "generator",
            "formatConverter",
            "pntext",
            "pntxta",
            "pntxtb",
        )

    def ignore_rtf_toggle(self, cw: entities.Control_Word) -> str:
        if cw.parameter == "" or cw.parameter == 1:
            self.ignore_rtf = True
        elif cw.parameter == 0:
            self.ignore_rtf = False
        return ""

    def check_fromhtml(self, cw: entities.Control_Word) -> str:
        if cw.parameter == 1:
            logger.info(f"This RTF was indeed generated from HTML")
        else:
            logger.warning(utils.warn(f"Encountered a part of RTF which was not generated from HTML"))
            logger.warning(utils.warn(f"This might not be the right renderer for it."))
        return ""

    def newline(self, cw: entities.Control_Word) -> str:
        if self.ignore_rtf:
            return ""
        else:
            return "\n"

    def tab(self, cw: entities.Control_Word) -> str:
        if self.ignore_rtf:
            return ""
        else:
            return "\t"

    def render_symbol(self, item: entities.Control_Symbol, file: io.TextIOWrapper) -> None:
        if not self.ignore_rtf:
            # Obsolete formula character used by Word 5.1 for Macintosh
            if item.text == "|":
                pass
            # Non-breaking space
            elif item.text == "~":
                file.write("\u00a0")
            # Optional hyphen
            elif item.text == "-":
                pass
            # Non-breaking hyphen
            elif item.text == "_":
                file.write("\u2011")
            # Subentry in an index entry
            elif item.text == ":":
                pass
            # Ignorable outside of Group
            elif item.text == "*":
                logger.warning(
                    utils.warn(f"Found an IGNORABLE control symbol which is not a group start!")
                )
            # Probably any symbol converted from a hex code: \'hh
            else:
                file.write(item.text)

    def render(self, parsed: entities.Group, file: io.TextIOWrapper) -> None:
        for item in parsed.structure:
            if isinstance(item, entities.Group):
                if item.name not in self.ignore_groups:
                    self.render(item, file)
            elif isinstance(item, entities.Control_Word):
                try:
                    file.write(self.render_word_func[item.control_name](item))
                except KeyError:
                    pass
            elif isinstance(item, entities.Control_Symbol):
                self.render_symbol(item, file)
            elif isinstance(item, entities.Plain_Text):
                if not self.ignore_rtf:
                    file.write(item.text)
            else:
                pass


if __name__ == "__main__":
    pass
