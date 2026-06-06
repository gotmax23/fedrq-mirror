<!--
SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
SPDX-License-Identifier: GPL-2.0-or-later
-->

# Contributing

This project's mailing list is [~gotmax23/fedrq@lists.sr.ht][mailto]
([archives]).

Project discussion happens on the mailing list.
Patches can be submitted via pull request on Fedora Forge.

## Patches

Contributions are always welcome!
It is recommended that you send a message to the mailing list before working on
a larger change.

## Linting and Unit Tests

Unit tests are run with `pytest`.
This project uses isort and black to format code, ruff for linting, and mypy
for type checking.
`reuse lint` is used to ensure that code follows the REUSE specification.
You can run all of these tools using nox. Simply install nox with pip or dnf.
The tests also require the `rpm-build` and createrepo_c` and packages.

CI also runs a mock build against rawhide.
Run `nox -e srpm` to build an SRPM containing the git HEAD
or run `nox -e mockbuild` to preform a build in mock.

builds.sr.ht runs CI for Fedora Forge pull requests,
but please run the tests locally before submitting your changes.
See the `.builds` directory for the CI workflow configuration.

[mailto]: mailto:~gotmax23/fedrq@lists.sr.ht
[archives]: https://lists.sr.ht/~gotmax23/fedrq
