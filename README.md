<!--
Copyright (c) 2022 SanCloud Ltd
SPDX-License-Identifier: CC-BY-4.0
-->

# git-acquire

Efficient acquisition of a git branch, tag or commit with the option to apply
local patches.

"Never spend more for an acquisition than you have to." - Ferengi rules of
acquisition

## Usage

`git-acquire` is a tool for managing the state of a git repository clone in an
declarative and (mostly) idempotent way. The command line arguments specify the
local target directory, the source URL of a git repository, the refspec to
checkout (a branch, tag or commit; defaulting to 'main'), an optional mirror
repository location and an optional set of local patches to apply after
checkout. This makes this tool well suited for use in CI/CD and other
automated workflows.

This tool will first initialize a git repository in the given target
directory if one is not already present.  If a mirror repository URL is
supplied, This tool will fetch from this mirror repository first on the
assumption that the mirror repository is local or on-site and therefore faster
to access than the source repository. This tool will then fetch from the
source repository and checkout the desired branch, tag or commit. Finally, if
any patches are supplied these will be applied in order.

Running this tool multiple times with the same arguments should broadly
result in the target directory arriving in the same state. As patches (if given)
are currently re-applied on each invocation of the tool, the resulting git
commit hash may not remain the same. If the refspec to checkout is a branch, and
this branch is updated in the source repository, then the target directory will
also be updated to the new HEAD commit of this branch. Other than these caveats,
this tool should operate in an idempotent fashion.

Through the use of an optional local or on-site mirror repository and the fact
that only new commits will be fetched if the source repository was already
checked out in the target directory, using this tool will be more efficient
than cloning a source repository from scratch each time.

This tool can be invoked as either `git-acquire` or `git acquire` when present
on the current PATH.

### Command Line Arguments

```
usage: git-acquire [-h] [--version] [-r REFSPEC] [-l LOCAL_PATH] [-p PATCH]
                   [-m MIRROR_ROOT] [-v] source

Efficient acquisition of a git branch/tag/commit

positional arguments:
  source                Source URI to clone or fetch from

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -r REFSPEC, --refspec REFSPEC
                        Refspec (branch, tag or commit) to checkout
  -l LOCAL_PATH, --local-path LOCAL_PATH
                        Local path in which to perform the checkout
  -p PATCH, --patch PATCH
                        Apply patch(es) to the git repository after checkout.
                        May be specified multiple times to apply several
                        patches in order
  -m MIRROR_ROOT, --mirror-root MIRROR_ROOT
                        Root directory of a tree of mirror repositories
  -v, --verbose         Show verbose output
```

### Managing mirror repositories

Mirror repositories are expected to be organized under a "mirror root" path
which will be provided as a command line argument to this tool. The path to
an individual mirror repository is formed by joining this root path with the
fully-qualified domain name and relative path of the source repository URI. For
example, if the mirror root path is given as `/srv/mirror` and the source
repository URI is `https://github.com/torvalds/linux.git`, the mirror repository
path used by this tool will be `/srv/mirror/github.com/torvalds/linux.git`.

To manage and update a tree of mirror repositories, the
[mirrorshades](https://pypi.org/project/mirrorshades/) tool can be used.

## Maintainers

* Paul Barker
  [:envelope:](mailto:paul.barker@sancloud.com)

## License

Copyright (c) 2021-2022 SanCloud Ltd.

* Code files are distributed under the
  [Apache 2.0 License](https://tldrlegal.com/license/apache-license-2.0-(apache-2.0)).

* Documentation files are distributed under the
  [CC BY 4.0 License](https://tldrlegal.com/license/creative-commons-attribution-4.0-international-(cc-by-4)).

* Trivial data files are distributed under the
  [CC0 1.0 License](https://tldrlegal.com/license/creative-commons-cc0-1.0-universal).
