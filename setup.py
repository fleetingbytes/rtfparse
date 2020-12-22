#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
import pathlib
import re


this_dir = pathlib.Path(__file__).parent.absolute()
project_name = "pyrtfparse"
package_dir = "src"
path_to_init_file = this_dir / package_dir / project_name / "__init__.py"


with open(this_dir / "README.md", encoding="utf-8") as file:
    long_description = file.read()


with open(this_dir / "requirements.txt", encoding="utf-8") as reqs:
    requirements = [line.strip() for line in reqs]


def get_property(property: str, path_to_init_file: pathlib.Path) -> str:
    """
    Reads a property from the project's __init__.py
    e.g. get_property("__version__") --> "1.2.3"
    """
    regex = re.compile(r"{}\s*=\s*[\"'](?P<value>[^\"']*)[\"']".format(property))
    try:
        with open(path_to_init_file) as initfh:
            try:
                result = regex.search(initfh.read()).group("value")
            except AttributeError:
                result = None
    except FileNotFoundError:
        result = None
    return result


setup(
        name=project_name,
        version=get_property("version", path_to_init_file.parent / "version.py"),
        description="RTF parser",
        long_description=long_description,
        author=get_property("__author__", path_to_init_file),
        author_email=get_property("__author_email__", path_to_init_file),
        url="https://github.com/Nagidal/pyrtfparse",
        classifiers=[
            "Development Status :: 2 - Pre-Alpha"
            # "Development Status :: 3 - Alpha",
            # "Development Status :: 4 - Beta", 
            # "Development Status :: 5 - Production/Stable"
            # "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Environment :: Console",
            "Topic :: Software Development :: Testing",
            "Topic :: Utilities",
            "License :: Free To Use But Restricted",
            "Natural Language :: English",
            "Programming Language :: Python :: 3.9",
            "Operating System :: OS Independent",
            "Operating System :: Microsoft :: Windows"
            "Operating System :: POSIX :: Linux",
            "Operating System :: MacOS :: MacOS X",
            ],
        keywords="parsing rtf",
        package_dir={"": package_dir},
        packages=find_packages(where=package_dir),
        package_data={
            project_name: [],
            },
        python_requires=">=3.9",
        install_requires=requirements,
        entry_points={
            "console_scripts": [f"{project_name} = {project_name}.__main__:{project_name}",
                ],
            },
        platforms=["any"],
    )
