#!/usr/bin/env python


# Towncrier needs version
# from rtfparse.__about__ import __version__
__all__ = ["rtfparse", "rtfparse.__about__.__version__"]

if __name__ == "__main__":
    from rtfparse.cli import main

    main()
