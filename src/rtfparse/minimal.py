#!/usr/bin/env python


import pathlib
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers import de_encapsulate_html


source_path = pathlib.Path(r"D:\trace\email\test_mail_sw_release.rtf")
target_path = pathlib.Path(r"D:\trace\email\extracted_with_rtfparse.html")


parser = Rtf_Parser(rtf_path=source_path)
parsed = parser.parse_file()

renderer = de_encapsulate_html.De_encapsulate_HTML()
with open(target_path, mode="w", encoding="utf-8") as html_file:
    renderer.render(parsed, html_file)
