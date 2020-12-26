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


def not_followed_by(preceding: bytes, actual: bytes) -> bytes:
    return rb"(?<!" + preceding + rb")" + actual


def no_capture(content: bytes) -> bytes:
    return rb"(?:" + content + rb")"


# Raw regular expression "strings"" (actually byte strings)


_control_characters = rb"\\\{\}"
_newline = b"\\" + rb"r" + b"\\" + rb"n"
control_character = group(_control_characters)
not_control_character = group(rb"^" + _control_characters)
_control_characters_or_newline = _control_characters + _newline
control_character_or_newline = group(_control_characters + _newline)
not_control_character_or_newline = group(rb"^" + _control_characters_or_newline)
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
parameter_pattern = named_regex_group("parameter", minus + digit + rb"{1,10}")
space = named_regex_group("space", rb" ")
other = named_regex_group("other", group(rb"^" + _letters + _digits))


ascii_letter_sequence = named_regex_group("control_name", ascii_letters)
delimiter = named_regex_group("delimiter", rb"|".join((space, parameter_pattern, other, rb"$")))
symbol = named_regex_group("symbol", other)
control_word_pattern = named_regex_group("control_word", rtf_backslash + ascii_letter_sequence + delimiter)
pcdata_delimiter = no_capture(rb"|".join((rtf_brace_open, rtf_brace_close, control_word_pattern)))
plain_text_pattern = named_regex_group("text", not_control_character_or_newline + rb"+") + no_capture(rb"|".join((control_character_or_newline, rb"$")))
probe_pattern = rb".."


class Bytes_Regex():
    def __init__(self, Bytes: bytes, flags:re.RegexFlag=0) -> None:
        self.pattern_bytes = Bytes
        self.pattern = re.compile(Bytes, flags)
        self.match = self.pattern.match
    def regex101(self) -> None:
        print(self.pattern_bytes.decode("ascii"))


meaningful_bs = Bytes_Regex(rtf_backslash)
probe = Bytes_Regex(named_regex_group("probe", probe_pattern), flags=re.DOTALL)
parameter = Bytes_Regex(parameter_pattern)
control_word = Bytes_Regex(control_word_pattern)
control_symbol = Bytes_Regex(rtf_backslash + symbol)
group_start = Bytes_Regex(rtf_brace_open)
group_end = Bytes_Regex(rtf_brace_close)
plain_text = Bytes_Regex(plain_text_pattern)


raw_pcdata = Bytes_Regex(named_regex_group("pcdata", rb".*?") + pcdata_delimiter, flags=re.DOTALL)
raw_sdata = Bytes_Regex(named_regex_group("sdata", group(_hdigits + rb"\r\n") + rb"+"), flags=re.DOTALL)
