#!/usr/bin/env python


import pathlib
from rtfparse.parsers import Rtf_Parser
from rtfparse.renderers import encapsulated_html


parser = Rtf_Parser()
renderer = encapsulated_html.Encapsulated_HTML()
source_file = pathlib.Path(r"D:\trace\email\test_mail_sw_release.rtf")
target_file = pathlib.Path(r"D:\trace\email\extracted_with_rtfparse.html")


with open(source_file, mode="rb") as rtf_file:
    parser.parse_file(rtf_file, default_encoding="cp1252")
    with open(target_file, mode="w", encoding="utf-8") as html_file:
        renderer.render(parser.parsed, target_file)
