#!/usr/bin/env python


import io
import re
import logging
# Own modules
from rtfparse import re_patterns
from rtfparse import entities
from rtfparse import errors
from rtfparse import utils
# Typing
from typing import Union
from rtfparse import config_loader


# Setup logging
logger = logging.getLogger(__name__)


class Rtf_Parser:
    def __init__(self) -> None:
        self.parsed = None
    def parse_file(self, config: config_loader.Config, file: Union[io.BufferedReader, io.BytesIO]) -> None:
        parsed_object = utils.what_is_being_parsed(file)
        logger.info(f"Parsing the structure of {parsed_object}")
        try:
            self.parsed = entities.Group(config, file)
        except errors.UnexpectedEndOfFileError as err:
            logger.error(f"{err}")
        except Exception as err:
            logger.exception(err)
        finally:
            logger.info(f"Structure of {parsed_object} parsed")


if __name__ == "__main__":
    pass
