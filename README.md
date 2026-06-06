<!--
SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
SPDX-License-Identifier: GPL-2.0-or-later
-->

# fedrq

A tool for querying the Fedora and EPEL repositories

fedrq makes it easy to query any branch of Fedora or EPEL. It uses the dnf
Python bindings and does not shell out to `dnf repoquery`. It allows querying
for reverse dependencies, packages that contain a certain Provide or file,
subpackages of an SRPM, and package metadata.

The tool doesn't seek to replace every feature of `dnf repoquery`. It provides a
more user friendly interface than `dnf repoquery` for certain common tasks.

[![builds.sr.ht status](https://builds.sr.ht/~gotmax23/fedrq/commits/main.svg)](https://builds.sr.ht/~gotmax23/fedrq/commits/main?)

[![copr build status][badge-copr]][link-copr] (stable)

[![copr build status][badge-copr-dev]][link-copr-dev] (dev)

[![docsite][badge-docsite]][link-docsite]


## Installation

fedrq has a Copr repository at [gotmax23/fedrq][link-copr] that contains
released versions.
Development snapshots are available at [gotmax23/fedrq-dev][link-copr-dev].
The RPM specfile is located in the repository root.

fedrq is also [published to PyPI](https://pypi.org/project/fedrq/) so you can
`pip install fedrq`.

When installing the package with pip, some additional system packages
are needed.

The following additional system package is required for the dnf backend:

- python3-dnf (dnf is currently the default Fedora package manager, so this
  should already be installed)

The following additional system packages are required for the libdnf5 backend:

- python3-libdnf5

The following additional system packages are always required:

- python3-rpm

fedrq defaults to the dnf backend, but fedrq falls back to the libdnf5 backend
if the former's dependencies aren't installed.
Users can explicitly choose a backend with the
`--backend` [CLI option](https://fedrq.gtmx.me/fedrq1/#shared-options)
or globally in the [fedrq config file](https://fedrq.gtmx.me/fedrq5).

Note that fedrq can only be installed for the system python interpreter.
fedrq cannot be installed in a venv unless it has `--system-site-packages`,
as it needs to find the aforementioned system bindings.

`fedrq check-config --dump` requires `tomli-w`.
The RPM package weakly depends on `python3-tomli-w`.

## Container images

fedrq now provides container images.

- [`quay.io/gotmax23/fedrq:latest`][Containerfile] is built with
  `registry.fedoraproject.org/fedora:latest`.
- [`quay.io/gotmax23/fedrq:ubi9`][Containerfile.rhel] is built with the ubi9
  image.
  It includes a builtin `rhel9` repository configuration that can be used to
  query the actual RHEL repositories when run on a system registered with
  subscription-manager.

Both of these images use the latest fedrq RPM packages from the
[gotmax23/fedrq][link-copr] Copr repository.

``` console
$ podman run --rm -v ~/.cache/fedrq:/fedrq-cache/fedrq:z quay.io/gotmax23/fedrq \
    pkgs fedrq -Fnevrr
fedrq-0.9.0-1.fc39.noarch rawhide
fedrq-0.9.0-1.fc39.src rawhide-source
```

[Containerfile]: https://git.sr.ht/~gotmax23/fedrq/tree/main/item/contrib/container/Containerfile
[Containerfile.rhel]: https://git.sr.ht/~gotmax23/fedrq/tree/main/item/contrib/container/Containerfile.rhel

## Versioning

This project's versioning scheme follows semver.

See [NEWS].

## Python API

The `fedrq.config` module and the `fedrq.backend` package are public API.
Everything under `fedrq.cli` is internal. fedrq is primarily a CLI tool and
its API only abstracts the specific dnf/libdnf5 functionality that the CLI uses. The
API's main purpose is "repoquerying", but you can use the fedrq functionality
you'd like and then access the underlying dnf Base object to preform other
tasks if needed.

See the [API Summary] on the docsite for more information. See [api-examples]
for some example code. As always, direct any feedback, questions, or issues to
the mailing list (see [Contributing](#contributing)).

[API Summary]: https://fedrq.gtmx.me/API/Summary/


## Documentation

See fedrq's [documentation site][link-docsite] for rendered manpages, changelogs, and
Python API documentation.


## Contributing

See [CONTRIBUTING.md].

## Author

Maxwell G (@gotmax23)

## Credits

Thank you to the dnf maintainers. This tool is inspired by `dnf repoquery` and
uses the dnf python bindings.


## License

This project follows the REUSE specification. In general:

- Code is licensed under GPL-2.0-or-later. This is the same license as dnf.
- Configuration and repo files in fedrq/data/ are `UNLICENSE`ed
- fedrq.spec is licensed under MIT to match Fedora
- The embedded repo defs in src/fedrq/data/repos from fedora-repos.rpm are MIT
  licensed.
  These are only used when the needed repo defs are not available in the system
  config (i.e., for querying the Fedora repos from a non Fedora system).
- `enum.StrEnum` is copied from Cpython 3.11 for older Python versions. It's
  ~30 lines of PSF-2.0 licensed code.

```
SPDX-License-Identifier: GPL-2.0-or-later AND Unlicense AND MIT AND PSF-2.0
```


[NEWS]: https://fedrq.gtmx.me/News/
[CONTRIBUTING.md]: https://forge.fedoraproject.org/packaging/fedrq/src/branch/main/CONTRIBUTING.md
[api-examples]: https://forge.fedoraproject.org/packaging/fedrq/src/branch/main/contrib/api_examples
[badge-copr]: https://copr.fedorainfracloud.org/coprs/gotmax23/fedrq/package/fedrq/status_image/last_build.png
[link-copr]: https://copr.fedorainfracloud.org/coprs/gotmax23/fedrq/
[badge-copr-dev]: https://copr.fedorainfracloud.org/coprs/gotmax23/fedrq-dev/package/fedrq/status_image/last_build.png
[link-copr-dev]: https://copr.fedorainfracloud.org/coprs/gotmax23/fedrq-dev/
[badge-docsite]: https://img.shields.io/badge/docs-fedrq-blue?style=for-the-badge&logo=readthedocs
[link-docsite]: https://fedrq.gtmx.me
