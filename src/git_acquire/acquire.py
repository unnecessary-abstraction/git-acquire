# Copyright (c) 2021-2022 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import subprocess
from urllib.parse import urlparse


def default_local_path(source):
    basename = os.path.basename(source)
    if basename.endswith(".git"):
        return basename[:-4]
    else:
        return basename


class Acquisition:
    def __init__(
        self, source, refspec="main", local_path=None, patches=None, mirror_root=None
    ):
        self.source = source
        self.refspec = refspec
        self.local_path = local_path or default_local_path(source)
        self.patches = patches or []
        self.mirror_path = None
        if mirror_root:
            url = urlparse(self.source)
            mirror_path = os.path.join(mirror_root, url.hostname, url.path.lstrip("/"))
            if os.path.exists(mirror_path):
                self.mirror_path = mirror_path

    def acquire(self):
        logging.info(f"Acquiring from '{self.source}' into '{self.local_path}'")
        if self.mirror_path:
            logging.info(f"Using mirror '{self.mirror_path}'")
        if os.path.exists(self.local_path):
            self.do_fetch()
        else:
            self.do_clone()
        self.do_checkout()
        self.do_patch()

    def add_remote(self, remote_name, remote_url):
        logging.debug(f"Adding remote '{remote_name}' with URL '{remote_url}'")
        subprocess.run(
            ["git", "remote", "add", remote_name, remote_url],
            cwd=self.local_path,
            check=True,
        )
        logging.debug(f"Fetching remote '{remote_name}'")
        subprocess.run(
            ["git", "fetch", "-q", remote_name], cwd=self.local_path, check=True
        )

    def do_clone(self):
        logging.debug(f"Initializing git repository in '{self.local_path}'")
        subprocess.run(["git", "init", "-q", self.local_path], check=True)
        if self.mirror_path:
            self.add_remote("mirror", self.mirror_path)
        self.add_remote("origin", self.source)

    def update_remote(self, remote_name, remote_url):
        rc = subprocess.run(
            ["git", "config", "--get", f"remote.{remote_name}.url"],
            cwd=self.local_path,
            capture_output=True,
        )
        if rc.returncode != 0:
            logging.debug(f"Remote '{remote_name}' doesn't exist")
            return self.add_remote(remote_name, remote_url)

        current_remote_url = rc.stdout.decode("utf-8").strip()
        logging.debug(f"Remote '{remote_name}' has URL '{current_remote_url}'")
        if current_remote_url != remote_url:
            logging.debug(f"Updating remote '{remote_name}' URL to '{remote_url}'")
            subprocess.run(
                ["git", "remote", "set-url", remote_name, remote_url],
                cwd=self.local_path,
                check=True,
            )
        logging.debug(f"Fetching remote '{remote_name}'")
        subprocess.run(
            ["git", "fetch", "-q", remote_name], cwd=self.local_path, check=True
        )

    def do_fetch(self):
        if self.mirror_path:
            self.update_remote("mirror", self.mirror_path)
        self.update_remote("origin", self.source)

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
            logging.debug("Assuming refspec is a commit hash or tag")
            subprocess.run(
                ["git", "checkout", "-q", "--detach", self.refspec],
                cwd=self.local_path,
                check=True,
            )

    def do_patch(self):
        for patch in self.patches:
            logging.info(f"Applying patch '{patch}'")
            subprocess.run(
                ["git", "am", "-q", os.path.abspath(patch)],
                cwd=self.local_path,
                check=True,
            )
