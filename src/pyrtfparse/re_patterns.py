#!/usr/bin/env python


import re


# Helper functions to construct raw regular expressions "strings" (actually byte strings)


def group(content: bytes) -> bytes:
    return rb"[" + content + rb"]"


def named_regex_group(name: str, content: bytes) -> bytes:
    group_start = rb"(?P<" + name.encode("ascii") + rb">"
    group_end = rb")"
    return rb"".join((group_start, content, group_end))


def not_preceded_by(preceding: bytes, actual: bytes) -> bytes:
    return rb"(?<!" + preceding + rb")" + actual


def no_capture(content: bytes) -> bytes:
    return rb"(?:" + content + rb")"


# Raw regular expression "strings"" (actually byte strings)


rtf_backslash = named_regex_group("backslash", not_preceded_by(rb"\\", rb"\\"))
unnamed_rtf_backslash = not_preceded_by(rb"\\", rb"\\")
_letters = rb"a-zA-Z"
ascii_letters = group(_letters) + rb"{1,32}"
_digits = rb"0-9"
_hdigits = rb"0-9a-f"
ignorable = named_regex_group("ignorable", rb"\\\*")
rtf_brace_open = named_regex_group("group_start", not_preceded_by(unnamed_rtf_backslash, rb"\{") + ignorable + rb"?")
rtf_brace_close = named_regex_group("group_end", not_preceded_by(unnamed_rtf_backslash, rb"\}"))


digit = named_regex_group("digit", group(_digits))
hdigit = named_regex_group("hdigit", group(_hdigits))
minus = named_regex_group("minus", rb"-?")
# int16 = minus + digit + rb"{1,5}"
parameter = named_regex_group("param", minus + digit + rb"{1,10}")
space = named_regex_group("space", rb" ")
other = named_regex_group("other", group(rb"^" + _letters + _digits))


ascii_letter_sequence = named_regex_group("control_name", ascii_letters)
delimiter = named_regex_group("delimiter", rb"|".join((rb" ", parameter, other)))
symbol = named_regex_group("symbol", other)
control_word_pattern = named_regex_group("control_word", rtf_backslash + ascii_letter_sequence + delimiter)
pcdata_delimiter = no_capture(rb"|".join((rtf_brace_open, rtf_brace_close, control_word_pattern)))


class Bytes_Regex():
    def __init__(self, Bytes: bytes, flags:re.RegexFlag=0) -> None:
        self.pattern_bytes = Bytes
        self.pattern = re.compile(Bytes, flags)
        self.match = self.pattern.match
    def regex101(self) -> None:
        print(self.pattern_bytes.decode("ascii"))


meaningful_bs = Bytes_Regex(rtf_backslash)
# control_word = Bytes_Regex(rtf_backslash + ascii_letter_sequence + delimiter)
control_word = Bytes_Regex(control_word_pattern)
control_symbol = Bytes_Regex(rtf_backslash + symbol)
group_start = Bytes_Regex(rtf_brace_open)
group_end = Bytes_Regex(rtf_brace_close)


raw_pcdata = Bytes_Regex(named_regex_group("pcdata", rb".*?") + pcdata_delimiter, flags=re.DOTALL)
raw_sdata = Bytes_Regex(named_regex_group("sdata", group(_hdigits + rb"\r\n") + rb"+"), flags=re.DOTALL)
