NEWS
=====

## fedrq 0.5.0

### New dependencies
- requests

### Highlighted examples

Find the latest version of `fedrq` available in the gotmax23/fedrq-dev copr. No extra configuration is required!

```
$ fedrq pkgs -F nevrr -b f36 -r @copr:gotmax23/fedrq-dev fedrq
fedrq-0.4.1^25.20230318.76d7910-1.fc36.noarch copr:copr.fedorainfracloud.org:gotmax23:fedrq-dev
fedrq-0.4.1^25.20230318.76d7910-1.fc36.src copr:copr.fedorainfracloud.org:gotmax23:fedrq-dev
```

Find the packages in Fedora and RPMFusion that depend on any subpackage of
ffmpeg. Currently, fedrq does not have a builtin rpmfusion configuration, but
with the repo loading revamp, fedrq can read arbitrary repositories from the
system configuration. It's just not as nice and convenient.

```
$ fedrq wrsrc ffmpeg -b f37 --enablerepo=rpmfusion-{non,}free{,-updates}{,-source} -Fline:na,repoid
HandBrake.src : rpmfusion-free-source
HandBrake.x86_64 : rpmfusion-free
HandBrake-gui.x86_64 : rpmfusion-free
[...]
mpv.src : updates-source
mpv.x86_64 : updates
mpv-libs.i686 : updates
mpv-libs.x86_64 : updates
[...]
```

### Changed
- Release: use releasever as cache directory key (https://todo.sr.ht/~gotmax23/fedrq/18)
- change format of copr_chroot_fmt in ReleaseConfig
- config: improve Release repository loading.
  Previously, a repository id that was defined in one of the repo files in a
  release's `defpaths` and also defined in the system configuration (when
  system_repos=true) would cause fedrq to crash when loading repositories. Now,
  system repositories are loaded first and then only repositories that are not
  already defined are loaded from defpaths. system_repos=false works the same as before
- add new repository loading API and dep on requests
  (https://todo.sr.ht/~gotmax23/fedrq/21,
  [More details](https://git.sr.ht/~gotmax23/fedrq/commit/85655fa3251b8c21f000dc04c2a8f54720c786f2))
- config: plug in new repository loading API
  ([More details](https://git.sr.ht/~gotmax23/fedrq/commit/68fd6d31dc64bdffc3f3867992eb1d82ff0a9f03))
- release.toml: update for new reoo loading API

### Added
- Add centos-stream8 release configuration
- Add whatobsoletes subcommand
- formatters: add full_nevra formatter
- config: implement recursive config file merging
- cli: add --enablerepo and --disablerepo
- docs: elaborate on new repo classes

BaseMaker API:

This includes changes to the BaseMaker API
(`fedrq.backends.(lib)dnf(5).backend.BaseMaker`).

- add disable_repo() method
- add repolist() method

fedrq.spec:

- include api_examples in %doc
- explicitly require python3-rpm

### Fixed
- releases.toml: Fix typo in epel_next release def

### Testing and development workflow
- nox: remove fclogr venv workarounds
- ruff: enable unused-arguments rules
- improve test_subpkgs_match2 integration test
- ruff: ignore no-explicit-stacklevel for now
- test Release._copr_repo() formatting
- nox publish: install all deps into the venv

## fedrq 0.4.1

This is a minor bugfix release that accounts for breaking libdnf5 API changes.

### Fixed

- BaseMaker: make compatible with libdnf5 changes. libdnf5 [changed its
  configuration API](https://github.com/rpm-software-management/dnf5/pull/327)
  so BaseMaker needs to be adjusted accordingly. For now, fedrq maintains
  compatibility with both API versions.
- Clarify explanatory comments in api_examples

### Added

- Add location attr to PackageCompat and formatters.
  Example: `fedrq pkgs ansible -Flocation`

### Testing and Dev Workflow

- Add nox targets to release fedrq


## fedrq 0.4.0

### Changed

- fedrq is now in beta.
- fedrq.spec: Always Require distribution-gpg-keys
- Command: simplify smartcache and load_filelists
- change logging format to include line numbers

### Added

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

### Tests

- .builds f36: don't run unit tests twice
- Remove lint.sh in favor of nox and switch to ruff
- Fix ruff linting errors

### New Contributors

- Thanks to Alfredo Moralejo (~amoralej) for contributing the `plainwithrepo`
  formatter.


## fedrq 0.3.0

### Changed
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

### Added
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

### Fixed
- whatrequires -P: don't resolve SRPM names
- Repoquery: ensure all Provides are resolved

### Documentation
- fedrq.1: add --backend and --filelists.
- fedrq.5: document `backend` and `filelist` config options

### Testing
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


## fedrq 0.2.0

### Changed
- Use $XDG_CACHE_HOME/fedrq to store instead of /var/tmp to store
  smartcache. This removes `fedrq.cli.Command.v_cachedir()`,
  `fedrq._utils.make_cachedir()`, and `fedrq.config.SMARTCACHE_BASEDIR`;
  they're no longer needed after this change.

### Fixed
- Fix EL 9 and Python 3.9 compatibility
    - Add fallback Fedora repository definitions.
    - Use `importlib_resources` backport.
    - Don't use @staticmethod as a decorator. This doesn't work with
      Python 3.9.

### Dev Changes
- Remove unnecessary `argparse.ArgumentParser.parse_args` workaround
- Fix importlib_resources.abc.Traversable type checking
- Test and lint on EPEL 9 and Fedora 36 in CI
- lint.sh: Ensure all test files are formatted
- Ditch rpmautospec in favor of fclogr


## fedrq 0.1.0

### Summary
- New JSON formatter
- `fedrq subpkgs --match` to filter `fedrq subpkgs` output packages
- Add smartcache CLI flag and config option to avoid clearing the system
  cache when repoquerying different versions.

- Backend improvements and cleanup
- More test coverage
- Docs improvements

### Bugfixes
- Tweak README wording
- Command: Fix configuration error handling
- Make _v_fatal_error and _v_handle_errors DRY
- Fix --notsrc on 32 bit x86
- Fix cli.Subpkgs v_arch() method
- Add more config validation

### Tests
- Reorganize tests
- tests: Don't hardcode x86_64
- Add basic `fedrq pkgs` integration test
- Test --exclude-subpackages
- Reformat fedrq.1 yet again
- Add formatters sanity test
- formatters: Add tests and improve error handling
- Test smartcache config option

### New Features
- Add initial --smartcache implementation
- Allow setting smartcache in config file and enable it by default
- formatters: Add missing attrs
- Add json formatter
- subpkgs: Add --match option
- Add fedrq(5) manpage

### Breaking API Changes
*Note that fedrq's API is currently unstable and not intended for
outside usage.*

- Rearchitect make_base()
- Replace cli.base.get_packages with Repoquery method
- Reimplement FormatterContainer (private API)


## fedrq 0.0.2

- pyproject.toml: Add project.urls
- pyproject.toml: Change Development Status to Alpha
- Truncate RPM changelog
- Exclude rpmautospec `changelog` from sdist
- fedrq.spec: Workaround F36's old flit-core
- fedrq.spec: Remove unnecessary rpmdevtools BR
- Add fedrq-dev copr


## fedrq 0.0.1

Initial release
