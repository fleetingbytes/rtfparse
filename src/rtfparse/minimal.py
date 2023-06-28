#!/usr/bin/env python


import pathlib

from rtfparse.parser import Rtf_Parser
from rtfparse.renderers import de_encapsulate_html

source_path = pathlib.Path(r"path/to/your/rtf/document.rtf")
target_path = pathlib.Path(r"path/to/your/html/de_encapsulated.html")


parser = Rtf_Parser(rtf_path=source_path)
parsed = parser.parse_file()

renderer = de_encapsulate_html.De_encapsulate_HTML()
with open(target_path, mode="w", encoding="utf-8") as html_file:
    renderer.render(parsed, html_file)
