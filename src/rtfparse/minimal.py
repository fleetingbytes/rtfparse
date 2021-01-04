#!/usr/bin/env python


import pathlib
from rtfparse.parsers import Rtf_Parser
from rtfparse.renderers import encapsulated_html


source_file = pathlib.Path(r"D:\trace\email\test_mail_sw_release.rtf")
target_file = pathlib.Path(r"D:\trace\email\extracted_with_rtfparse.html")


parser = Rtf_Parser(rtf_file=source_file)
parsed = parser.parse_file()

renderer = encapsulated_html.Encapsulated_HTML()
renderer.render(rtf_structure=parsed, target_file=target_file)
