# Copyright (c) 2021 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

from invoke import task


@task
def install(c):
    """Install the project locally"""
    c.run("python3 -m pip install .")


@task
def install_deps(c):
    """Install dependencies only (for local development)"""
    import configparser
    import shlex

    config = configparser.ConfigParser()
    config.read("setup.cfg")
    deps = shlex.join(config["options"]["install_requires"].strip().split("\n"))
    c.run(f"python3 -m pip install {deps}")


@task
def build(c):
    """Build the project"""
    c.run("python3 -m build .")


@task
def clean(c):
    """Remove build output"""
    c.run("rm -rf build dist src/*.egg-info")


@task
def test(c):
    """Check the code for errors"""
    c.run('PYTHONPATH="$(realpath src):${PYTHONPATH}" pytest tests')
