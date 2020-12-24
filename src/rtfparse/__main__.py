#!/usr/bin/env python


import sys
from rtfparse import version
from rtfparse import entry


def main():
    sys.exit(entry.cli_start(version.version))


if __name__ == "__main__":
    main()
