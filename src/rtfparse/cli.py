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
from rtfparse.renderers import Renderer
from rtfparse.renderers.html_decapsulator import HTML_Decapsulator
from rtfparse.renderers.rtf_decapsulator import Rtf_Decapsulator


def setup_logger(directory: Path) -> logging.Logger:
    """
    Returns a logger and a path to directory where the logs are saved
    """
    try:
        provide_dir(directory)
        logger_config = logging_conf.create_dict_config(directory, "rtfparse.debug.log", "rtfparse.info.log", "rtfparse.errors.log")
    except FileExistsError:
        print(f"Failed to create the directory `{str(directory)}` because it already exists as a file.")
        print(f"Please create the directory `{str(directory)}`")
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
    parser.add_argument("-v", "--version", action="version", version=" ".join(("%(prog)s", __version__)), help="print out rtfparse version and exit")
    parser.add_argument("-r", "--rtf-file", action="store", metavar="PATH", type=Path, help="path to the rtf file")
    parser.add_argument("-m", "--msg-file", action="store", metavar="PATH", type=Path, help="Parse RTF from MS Outlook's .msg file")
    parser.add_argument("-d", "--decapsulate-html", action="store_true", help="Decapsulate HTML from RTF")
    parser.add_argument("-i", "--embed-img", action="store_true", help="Embed images from email to HTML")
    parser.add_argument("-o", "--output-file", metavar="PATH", type=Path, help="path to the desired output file")
    parser.add_argument("-a", "--attachments-dir", metavar="PATH", type=Path, help="path to directory where to save email attachments")
    parser.add_argument("-R", "--decapsulate-rtf", action="store_true", help="Render RTF")
    return parser


def decapsulate(rp: Rtf_Parser, target_file: Path, renderer: Renderer) -> None:
    with open(target_file, mode="w", encoding="utf-8") as htmlfile:
        logger.info(f"Rendering using {renderer.__class__.__name__}")
        renderer.render(rp.parsed, htmlfile)
        logger.info(f"Rendering finished, saved to {target_file}")


def run(cli_args: Namespace) -> None:
    if cli_args.rtf_file and cli_args.rtf_file.exists():
        with open(cli_args.rtf_file, mode="rb") as rtf_file:
            rp = Rtf_Parser(rtf_file=rtf_file)
            rp.parse_file()
    elif cli_args.msg_file:
        msg = em.openMsg(f"{cli_args.msg_file}")
        if cli_args.attachments_dir:
            provide_dir(cli_args.attachments_dir)
            for attachment in msg.attachments:
                with open(cli_args.attachments_dir / f"{attachment.longFilename}", mode="wb") as att_file:
                    att_file.write(attachment.data)
        decompressed_rtf = cr.decompress(msg.compressedRtf)
        with open(cli_args.msg_file.with_suffix(".rtf"), mode="wb") as email_rtf:
            email_rtf.write(decompressed_rtf)
        with io.BytesIO(decompressed_rtf) as rtf_file:
            rp = Rtf_Parser(rtf_file=rtf_file)
            rp.parse_file()
    if cli_args.decapsulate_html and cli_args.output_file:
        decapsulate(rp, cli_args.output_file.with_suffix(".html"), HTML_Decapsulator())
    if cli_args.decapsulate_rtf and cli_args.output_file:
        decapsulate(rp, cli_args.output_file.with_suffix(".rtf"), Rtf_Decapsulator())


def main() -> None:
    """
    Entry point for any component start from the commmand line
    """
    logger.debug("rtfparse started")
    parser = argument_parser()
    argcomplete.autocomplete(parser)
    cli_args = parser.parse_args()
    logger.debug(f"Parsed arguments: {cli_args}")
    try:
        run(cli_args)
    except Exception as err:
        logger.exception(f"Uncaught exception {repr(err)} occurred.")
    logger.debug("rtfparse ended")


if __name__ == "__main__":
    main()