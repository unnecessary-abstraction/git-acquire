# Copyright (c) 2021-2022 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse


__progname__ = "git-acquire"
__description__ = "Efficient acquisition of a git branch/tag/commit"
__version__ = "0.1.0-dev"


def main():
    parser = argparse.ArgumentParser(prog=__progname__, description=__description__)
    parser.add_argument(
        "--version", action="version", version=f"{__progname__} {__version__}"
    )
    parser.parse_args()
