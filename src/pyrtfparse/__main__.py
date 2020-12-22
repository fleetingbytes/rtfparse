#!/usr/bin/env python


import sys
from pyrtfparse import version
from pyrtfparse import entry


def pyrtfparse():
    sys.exit(entry.cli_start(version.version))


if __name__ == "__main__":
    pyrtfparse()
