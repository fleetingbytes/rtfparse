# rtfparse

Parses Microsofts Rich Text Format (RTF) documents. It creates an in-memory object which represents the tree structure of the RTF document. This object can in turn be rendered by using one of the renderers.
So far, rtfparse provides only one renderer (`HTML_Decapsulator`) which liberates the HTML code encapsulated in RTF. This will come handy, for examle, if you ever need to extract the HTML from a HTML-formatted email message saved by Microsoft Outlook.

MS Outlook also tends to use RTF compression, so the CLI of rtfparse can optionally do that, too.

You can of course write your own renderers of parsed RTF documents and consider contributing them to this project.


# Installation

Install rtfparse from your local repository with pip:

    pip install rtfparse

Installation creates an executable file `rtfparse` in your python scripts folder which should be in your `$PATH`.

# Usage From Command Line

Use the `rtfparse` executable from the command line. Read `rtfparse --help`.

rtfparse writes logs into `~/rtfparse/` into these files:

```
rtfparse.debug.log
rtfparse.info.log
rtfparse.errors.log
```

## Example: Decapsulate HTML from an uncompressed RTF file

    rtfparse --rtf-file "path/to/rtf_file.rtf" --decapsulate-html --output-file "path/to/extracted.html"

## Example: Decapsulate HTML from MS Outlook email file

For this, the CLI of rtfparse uses [extract_msg](https://github.com/TeamMsgExtractor/msg-extractor) and [compressed_rtf](https://github.com/delimitry/compressed_rtf).

    rtfparse --msg-file "path/to/email.msg" --decapsulate-html --output-file "path/to/extracted.html"

## Example: Only decompress the RTF from MS Outlook email file

    rtfparse --msg-file "path/to/email.msg" --output-file "path/to/extracted.rtf"

## Example: Decapsulate HTML from MS Outlook email file and save (and later embed) the attachments

When extracting the RTF from the `.msg` file, you can save the attachments (which includes images embedded in the email text) in a directory:

    rtfparse --msg-file "path/to/email.msg" --output-file "path/to/extracted.rtf" --attachments-dir "path/to/dir"

In `rtfparse` version 1.x you will be able to embed these images in the decapsulated HTML. This functionality will be provided by the package [embedimg](https://github.com/fleetingbytes/embedimg).

    rtfparse --msg-file "path/to/email.msg" --output-file "path/to/extracted.rtf" --attachments-dir "path/to/dir" --embed-img

In the current version the option `--embed-img` does nothing.

# Programatic usage in a Python module

## Decapsulate HTML from an uncompressed RTF file

```py
from pathlib import Path
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers.html_decapsulator import HTML_Decapsulator

source_path = Path(r"path/to/your/rtf/document.rtf")
target_path = Path(r"path/to/your/html/decapsulated.html")
# Create parent directory of `target_path` if it does not already exist:
target_path.parent.mkdir(parents=True, exist_ok=True)

parser = Rtf_Parser(rtf_path=source_path)
parsed = parser.parse_file()

renderer = HTML_Decapsulator()

with open(target_path, mode="w", encoding="utf-8") as html_file:
    renderer.render(parsed, html_file)
```

## Decapsulate HTML from an MS Outlook msg file

```py
from pathlib import Path
from extract_msg import openMsg
from compressed_rtf import decompress
from io import BytesIO
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers.html_decapsulator import HTML_Decapsulator


source_file = Path("path/to/your/source.msg")
target_file = Path(r"path/to/your/target.html")
# Create parent directory of `target_path` if it does not already exist:
target_file.parent.mkdir(parents=True, exist_ok=True)

# Get a decompressed RTF bytes buffer from the MS Outlook message
msg = openMsg(source_file)
decompressed_rtf = decompress(msg.compressedRtf)
rtf_buffer = BytesIO(decompressed_rtf)

# Parse the rtf buffer
parser = Rtf_Parser(rtf_file=rtf_buffer)
parsed = parser.parse_file()

# Decapsulate the HTML from the parsed RTF
decapsulator = HTML_Decapsulator()
with open(target_file, mode="w", encoding="utf-8") as html_file:
    decapsulator.render(parsed, html_file)
```

# RTF Specification Links

If you find a working official Microsoft link to the RTF specification and add it here, you'll be remembered fondly.

* [Webarchive Link to RTF Spec 1.9.1](https://web.archive.org/web/20190708132914/http://www.kleinlercher.at/tools/Windows_Protocols/Word2007RTFSpec9.pdf)
* [RTF Extensions, MS-OXRTFEX](https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxrtfex/411d0d58-49f7-496c-b8c3-5859b045f6cf)
