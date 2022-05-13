# Copyright (c) 2021-2022 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess


def default_local_path(source):
    basename = os.path.basename(source)
    if basename.endswith(".git"):
        return basename[:-4]
    else:
        return basename


class Acquisition:
    def __init__(self, source, refspec="main", local_path=None):
        self.source = source
        self.refspec = refspec
        self.local_path = local_path or default_local_path(source)

    def acquire(self):
        if os.path.exists(self.local_path):
            self.do_fetch()
        else:
            self.do_clone()
        self.do_checkout()

    def do_clone(self):
        subprocess.run(["git", "clone", "-n", self.source, self.local_path], check=True)

    def do_fetch(self):
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
            subprocess.run(
                ["git", "remote", "set-url", "origin", self.source],
                cwd=self.local_path,
                check=True,
            )
        subprocess.run(["git", "fetch", "origin"], cwd=self.local_path, check=True)

    def do_checkout(self):
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
            subprocess.run(
                [
                    "git",
                    "checkout",
                    "-B",
                    self.refspec,
                    f"refs/remotes/origin/{self.refspec}",
                ],
                cwd=self.local_path,
                check=True,
            )
        else:
            subprocess.run(
                ["git", "checkout", "--detach", self.refspec],
                cwd=self.local_path,
                check=True,
            )
