#!/usr/bin/env python


import re

# Helper functions to construct raw regular expressions "strings" (actually byte strings)


def group(content: bytes) -> bytes:
    if content:
        return rb"[" + content + rb"]"
    else:
        return b""


def named_regex_group(name: str, content: bytes) -> bytes:
    group_start = rb"(?P<" + name.encode("ascii") + rb">"
    group_end = rb")"
    return rb"".join((group_start, content, group_end))


def preceded_by(preceding: bytes, actual: bytes) -> bytes:
    return rb"(?<=" + preceding + rb")" + actual

def not_preceded_by(preceding: bytes, actual: bytes) -> bytes:
    return rb"(?<!" + preceding + rb")" + actual

def followed_by(following: bytes, actual: bytes) -> bytes:
    return actual + rb"(?=" + following + rb")"

def not_followed_by(following: bytes, actual: bytes) -> bytes:
    return actual + rb"(?!" + following + rb")"

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
ascii_letters = group(_letters + b"~") + rb"{1,32}"
_digits = rb"0-9"
_hdigits = rb"0-9a-f"
ignorable = named_regex_group("ignorable", rb"\\\*")
rtf_brace_open = named_regex_group("group_start", not_preceded_by(unnamed_rtf_backslash, rb"\{") + ignorable + rb"?")
rtf_brace_close = named_regex_group("group_end", not_preceded_by(unnamed_rtf_backslash, rb"\}")) + named_regex_group("group_tail", rb'\s*')


minus = named_regex_group("minus", rb"-?")
digit = named_regex_group("digit", minus + group(_digits) + rb"{1,10}")
hdigit = named_regex_group("hdigit", group(_hdigits))
parameter_pattern = named_regex_group("parameter", digit)
space = named_regex_group("space", rb" ")
newline = named_regex_group("newline", _newline)
other = named_regex_group("other", group(rb"^" + _letters + _digits))
nothing = named_regex_group("nothing", group(rb""))


ascii_letter_sequence = named_regex_group("control_name", ascii_letters + parameter_pattern + rb"?")
delimiter = named_regex_group("delimiter", rb"|".join((named_regex_group("other", group(rb"^" + _letters + _digits + rb"\s*;")), nothing, rb"$"))) + named_regex_group("delimiter_tail", rb"[\s;]*")
symbol = named_regex_group("symbol", other)
optional_asterisk = named_regex_group("optional_asterisk", rb"(\\\*)?")
control_word_pattern = named_regex_group("control_word", optional_asterisk + rtf_backslash + ascii_letter_sequence + delimiter)
pcdata_delimiter = no_capture(rb"|".join((rtf_brace_open, rtf_brace_close, control_word_pattern)))
plain_text_pattern = named_regex_group("text", not_control_character_or_newline + rb"+") + no_capture(
    rb"|".join((control_character_or_newline, rb"$"))
)
probe_pattern = rb".."


class Bytes_Regex:
    """
    This wraps `re.pattern` objects and gives them a method `regex101` which
    prints out the pattern in such a manner that it can be copy-pasted
    to regex101.com.
    """

    def __init__(self, Bytes: bytes, flags: re.RegexFlag = 0) -> None:
        self.pattern_bytes = Bytes
        self.pattern = re.compile(Bytes, flags)
        self.match = self.pattern.match

    def regex101(self) -> None:
        print(self.pattern_bytes.decode("ascii"))


meaningful_bs = Bytes_Regex(rtf_backslash)
probe = Bytes_Regex(named_regex_group("probe", probe_pattern), flags=re.DOTALL)
parameter = Bytes_Regex(parameter_pattern)
control_word = Bytes_Regex(control_word_pattern)
control_symbol = Bytes_Regex(optional_asterisk + rtf_backslash + symbol)
group_start = Bytes_Regex(rtf_brace_open)
group_end = Bytes_Regex(rtf_brace_close)
plain_text = Bytes_Regex(plain_text_pattern)


raw_pcdata = Bytes_Regex(named_regex_group("pcdata", rb".*?") + pcdata_delimiter, flags=re.DOTALL)
raw_sdata = Bytes_Regex(named_regex_group("sdata", group(_hdigits + rb"\r\n") + rb"+"), flags=re.DOTALL)
