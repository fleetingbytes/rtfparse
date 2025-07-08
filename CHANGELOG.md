# Changelog

<!-- towncrier release notes start -->

## 0.9.5 (2025-07-08)


### Documentation

- add MIT header to LICENSE.txt [#46](https://github.com/fleetingbytes/rtfparse/issues/46)
- use MIT SPDX identifier in pyproject.toml, use correct name in LICENSE.txt, update year in LICENSE.txt, rename LICENSE.txt to LICENSE [#47](https://github.com/fleetingbytes/rtfparse/issues/47)

## 0.9.4 (2024-11-10)


### Bugfixes

- add missing import statement in `html_decapsulator.py` [#42](https://github.com/fleetingbytes/rtfparse/issues/42)


### Development Details

- replace `black` and `isort` with `ruff` [#44](https://github.com/fleetingbytes/rtfparse/issues/44)

## 0.9.3 (2024-11-01)


### Bugfixes

- Fixed double numbering of ordered and unordered lists [#38](https://github.com/fleetingbytes/rtfparse/issues/38)

## 0.9.2 (2024-09-30)


### Bugfixes

- Fixed `rtfparse --help`, correct entrypoint in `pyproject.toml` [#34](https://github.com/fleetingbytes/rtfparse/issues/34)

## 0.9.1 (2024-06-21)


### Documentation

- Fix old naming in readme [#22](https://github.com/fleetingbytes/rtfparse/issues/22)
- Add example how to programmatically extract HTML from MS Outlook message [#25](https://github.com/fleetingbytes/rtfparse/issues/25)


### Bugfixes

- Don't setup log if not using the CLI [#24](https://github.com/fleetingbytes/rtfparse/issues/24)
- Fix possible bug in error handling [#26](https://github.com/fleetingbytes/rtfparse/issues/26)

## 0.9.0 (2024-03-11)


### Bugfixes

- Recognize control words with where the parameter's digital sequence is delimited by any character other than an ASCII digit [#18](https://github.com/fleetingbytes/rtfparse/issues/18)


### Development Details

- Renamed a few things, improved readme [#17](https://github.com/fleetingbytes/rtfparse/issues/17)

## 0.8.2 (2024-03-05)


### Documentation

- Update `README.md`: Create parent directories of `target_path` if they don't already exist. [#14](https://github.com/fleetingbytes/rtfparse/issues/14)

## 0.8.1 (2023-08-07)


### Bugfixes

- Interpret ANSI encoding as CP1252, improve error handling [#11](https://github.com/fleetingbytes/rtfparse/issues/11)


## 0.8.0 (2023-06-29)


### Bugfixes

- Using `pyproject.toml` for installation with current pip versions [#1](https://github.com/fleetingbytes/rtfparse/issues/1)


### Development Details

- Fixed reference before assignment error [#3](https://github.com/fleetingbytes/rtfparse/issues/3)
- Removed convoluted configurator [#5](https://github.com/fleetingbytes/rtfparse/issues/5)
