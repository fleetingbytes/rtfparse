#!/usr/bin/env python


import logging
import pathlib
import io
# Typing
from typing import Union


# Setup logging
logger = logging.getLogger(__name__)


program_name = home_dir_name = "rtfparse"
dir_name = "".join((".", program_name))
configuration_file_name = f"{program_name}_configuration.ini"


def provide_dir(directory: pathlib.Path) -> pathlib.Path:
    """
    Checks if there is a directory of name `dir_name` in the user home path.
    If not, it will try to create one. 
    """
    if directory.exists() and directory.is_dir():
        logger.debug(f"Found directory {str(directory)}")
    else:
        while True:
            try:
                directory.mkdir()
                logger.info(f"Created directory {str(directory)}")
                break
            except FileNotFoundError:
                provide_dir(directory.parent)
                continue
            except FileExistsError:
                logger.debug(f"{directory} already exists")
                break
    return directory


def warn(s: str) -> str:
    """
    Creates a string highlighted as warning in log output
    """
    return " ".join(("◊", s))


def what_is_being_parsed(file: Union[io.BufferedReader, io.BytesIO]) -> str:
    if isinstance(file, io.BufferedReader):
        return file.name
    elif isinstance(file, io.BytesIO):
        return repr(file)
