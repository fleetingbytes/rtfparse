#!/usr/bin/env python


import io
import logging
from rtfparse import re_patterns


# Setup logging
logger = logging.getLogger(__name__)


class Destination_Group:
    def __init__(self, file: io.BufferedReader) -> None:
        logger.debug(f"Creating destination group from {file.name}")


if __name__ == "__main__":
    pass
