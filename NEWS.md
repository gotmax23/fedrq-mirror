fedrq 0.4.1
============

This is a minor bugfix release that accounts for breaking libdnf5 API changes.

Fixed
------

- BaseMaker: make compatible with libdnf5 changes. libdnf5 [changed its
  configuration API](https://github.com/rpm-software-management/dnf5/pull/327)
  so BaseMaker needs to be adjusted accordingly. For now, fedrq maintains
  compatibility with both API versions.
- Clarify explanatory comments in api_examples

Added
------

- Add location attr to PackageCompat and formatters.
  Example: `fedrq pkgs ansible -Flocation`

Testing and Dev Workflow
------------------------

- Add nox targets to release fedrq


fedrq 0.4.0
===========

Changed
--------

- fedrq is now in beta.
- fedrq.spec: Always Require distribution-gpg-keys
- Command: simplify smartcache and load_filelists
- change logging format to include line numbers

Added
-----

CLI:

- Add CentOS Stream 9 release configuration
- Add new formatter `plainwithrepo`. Try it with `fedrq CMD -F plainwithrepo`.
  Contributed by ~amoralej.
- Document `whatrequires-src` subcommand.

- Cleanup fedrq.cli.formatters interface (PRIVATE API)

API:

- Cleanup API interface and mark it as public. Add docstrings.
- Add initial API documentation and examples. More to come.
- Make `fedrq.backends.libdnf5.backend.Package` hashable.
- Add __lt__ and __gt__ methods to `fedrq.backends.libdnf5.backend.Package`.
  Use the same sort algorithm as hawkey.
- Add `create_repo()` method to BaseMaker
- BaseMaker and Repoquery: add `backend` property to access the current backend module
- libdnf5: add `config_loaded` param to BaseMaker

Tests
------

- .builds f36: don't run unit tests twice
- Remove lint.sh in favor of nox and switch to ruff
- Fix ruff linting errors

New Contributors
-----------------

- Thanks to Alfredo Moralejo (~amoralej) for contributing the `plainwithrepo`
  formatter.


fedrq 0.3.0
============

Changed
---------
- Get rid of importlib_resources on Python 3.9. We can use the stdlib version.
- Stop excluding files from the sdist.
- Abstract dnf code into backends. (INTERNAL API)
  - `fedrq.repoquery` is now a shim module that tries to import Repoquery and
    BaseMaker from `fedrq.backends.dnf.backend` and then falls back to
    `fedrq.backends.dnf.backend`.
  - `fedrq.repoquery.Repoquery` and `fedrq.repoquery.BaseMaker`'s interfaces
    are mostly unchanged, but they now point to the appropriate backend in
    `fedrq.backends`.
- Make loading filelists optional.

Added
-------
- **Add a libdnf5 backend.**
    - Use *-b* / *--backend* or `backend` in the config file to explicitly
      choose a backend. Otherwise, the default backend (currently dnf) will be
      used.
- Add `whatrequires-src` subcommand and a `wrsrc` alias.
- Add `wr` alias for `whatrequires` subcommand.
- Add --forcearch flag
- Add a `fedrq.backends.get_default_backend()` function to import backends.
  This provides more flexibility than `fedrq.repoquery` which is now a shim
  module and is the recommended approach. (INTERNAL API)

Fixed
-------
- whatrequires -P: don't resolve SRPM names
- Repoquery: ensure all Provides are resolved

Documentation
-------------
- fedrq.1: add --backend and --filelists.
- fedrq.5: document `backend` and `filelist` config options

Testing
---------
- .builds: Use fclogr main branch
- Fix Copr dev builds
- .builds: Run rpmlint
- Allow test parallelization
- Adopt nox as a test runner.
- noxfile: Use editable install for local testing
- Test libdnf5 backend
- .builds: test libdnf5 backend on f36
- nox: add libdnf5_test target
- nox: add testa target to test both backends at once


fedrq 0.2.0
============

Changed
-------
- Use $XDG_CACHE_HOME/fedrq to store instead of /var/tmp to store
  smartcache. This removes `fedrq.cli.Command.v_cachedir()`,
  `fedrq._utils.make_cachedir()`, and `fedrq.config.SMARTCACHE_BASEDIR`;
  they're no longer needed after this change.

Fixed
-----
- Fix EL 9 and Python 3.9 compatibility
    - Add fallback Fedora repository definitions.
    - Use `importlib_resources` backport.
    - Don't use @staticmethod as a decorator. This doesn't work with
      Python 3.9.

Dev Changes
-----------
- Remove unnecessary `argparse.ArgumentParser.parse_args` workaround
- Fix importlib_resources.abc.Traversable type checking
- Test and lint on EPEL 9 and Fedora 36 in CI
- lint.sh: Ensure all test files are formatted
- Ditch rpmautospec in favor of fclogr


fedrq 0.1.0
============

Summary
--------
- New JSON formatter
- `fedrq subpkgs --match` to filter `fedrq subpkgs` output packages
- Add smartcache CLI flag and config option to avoid clearing the system
  cache when repoquerying different versions.

- Backend improvements and cleanup
- More test coverage
- Docs improvements

Bugfixes
----------
- Tweak README wording
- Command: Fix configuration error handling
- Make _v_fatal_error and _v_handle_errors DRY
- Fix --notsrc on 32 bit x86
- Fix cli.Subpkgs v_arch() method
- Add more config validation

Tests
------
- Reorganize tests
- tests: Don't hardcode x86_64
- Add basic `fedrq pkgs` integration test
- Test --exclude-subpackages
- Reformat fedrq.1 yet again
- Add formatters sanity test
- formatters: Add tests and improve error handling
- Test smartcache config option

New Features
-------------
- Add initial --smartcache implementation
- Allow setting smartcache in config file and enable it by default
- formatters: Add missing attrs
- Add json formatter
- subpkgs: Add --match option
- Add fedrq(5) manpage

Breaking API Changes
---------------------
*Note that fedrq's API is currently unstable and not intended for
outside usage.*

- Rearchitect make_base()
- Replace cli.base.get_packages with Repoquery method
- Reimplement FormatterContainer (private API)


fedrq 0.0.2
===========

- pyproject.toml: Add project.urls
- pyproject.toml: Change Development Status to Alpha
- Truncate RPM changelog
- Exclude rpmautospec `changelog` from sdist
- fedrq.spec: Workaround F36's old flit-core
- fedrq.spec: Remove unnecessary rpmdevtools BR
- Add fedrq-dev copr


fedrq 0.0.1
=======
Initial release
