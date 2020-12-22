#!/usr/bin/env python


from __future__ import annotations
import os
import collections
import logging
# Own modules
from pyrtfparse import utils


# Setup logging
logger = logging.getLogger(__name__)


class Text_Menu:
    """
    Command prompt menu
    """
    def __init__(self, menu_name: str, heading: str) -> None:
        self.menu_name = menu_name
        # not using pyfiglet because pyinstaller package cannot find pyfiglet.fonts
        # self.figlet = pyfiglet.Figlet(font=font) 
        self.heading = heading
    def wait_key(self) -> str:
        """
        Wait for a key press on the console and return it.
        Source: https://stackoverflow.com/a/34956791
        """
        result = None
        if os.name == 'nt':
            import msvcrt
            result = msvcrt.getch()
        else:
            import termios
            fd = sys.stdin.fileno()
            oldterm = termios.tcgetattr(fd)
            newattr = termios.tcgetattr(fd)
            newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, newattr)
            try:
                result = sys.stdin.read(1)
            except IOError:
                pass
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        return str(result, encoding="utf-8").upper()
    def show_heading(self) -> None:
        """
        Renders the Heading of the menu in the logger at INFO level
        """
        # for line in self.figlet.renderText(self.menu_name).split("\n"):
        for line in self.heading.split("\n"):
            logger.info(line)
    def show_options(self, options: collections.OrderedDict) -> None:
        """
        Renders a command prompt menu for each exrtacted traces file.
        Manages key input and acts accordingly
        """
        for key, text in options.items():
            logger.info(f"({key}) {text}")
        logger.info("")
    def show_reason(self, reason: str) -> None:
        logger.warning("\n" + utils.warn(reason + "\n"))
    def choose_from(self, options: collections.OrderedDict) -> str:
        self.show_options(options)
        choice = None
        choices = tuple(key.upper() for key in options.keys())
        logger.debug(f"{choices = }")
        while choice not in choices:
            try:
                if choice == False:
                    logger.debug(f"Empyting wait_key output")
                    _ = self.wait_key()
                    logger.debug(f"choice changing from False to None")
                    choice = None
                    continue
                else:
                    logger.debug(f"{choice = }")
                    logger.debug(f"Waiting for key")
                    choice = self.wait_key()
                    logger.debug(f"{choice = }")
            except UnicodeDecodeError:
                logger.debug("Handling UnicodeDecodeError, changing choice to False")
                choice = False
        return choice


if __name__ == "__main__":
    pass
