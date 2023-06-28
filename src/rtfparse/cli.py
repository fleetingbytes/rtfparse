#!/usr/bin/env python

import logging
import logging.config
from pathlib import Path
from provide_dir import provide_dir
from rtfparse import logging_conf


def setup_logger(directory: Path) -> logging.Logger:
    """
    Returns a logger and a path to directory where the logs are saved
    """
    try:
        provide_dir(directory)
        logger_config = logging_conf.create_dict_config(
            directory, "debug.log", "info.log", "errors.log"
        )
    except FileExistsError:
        logger.error(
            f"Failed to create the directory `{str(directory)}` because it already exists as a file."
        )
        logger.error(f"Please create the directory `{str(directory)}`")
    finally:
        logging.config.dictConfig(logger_config)
        logger = logging.getLogger(__name__)
    return logger


logger = setup_logger(Path.home() / "rtfparse")


def argument_parser() -> argparse.ArgumentParser:
    """
    Creates an argument parser for command line arguments
    """
    parser = argparse.ArgumentParser(description="RTF parser")
    parser.add_argument(
        "-v", "--version", action="store_true", help="print out rtfparse version and exit"
    )
    parser.add_argument("--autoconfig", action="store_true", help="Configure rtfparse automatically")
    parser.add_argument(
        "-f", "--file", action="store", metavar="PATH", type=Path, help="path to the rtf file"
    )
    parser.add_argument(
        "-m",
        "--msg",
        action="store",
        metavar="PATH",
        type=Path,
        help="Parse RTF from MS Outlook's .msg file",
    )
    parser.add_argument(
        "-d", "--de-encapsulate-html", action="store_true", help="De-encapsulate HTML from RTF"
    )
    parser.add_argument(
        "-i", "--embed-img", action="store_true", help="Embed images from email to HTML"
    )
    return parser


def run(cli_args: argparse.Namespace) -> None:
    logger.info("Program runs")


def main(version) -> None:
    """
    Entry point for any component start from the commmand line
    """
    logger.debug(f"{utils.program_name} started")
    parser = argument_parser()
    argcomplete.autocomplete(parser)
    cli_args = parser.parse_args()
    logger.debug(f"Parsed arguments: {cli_args}")
    try:
        run(cli_args)
    except Exception as err:
        logger.exception(f"Uncaught exception {repr(err)} occurred.")
    logger.debug(f"{utils.program_name} ended")
