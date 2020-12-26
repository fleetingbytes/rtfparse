#!/usr/bin/env python


import pathlib


class Error(Exception):
    """
    Base class for rtfparser-specific errors
    """
    def __init__(self, message: str=""):
        self.message = message


class WrongConfiguration(Error):
    def __init__(self, message, payload):
        self.message = message
        self.payload = payload


class UnexpectedEndOfFileError(Error):
    pass
