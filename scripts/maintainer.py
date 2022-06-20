#! /usr/bin/env python3
# Copyright (c) 2021-2022 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import re
import shutil
import subprocess


def run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, check=True, **kwargs)


def capture(cmd, **kwargs):
    return run(cmd, capture_output=True, **kwargs).stdout.decode("utf-8")


def do_build(args):
    run("python3 -m build .")


def do_clean(args):
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("src/git_acquire.egg-info"):
        shutil.rmtree("src/git_acquire.egg-info")


def do_release(args):
    do_clean(args)
    with open("src/git_acquire/__init__.py", "r+") as f:
        text = re.sub(r"(__version__ =).*\n", rf'\1 "{args.version}"\n', f.read())
        f.seek(0)
        f.write(text)
        f.truncate()
    run(f'git commit -asm "Release {args.version}"')
    release_commit = capture("git rev-parse HEAD").strip()
    run(f"git push origin {release_commit}:refs/heads/release")
    run(f"git push gh {release_commit}:refs/heads/release")
    do_build(args)
    with open("dist/RELEASE_NOTES.txt", "w") as f:
        f.write(f"git-acquire {args.version}\n")
        text = capture(f"markdown-extract -n ^{args.version} ChangeLog.md")
        f.write(text)
    run(f"git tag -a -F dist/RELEASE_NOTES.txt v{args.version} HEAD")
    run(f"git push origin v{args.version}")
    run(f"git push gh v{args.version}")
    with open("dist/SHA256SUMS", "w") as f:
        text = capture(
            "sha256sum RELEASE_NOTES.txt "
            f"git-acquire-{args.version}.tar.gz git_acquire-{args.version}-py3-none-any.whl",
            cwd="dist",
        )
        f.write(text)
    if args.sign:
        run("gpg --detach-sign -a dist/SHA256SUMS")
    if not args.no_gitlab:
        run(f"glab release create v{args.version} -F dist/RELEASE_NOTES.txt dist/*")
        run(
            "twine upload -r gitlab "
            f"dist/git-acquire-{args.version}.tar.gz "
            f"dist/git_acquire-{args.version}-py3-none-any.whl"
        )
    run(f"gh release create v{args.version} -F dist/RELEASE_NOTES.txt dist/*")
    run(
        "twine upload "
        f"dist/git-acquire-{args.version}.tar.gz "
        f"dist/git_acquire-{args.version}-py3-none-any.whl"
    )


def do_set_version(args):
    with open("src/git_acquire/__init__.py", "r+") as f:
        text = re.sub(r"(__version__ =).*\n", rf'\1 "{args.version}"\n', f.read())
        f.seek(0)
        f.write(text)
        f.truncate()
    run(f'git commit -asm "Bump version to {args.version}"')


def do_no_command(args):
    print("Missing command! Try `./scripts/maintainer.py --help`")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.set_defaults(cmd_fn=do_no_command)
    subparsers = parser.add_subparsers(
        dest="cmd", title="Maintainer commands", metavar="command"
    )

    build_cmd = subparsers.add_parser(name="build", help="Build a wheel")
    build_cmd.set_defaults(cmd_fn=do_build)

    clean_cmd = subparsers.add_parser(
        name="clean", help="Remove build output from the source tree"
    )
    clean_cmd.set_defaults(cmd_fn=do_clean)

    release_cmd = subparsers.add_parser(
        name="release", help="Release a new version of this project"
    )
    release_cmd.set_defaults(cmd_fn=do_release)
    release_cmd.add_argument("version", help="Version string for the new release")
    release_cmd.add_argument(
        "-s", "--sign", action="store_true", help="Sign release with gpg"
    )
    release_cmd.add_argument(
        "--no-gitlab",
        action="store_true",
        help="Disable push to SanCloud gitlab instance",
    )

    set_version_cmd = subparsers.add_parser(
        name="set-version", help="Set version string & commit"
    )
    set_version_cmd.set_defaults(cmd_fn=do_set_version)
    set_version_cmd.add_argument("version", help="New version string")

    return parser.parse_args()


def main():
    args = parse_args()
    args.cmd_fn(args)


if __name__ == "__main__":
    main()
