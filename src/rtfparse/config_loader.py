#!/usr/bin/env python


import pathlib
import configparser
import logging
import sys
import traceback
import re
import dataclasses
import urllib.parse
from collections import OrderedDict
# Own modules
from rtfparse import errors
from rtfparse import utils
from rtfparse import menu


# setup logging
logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Preconfigured_Path():
    internal_name: str
    path: dataclasses.InitVar[pathlib.Path]
    comment: str
    def __post_init__(self, path) -> None:
        self.path = pathlib.Path(path)


class Config():
    """
    Holds all confituration data readily available as attributes
    """
    def __init__(self, cfg_path: pathlib.Path, autoconfig: bool) -> None:
        self.error_regex = re.compile(r"""config_parser\.get.*\(["'](?P<section>\w+)["'], *["'](?P<variable>\w+)["']\)""")
        self.path_to_config_file = cfg_path
        self.path_to_home = utils.provide_dir(self.path_to_config_file.parent)
        self.path_to_pyrtfparse_home = pathlib.Path.home() / utils.home_dir_name
        self._subdir_dir = Preconfigured_Path(
                internal_name="subdir_dir",
                path=self.path_to_pyrtfparse_home / "subdir",
                comment="some subdir",
            )
        self._wizard_has_run = False
        self.autoconfig = autoconfig
        self.read_config_file()
        self.check_paths = (self._subdir_dir,
                           )
        self.integrity_check()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Deleting config during development. Comment after release.
        # self.delete_config_file()
        pass
    def reset_parser(self) -> None:
        self.config_parser = configparser.ConfigParser(allow_no_value=True)
        self.config_parser.optionxform = str
    def read_config_file(self) -> None:
        """
        Reads current configuration file or creates a new one with a default configuration
        """
        self.reset_parser()
        try:
            self.config_parser.read_file(open(self.path_to_config_file))
            self.parse()
            logger.debug(f"{self.path_to_config_file.name} read")
        except FileNotFoundError:
            logger.info("Config file missing, creating new default config file")
            self.create_config_file()
    def integrity_check(self) -> None:
        try:
            for preconf_path in self.check_paths:
                path_to_check = preconf_path.path
                assert path_to_check.exists()
        except AssertionError as e:
            logger.debug(f"Path not found, starting wizard")
            self.wizard(errors.WrongConfiguration(f"{self.path_to_config_file.name}: '{str(path_to_check)}', path does not exist!", preconf_path), autoconfig=self.autoconfig)
    def create_config_file(self) -> None:
        """
        Creates the default config file
        """
        self.reset_parser()
        self.config_parser.add_section("Paths")
        self.config_parser.set("Paths", "# You can write paths in Windows format or Linux/POSIX format.")
        self.config_parser.set("Paths", "# A trailing '/' at the end of the final directory in a POSIX path")
        self.config_parser.set("Paths", "# or a '\\' at the end of the final directory of a Windows path")
        self.config_parser.set("Paths", "# does not interfere with the path parser.")
        self.config_parser.set("Paths", "")
        for preconf_path in (
                self._subdir_dir,
                ):
            self.config_parser.set("Paths", f"# {preconf_path.comment[0].capitalize()}{preconf_path.comment[1:]}")
            self.config_parser.set("Paths", f"{preconf_path.internal_name}", f"{preconf_path.path}")
        with open(self.path_to_config_file, mode="w", encoding="utf-8") as configfh:
            self.config_parser.write(configfh)
        self.read_config_file()
    def delete_config_file(self) -> None:
        """
        Serves debugging purposes. Deletes the config file.
        """
        try:
            self.path_to_config_file.unlink()
            logger.info(f"{self.path_to_config_file.name} deleted")
        except FileNotFoundError as exc:
            logger.error(f"Could not delete {self.path_to_config_file.name} because it does not exist")
    def getpath(self, section: str, value: str) -> pathlib.Path:
        """
        Returns value from config file as pathlib.Path object
        """
        return pathlib.Path(self.config_parser.get(section, value))
    def geturl(self, section: str, raw_url: str) -> urllib.parse.ParseResult:
        """
        Parses a URL and returns urllib ParseResult
        """
        return urllib.parse.urlparse(self.config_parser.get(section, raw_url))
    def parse(self) -> None:
        """
        Parses the configuration files into usable attributes
        """
        try:
            self.subdir_dir = self.getpath("Paths", "subdir_dir")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exc().splitlines()
            section, variable, value = False, False, False
            for line in lines:
                if "config_parser" in line:
                    match = re.search(self.error_regex, line)
                    if match:
                        section = match.group("section")
                        variable = match.group("variable")
            value = lines[-1].split()[-1]
            if section and variable and value:
                message = f"{self.path_to_config_file.name}: '{variable}' in section '{section}' has an unacceptable value of {value}"
                raise errors.WrongConfiguration(message, None)
            else:
                raise
        except configparser.NoOptionError as err:
            raise errors.WrongConfiguration(f"{self.path_to_config_file.name}: {err.message}", err)
        except configparser.NoSectionError as err:
            raise errors.WrongConfiguration(f"{self.path_to_config_file.name}: {err.message}", err)
        except Exception as err:
            raise errors.WrongConfiguration(f"There is something wrong with {self.path_to_config_file.name}. Please check it carefully or delete it to have it recreated.", err)
    def configure_paths(self, preconf_path: Preconfigured_Path, manually: bool) -> None:
        logger.debug(f"{preconf_path.internal_name} needs to be reconfigured")
        if manually:
            logger.debug(f"Configuring paths manually")
            while True:
                try:
                    path_to_create = utils.input_path(f"Input a {preconf_path.comment}: ")
                    created_path = utils.provide_dir(path_to_create)
                    break
                except OSError as err:
                    logger.error(err)
                    continue
        else:
            logger.debug(f"Configuring paths automatically")
            created_path = utils.provide_dir(preconf_path.path)
        preconf_path.path = created_path
        self.create_config_file()
        self.integrity_check()
    def wizard(self, error: errors.WrongConfiguration, autoconfig: bool) -> None:
        """
        Configuration wizard guides the user through the initial setup process
        """
        wiz_menu = menu.Text_Menu(menu_name="Configuration Wizard", heading=r"""
 ____ ____ __ _ ____ _ ____ _  _ ____ ____ ___ _ ____ __ _
 |___ [__] | \| |--- | |__, |__| |--< |--|  |  | [__] | \|
 _  _ _ ___  ____ ____ ___
 |/\| |  /__ |--| |--< |__>
 """)
        if not self._wizard_has_run:
            wiz_menu.show_heading()
        self._wizard_has_run = True
        if "path does not exist" in error.message:
            reason = (f"{error.payload.internal_name} ({error.payload.path}) does not exist!")
            options = OrderedDict((
                    ("A", "Automatically configure this and all remaining claws settings"),
                    ("C", "Create this path automatically"),
                    ("M", "Manually input correct path to use or to create"),
                    ("Q", f"Quit and edit `{error.payload.internal_name}` in {self.path_to_config_file.name}"),
                ))
            if autoconfig:
                choice = "C"
            else:
                choice = None
            if not choice:
                wiz_menu.show_reason(reason)
                choice = wiz_menu.choose_from(options)
            if choice == "A":
                self.autoconfig = True
            logger.debug(f"Your choice: {choice}")
            if choice == "C":
                self.configure_paths(error.payload, manually=False)
            elif choice == "M":
                self.configure_paths(error.payload, manually=True)
            elif choice == "Q":
                raise errors.WrongConfiguration(f"Who needs a wizard, when you can edit `{self.path_to_config_file.name}` yourself, right?", None)
            self.integrity_check()
        else:
            raise NotImplementedError(f"Starting configuration wizard with {err.message} is not implemented yet")


if __name__ == "__main__":
    pass
