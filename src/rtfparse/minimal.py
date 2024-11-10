#!/usr/bin/env python


"""
A minimal example for a programatic use of the rtf parser and renderer
"""

from pathlib import Path

from rtfparse.parser import Rtf_Parser
from rtfparse.renderers.html_decapsulator import HTML_Decapsulator

source_path = Path(r"D:\trace\Pre-Integration test report of carapp_orureleasenotes_1_22_104 Webapps on ID_S 5_0.rtf")
target_path = Path(r"D:\trace\Pre-Integration test report of carapp_orureleasenotes_1_22_104 Webapps on ID_S 5_0.html")
# Create parent directory of `target_path` if it does not already exist:
target_path.parent.mkdir(parents=True, exist_ok=True)

parser = Rtf_Parser(rtf_path=source_path)
parsed = parser.parse_file()

renderer = HTML_Decapsulator()

with open(target_path, mode="w", encoding="utf-8") as html_file:
    renderer.render(parsed, html_file)
