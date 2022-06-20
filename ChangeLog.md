<!--
Copyright (c) 2022 SanCloudLtd
SPDX-License-Identifier: CC-BY-4.0
-->

# ChangeLog for git-acquire

## 0.1.0

Initial public release.

* Support use of local mirrors to accelerate clone or fetch.

* Improve output and support verbose mode.

* Switch from `invoke` to a maintainer script for automation of maintainer tasks.

## 0.0.2

Internal fixup release.

* Fix handling of empty patches list.

* Install git-acquire command.

* Improve release automation.

## 0.0.1

Initial internal release for testing.

Supports checking out a single git repository and optionally applying a series
of patches. The source URI, refspec to checkout, local (destination) path and
list of patches are supplied as command line arguments.

Documentation, error handling, tests and configuration are all TODO.
