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


@task
def release(c, version):
    """Release a version of the project"""
    clean(c)
    c.run(
        f"sed -i 's/^\\(__version__ =\\).*$/\\1 \"{version}\"/' src/git_acquire/__init__.py"
    )
    c.run(f"git commit -a -s -m 'Release {version}'")
    release_commit = c.run("git rev-parse HEAD").stdout.strip()
    c.run(f"git push origin {release_commit}:refs/heads/release")
    build(c)
    c.run(f"echo git-acquire {version} > dist/RELEASE_NOTES.txt")
    c.run(f"markdown-extract -n '^{version}' ChangeLog.md >> dist/RELEASE_NOTES.txt")
    c.run(f"git tag -a -F dist/RELEASE_NOTES.txt 'v{version}' HEAD")
    c.run(f"git push origin v{version}")
    with c.cd("dist"):
        c.run("sha256sum * > SHA256SUMS")
    c.run(f"glab release create v{version} -F dist/RELEASE_NOTES.txt dist/*")
    c.run(
        "twine upload --config-file .pypirc -r gitlab "
        f"dist/git-acquire-{version}.tar.gz dist/git_acquire-{version}-py3-none-any.whl"
    )
