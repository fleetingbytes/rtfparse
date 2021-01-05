#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK


import pathlib
import logging
import logging.config
import argparse
import argcomplete
from argcomplete.completers import EnvironCompleter as EC
from itertools import filterfalse
import io
import extract_msg as em
import compressed_rtf as cr
# Own modules
from rtfparse import logging_conf
from rtfparse import errors
from rtfparse import utils
from rtfparse import config_loader
from rtfparse import version
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers import de_encapsulate_html


# Setup logging
def setup_logging_directory(directory: pathlib.Path) -> tuple[logging.Logger, pathlib.Path]:
    """
    Returns a logger and a path to directory where the logs are saved
    """
    try:
        path_to_dir = utils.provide_dir(directory)
        logger_config = logging_conf.create_dict_config(path_to_dir, "debug.log", "info.log", "errors.log")
    except FileExistsError:
        logger.error(f"Failed to create the directory `{str(path_to_dir)}` because it already exists as a file.")
        logger.error(f"Please create the directory `{str(path_to_dir)}`")
    finally:
        logging.config.dictConfig(logger_config)
        logger = logging.getLogger(__name__)
    return logger, path_to_dir


logger, path_to_dir = setup_logging_directory(pathlib.Path.home() / utils.dir_name)


def argument_parser() -> argparse.ArgumentParser:
    """
    Creates an argument parser for command line arguments
    """
    parser = argparse.ArgumentParser(description="RTF parser")
    parser.add_argument("-v", "--version", action="store_true", help="print out rtfparse version and exit").completer = EC
    parser.add_argument("--autoconfig", action="store_true", help="Configure rtfparse automatically").completer = EC
    parser.add_argument("-f", "--file", action="store", metavar="PATH", type=pathlib.Path, help="path to the rtf file").completer = EC
    parser.add_argument("-m", "--msg", action="store", metavar="PATH", type=pathlib.Path, help="Parse RTF from MS Outlook's .msg file").completer = EC
    parser.add_argument("-d", "--de-encapsulate-html", action="store_true", help="De-encapsulate HTML from RTF").completer = EC
    return parser


def de_encapsulate(rp: Rtf_Parser, target_file: pathlib.Path) -> None:
    renderer = de_encapsulate_html.De_encapsulate_HTML()
    with open(target_file, mode="w", encoding="utf-8") as htmlfile:
        logger.info(f"Rendering the encapsulated HTML")
        renderer.render(rp.parsed, htmlfile)
        logger.info(f"Encapsulated HTML rendered")


def run(config: config_loader.Config) -> None:
    if config.cli_args.file and config.cli_args.file.exists():
        file_name = config.cli_args.file.name
        with open(config.cli_args.file, mode="rb") as rtf_file:
            rp = Rtf_Parser(rtf_file=rtf_file)
            rp.parse_file()
    elif config.cli_args.msg:
        file_name = config.cli_args.msg.name
        msg = em.openMsg(f"{config.cli_args.msg}")
        for attachment in msg.attachments:
            with open(config.html / f"{attachment.longFilename}", mode="wb") as att_file:
                att_file.write(attachment.data)
        decompressed_rtf = cr.decompress(msg.compressedRtf)
        with open((config.email_rtf / config.cli_args.msg.name).with_suffix(".rtf"), mode="wb") as email_rtf:
            email_rtf.write(decompressed_rtf)
        with io.BytesIO(decompressed_rtf) as rtf_file:
            rp = Rtf_Parser(rtf_file=rtf_file)
            rp.parse_file()
    if config.cli_args.de_encapsulate_html:
        de_encapsulate(rp, (config.html / file_name).with_suffix(".html"))


def cli_start(version) -> None:
    """
    Entry point for any component start from the commmand line
    """
    logger.debug(f"{utils.program_name} started")
    parser = argument_parser()
    argcomplete.autocomplete(parser)
    cli_args = parser.parse_args()
    logger.debug(f"Parsed arguments: {cli_args}")
    path_to_config = path_to_dir / utils.configuration_file_name
    try:
        if cli_args.version:
            logger.info(f"{version}")
        else:
            with config_loader.Config(path_to_config, cli_args.autoconfig) as config:
                config.cli_args = cli_args
                run(config)
    except errors.WrongConfiguration as err:
        logger.error(err.message)
    except Exception as err:
        logger.exception(f"Uncaught exception {repr(err)} occurred.")
    logger.debug(f"{utils.program_name} ended")


if __name__ == "__main__":
    pass
