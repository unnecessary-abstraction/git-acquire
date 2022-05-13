# Copyright (c) 2021 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse

from . import __progname__, __description__, __version__
from .acquire import Acquisition


def main():
    parser = argparse.ArgumentParser(prog=__progname__, description=__description__)
    parser.add_argument(
        "--version", action="version", version=f"{__progname__} {__version__}"
    )
    parser.add_argument(
        "-r",
        "--refspec",
        default="main",
        help="Refspec (branch, tag or commit) to checkout",
    )
    parser.add_argument(
        "-l", "--local-path", help="Local path in which to perform the checkout"
    )
    parser.add_argument("source", help="Source URI to clone or fetch from")
    args = parser.parse_args()

    a = Acquisition(args.source, refspec=args.refspec, local_path=args.local_path)
    a.acquire()


if __name__ == "__main__":
    main()
