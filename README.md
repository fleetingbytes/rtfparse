# rtfparse

RTF Parser. So far it can only de-encapsulate HTML content from an RTF, but it properly parses the RTF structure and allows you to write your own custom RTF renderers. The HTML de-encapsulator provided with `rtfparse` is just one such custom renderer which liberates the HTML content from its RTF encapsulation and saves it in a given html file.

rtfparse can also decompressed RTF from MS Outlook `.msg` files and parse that.

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

## Example: De-encapsulate HTML from an uncompressed RTF file

    rtfparse --rtf-file "path/to/rtf_file.rtf" --de-encapsulate-html --output-file "path/to/extracted.html"

## Example: De-encapsulate HTML from MS Outlook email file

Thanks to [extract_msg](https://github.com/TeamMsgExtractor/msg-extractor) and [compressed_rtf](https://github.com/delimitry/compressed_rtf), rtfparse internally uses them:

    rtfparse --msg-file "path/to/email.msg" --de-encapsulate-html --output-file "path/to/extracted.html"

## Example: Only decompress the RTF from MS Outlook email file

    rtfparse --msg-file "path/to/email.msg" --output-file "path/to/extracted.rtf"

## Example: De-encapsulate HTML from MS Outlook email file and save (and later embed) the attachments

When extracting the RTF from the `.msg` file, you can save the attachments (which includes images embedded in the email text) in a directory:

    rtfparse --msg-file "path/to/email.msg" --output-file "path/to/extracted.rtf" --attachments-dir "path/to/dir"

In `rtfparse` version 1.x you will be able to embed these images in the de-encapsulated HTML. This functionality will be provided by the package [embedimg](https://github.com/fleetingbytes/embedimg).

    rtfparse --msg-file "path/to/email.msg" --output-file "path/to/extracted.rtf" --attachments-dir "path/to/dir" --embed-img

In the current version the option `--embed-img` does nothing.

# Programatic usage in python module

```
from pathlib import Path
from rtfparse.parser import Rtf_Parser
from rtfparse.renderers.de_encapsulate_html import De_encapsulate_HTML

source_path = Path(r"path/to/your/rtf/document.rtf")
target_path = Path(r"path/to/your/html/de_encapsulated.html")
# Create parent directory of `target_path` if it does not already exist:
target_path.parent.mkdir(parents=True, exist_ok=True)


parser = Rtf_Parser(rtf_path=source_path)
parsed = parser.parse_file()

renderer = De_encapsulate_HTML()

with open(target_path, mode="w", encoding="utf-8") as html_file:
    renderer.render(parsed, html_file)
```

# RTF Specification Links

If you find a working official Microsoft link to the RTF specification and add it here, you'll be remembered fondly.

* [Swissmains Link to RTF Spec 1.9.1](https://manuals.swissmains.com/pages/viewpage.action?pageId=1376332&preview=%2F1376332%2F10620104%2FWord2007RTFSpec9.pdf)
* [Webarchive Link to RTF Spec 1.9.1](https://web.archive.org/web/20190708132914/http://www.kleinlercher.at/tools/Windows_Protocols/Word2007RTFSpec9.pdf)
* [RTF Extensions, MS-OXRTFEX](https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxrtfex/411d0d58-49f7-496c-b8c3-5859b045f6cf)
