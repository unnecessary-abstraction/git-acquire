# Copyright (c) 2021-2022 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import subprocess


def default_local_path(source):
    basename = os.path.basename(source)
    if basename.endswith(".git"):
        return basename[:-4]
    else:
        return basename


class Acquisition:
    def __init__(self, source, refspec="main", local_path=None, patches=[]):
        self.source = source
        self.refspec = refspec
        self.local_path = local_path or default_local_path(source)
        self.patches = patches

    def acquire(self):
        logging.info(f"Acquiring '{self.source}'")
        if os.path.exists(self.local_path):
            self.do_fetch()
        else:
            self.do_clone()
        self.do_checkout()
        self.do_patch()

    def do_clone(self):
        logging.info(f"Cloning into '{self.local_path}'")
        subprocess.run(
            ["git", "clone", "-q", "-n", self.source, self.local_path], check=True
        )

    def do_fetch(self):
        logging.info(f"Fetching in '{self.local_path}'")
        remote_url = (
            subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.local_path,
                check=True,
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .strip()
        )
        if remote_url != self.source:
            logging.info(f"Replacing remote URL, was '{remote_url}'")
            subprocess.run(
                ["git", "remote", "set-url", "origin", self.source],
                cwd=self.local_path,
                check=True,
            )
        subprocess.run(
            ["git", "fetch", "-q", "origin"], cwd=self.local_path, check=True
        )

    def do_checkout(self):
        logging.info(f"Checking out '{self.refspec}'")
        is_ref = (
            subprocess.run(
                ["git", "rev-parse", "--verify", f"refs/remotes/origin/{self.refspec}"],
                cwd=self.local_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )
        if is_ref:
            logging.debug(f"Found 'refs/remotes/origin/{self.refspec}'")
            subprocess.run(
                [
                    "git",
                    "checkout",
                    "-q",
                    "-B",
                    self.refspec,
                    f"refs/remotes/origin/{self.refspec}",
                ],
                cwd=self.local_path,
                check=True,
            )
        else:
            logging.debug("Assuming refspec is a commit hash")
            subprocess.run(
                ["git", "checkout", "-q", "--detach", self.refspec],
                cwd=self.local_path,
                check=True,
            )

    def do_patch(self):
        for patch in self.patches:
            fullpath = os.path.abspath(patch)
            logging.info(f"Applying patch '{fullpath}'")
            subprocess.run(
                ["git", "am", "-q", fullpath], cwd=self.local_path, check=True
            )
