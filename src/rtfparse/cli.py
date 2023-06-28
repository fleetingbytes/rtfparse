#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import io
import logging
import logging.config
from argparse import ArgumentParser, Namespace
from pathlib import Path

import argcomplete
import compressed_rtf as cr
import extract_msg as em
from provide_dir import provide_dir

from rtfparse import logging_conf
from rtfparse.__about__ import __version__
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers import de_encapsulate_html


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


def argument_parser() -> ArgumentParser:
    """
    Creates an argument parser for command line arguments
    """
    parser = ArgumentParser(description="RTF parser", prog="rtfparse")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=" ".join(("%(prog)s", __version__)),
        help="print out rtfparse version and exit",
    )
    parser.add_argument(
        "-r", "--rtf-file", action="store", metavar="PATH", type=Path, help="path to the rtf file"
    )
    parser.add_argument(
        "-m",
        "--msg-file",
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
    parser.add_argument(
        "-o", "--output-file", metavar="PATH", type=Path, help="path to the desired output file"
    )
    parser.add_argument(
        "-a",
        "--attachments-dir",
        metavar="PATH",
        type=Path,
        help="path to directory where to save email attachments",
    )
    return parser


def de_encapsulate(rp: Rtf_Parser, target_file: Path) -> None:
    renderer = de_encapsulate_html.De_encapsulate_HTML()
    with open(target_file, mode="w", encoding="utf-8") as htmlfile:
        logger.info(f"Rendering the encapsulated HTML")
        renderer.render(rp.parsed, htmlfile)
        logger.info(f"Encapsulated HTML rendered")


def run(cli_args: Namespace) -> None:
    if cli_args.rtf_file and cli_args.rtf_file.exists():
        with open(cli_args.rtf_file, mode="rb") as rtf_file:
            rp = Rtf_Parser(rtf_file=rtf_file)
            rp.parse_file()
    elif cli_args.msg_file:
        msg = em.openMsg(f"{cli_args.msg_file}")
        if cli_args.attachments_dir:
            for attachment in msg.attachments:
                with open(
                    cli_args.attachments_dir / f"{attachment.longFilename}", mode="wb"
                ) as att_file:
                    att_file.write(attachment.data)
        decompressed_rtf = cr.decompress(msg.compressedRtf)
        with open(cli_args.msg_file.with_suffix(".rtf"), mode="wb") as email_rtf:
            email_rtf.write(decompressed_rtf)
        with io.BytesIO(decompressed_rtf) as rtf_file:
            rp = Rtf_Parser(rtf_file=rtf_file)
            rp.parse_file()
    if cli_args.de_encapsulate_html and cli_args.output_file:
        de_encapsulate(rp, cli_args.output_file.with_suffix(".html"))


def main() -> None:
    """
    Entry point for any component start from the commmand line
    """
    logger.debug(f"rtfparse started")
    parser = argument_parser()
    argcomplete.autocomplete(parser)
    cli_args = parser.parse_args()
    logger.debug(f"Parsed arguments: {cli_args}")
    try:
        run(cli_args)
    except Exception as err:
        logger.exception(f"Uncaught exception {repr(err)} occurred.")
    logger.debug(f"rtfparse ended")
