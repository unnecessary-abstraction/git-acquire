# Copyright (c) 2021 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging

from . import __progname__, __description__, __version__
from .acquire import Acquisition


def parse_args():
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
    parser.add_argument(
        "-p",
        "--patch",
        metavar="PATCH",
        dest="patches",
        action="append",
        help=(
            "Apply patch(es) to the git repository after checkout. "
            "May be specified multiple times to apply several patches in order"
        ),
    )
    parser.add_argument(
        "-m", "--mirror-root", help="Root directory of a tree of mirror repositories"
    )
    parser.add_argument("source", help="Source URI to clone or fetch from")
    return parser.parse_args()


def main():
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    args = parse_args()

    a = Acquisition(
        args.source,
        refspec=args.refspec,
        local_path=args.local_path,
        patches=args.patches,
        mirror_root=args.mirror_root,
    )
    a.acquire()


if __name__ == "__main__":
    main()
