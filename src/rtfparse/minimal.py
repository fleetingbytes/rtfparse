#!/usr/bin/env python


"""
A minimal example for a programatic use of the rtf parser and renderer
"""

from pathlib import Path
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers.de_encapsulate_html import De_encapsulate_HTML

source_path = Path(r"path/to/your/rtf/document.rtf")
target_path = Path(r"path/to/your/html/de_encapsulated.html")


parser = Rtf_Parser(rtf_path=source_path)
parsed = parser.parse_file()

renderer = De_encapsulate_HTML()

with open(target_path, mode="w", encoding="utf-8") as html_file:
    renderer.render(parsed, html_file)
