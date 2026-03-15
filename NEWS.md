NEWS
=====

## 1.5.0 - 2025-03-01 <a id='1.5.0'></a>

### Changed

- Improve typing of backend code, again.
  This mainly affects API users who explicitly opt-in to the libdnf5 backend
  (using `get_config().get_libdnf5_rq()`) and wish to annotate functions that
  interact with `Package`, `PackageQuery`, and/or `Repoquery` objects.

    It is now possible to annotate functions either using the libdnf5-specific
    subclasses (e.g., `fedrq.backends.libdnf5.backend.PackageQuery`)
    for code that only works with libdnf5 and may access lower-level libdnf5 API
    or with the baseclasses (e.g., `fedrq.backends.base.backend.PackageQueryCompat`)
    for code that maintains compatibility with both backends.

## 1.4.0 - 2024-11-01 <a id='1.4.0'></a>

This release contains mostly backend changes and a fix to the CentOS Stream
release configuration.

### Added

- backends: add experimental support for comps groups and environments.
  See the stability warning in the API documentation about experimental code.
- backends base: add `RepoqueryAlias` for typing `RepoqueryBase` subclasses
- config RQConfig: add `get_dnf_rq` and `get_libdnf5_rq` methods to more explicitly
  create a dnf- or libdnf5-based `Repoquery` object
- data releases: add `@koji:<tag>` and `@koji-src:<tag>` `--repo` aliases to
  the `epelX` and `epel-nextX` branch configurations.
- dev: add Github mirror for discoverability

### Fixed
- config `RQConfig`: ensure `backend_mod` and `backend` attributes are synced.
  If the user modifies the `backend` attribute,
  the `backend` property now returns the correct backend module instead of
  caching the old one.
- data releases: adjust releases.toml for new EPEL 10+ branching model.
  This fixes `fedrq ... -b c10s -r @epel`.
  (Contributed by Michel Lind.)

## 1.3.0 - 2024-08-27 <a id='1.3.0'></a>

### CLI improvements

- Make automatic loading of filelists more intelligent.
  Filelists are now loaded automatically when the formatter name includes
  `files` or if any argument looks like a path


### API changes/improvements

- backends: add `difference()` and `intersection()` methods to `PackageQuery`
- backends: add `PackageQueryAlias` to backend modules
- backends base: add missing `nevra_forms` parameter to
  `RepoqueryBase.resolve_pkg_specs()`.
  The dnf and libdnf5 `Repoquery` implementations both accept this argument,
  but it wasn't included in the base class's definition.
- backends base: convert `PackageCompat` to a `Protocol`
- backends libdnf5: fix `filter()` and `filterm()`'s handling of `__contains`
  comparisons, such as `query.filter(name__contains="substring")`.
  Previously, `name__contains` mistakenly checked for packages whose names do
  **not** include the substring.
- packaging: declare project as stable in classifiers

## 1.2.0 - 2024-08-03 <a id='1.2.0'></a>

### Added

- backends base: add `fedrq.backends.base.PackageQueryAlias` that should be
  used to type `PackageQuery`-like objects instead of `PackageQueryCompat`
  directly
- contrib api_examples: add `longest_license` script

### Changed

- backends: fix TypeVar bound type cannot be generic error and refactor
  `PackageQueryCompat` and `RepoqueryBase` typing
- contrib: adjust example scripts for `PackageQueryCompat` typing changes
- config: allow environment variables (`FEDRQ_BRANCH` and `FEDRQ_REPO`) to override config file


### Fixed

- repos epel: fix epel-testing metalink url

## 1.1.0 - 2024-05-01 <a id='1.1.0'></a>

### Added

- backends libdnf5: add dnf 5.2.0.x compatibility

### Changed

- backends: revamp typing for `Package` and `PackageQuery`

## 1.0.0 - 2024-04-01 <a id='1.0.0'></a>

First stable release

### Added

- Containerfiles: add experimental UBI 8–based Containerfile
- cli formatters: add `source+requiresmatch` and `source+rm` formatters

### Changed

- Containerfiles: license under `GPL-2.0-or-later`
- doc fedrq.1: use formatting consistent with `man-pages(7)`

### Fixed

- doc: remove broken reference

### Removed

- cli formatters: remove long-deprecated `_DefaultFormatters` class (INTERNAL API)

## 0.15.0 - 2024-02-13 <a id='0.15.0'></a>

### Added

- backends dnf: add `load_filelists()` implementation. This makes sure that
  systems with `dnf >= 4.19.0` can, for example, use `-L always` to load
  filelists.

### Changed

- doc: revamp and cleanup

### Fixed

- changelogs: fix off-by-one error with `--entry-limit` flag

## 0.14.0 - 2024-02-07 <a id='0.14.0'></a>

### Added

- api: add `fedrq.cli.formatters.Formatters.formatters_it()` method
- cli: add `formatters` subcommand to list formatters
- formatters: add `-F multiline`
- formatters: add `-F requiresmatch` and related formatters
- releases: add `--branch=eln` / `--repo=buildroot` repo definition

### Changed

- api: clean up INTERNAL `fedrq.cli.formatters` API

### Deprecated

- api: deprecate standalone `fedrq.repoquery` module

### Removed

- all: drop support for libdnf5 version less than 5.0.12

## 0.13.0 - 2023-12-18 <a id='0.13.0'></a>

!!! warning
    The next release will drop support for `libdnf5<5.0.12`

### Added

CLI:

- cli `download` / `download-spec`: mark commands as stable and document
- cli: add new `make-cache` subcommand

---

API:

- backends `Repoquery.resolve_pkg_specs`: add `nevra_forms` argument
- backends `Repoquery.resolve_pkg_specs`: allow more granular `resolve` control
- backends: add `allow_multiple_backends_per_process` argument to `get_backend()`
- backends: make `base` a package instead of a single module

---

contrib:

- Caddyfile: update for 404.html template

---

doc:

- API Summary: add dnf and libdnf5 intersphinx links
- dnf-repoquery-diff: fix inter-doc links
- release_repo: add unstable API warning admonition
- add _archive.md API doc

### Changed

- all: use `metaclass=abc.ABCMeta` instead of inheriting `abc.ABC`
- backends: make `libdnf5.backends.${NAME}.backend` packages instead of single modules
- cli: correct license of changelogs and download.
  They are now `GPL-2.0-or-later` as opposed to `MIT`.
- doc: switch to google docstring style

### Fixed

- fedrq.repoquery: fix type checking
- backends dnf: fix `BaseMaker.set_var()` error typo
- cli whatrequires: fix typo (`Exception: Unrecognized key name: recommend`).

## 0.12.0 - 2023-09-11 <a id='0.12.0'></a>

### Added

- whatrequires: add experimental `--extra-exact` argument
- add support for pydantic v2

## 0.11.0 - 2023-08-31 <a id='0.11.0'></a>

### Added

API:

- backends: add `repo` @property to PackageCompat
- BaseMaker: add `load_changelogs()`; improve `load_filelists()`
- BaseMaker: add `conf` property
- backends: add API for accessing Package changelogs

CLI:

- handle repo ssl client certificates in `download` subcommand
- add `changelog` subcommand

Container images:

- add `@epel` release group to the `rhel9` release configuration in the `ubi9`
  container

General:

- Declare support for Python 3.12

### Deprecated

API:

- libdnf5 BaseMaker: deprecate config property

### Fixed

- fix `importlib.abc` `DeprecationWarning`.
- improve CLI error handling by erroring out before loading metadata if other
  non-fatal errors have occurred.
- fix help message in `download` subcommand

### Removed

API:

- config: remove pydantic validators from public API. These never should have
  been exposed in the first place.

## 0.10.0 - 2023-07-12 <a id='0.10.0'></a>

### Added

- add unconditional dependency on python3-rpm
- container - refresh redhat.repo on entrypoint
- add `smartcache=always` config option
- add `--smartcache-always` CLI flag
- add more documentation for the container builds

### Changed

- container - install config file to set `smartcache=always`
- `fedrq.backends.libdnf5.backend.Package` - use libdnf5's getters for
  `debug_name` and `source_debug_name` instead of our copies from dnf4.
  There is still a fallback to the dnf4 versions for libdnf5 < 5.0.12.
- fedrq.spec - favor python3-libdnf5 if dnf5 is installed

### Deprecated

- deprecate support for libdnf5 < 5.0.12 in the libdnf5 backend

### Fixed

- container - make sure cache persistence volume is actually used

### Removed

- remove deprecated `config.get_rq()` function
- drop support for libdnf5 < 5.0.10 in the libdnf5 backend

## 0.9.0 - 2023-06-29 <a id='0.9.0'></a>

### Added

- add remote_location formatter
- document CentOS 7 release configuration
- add UBI release configuration
- add Oracle Linux release configuration
- add Rocky Linux release configuration
- add experimental download and download-spec subcommands
- add fedrq [container builds][container builds]
- add @source-repos repo class
- BaseMaker: add enable_source_repos() method
- PackageCompat: add remote_location() method

### Changed

- Remove enabled=1 from built-in fedora repo defs.
  We want all repo to have enabled=0. We control which repos are enabled and
  disabled with repo groups configured in releases.toml.
  This previously led to divergent behavior with the --repo and --enablerepo
  options when querying Fedora releases on Fedora systems and non-Fedora
  systems (e.g. CentOS).

### Deprecated

- deprecate support for libdnf5 < 5.0.10 and raise warnings

### Fixed

- backends libdnf5: don't call rpm.ts.closeDB()

[container builds]: https://git.sr.ht/~gotmax23/fedrq#container-images

## 0.8.0 - 2023-06-21 <a id='0.8.0'></a>

### Added

- add --version flag to CLI
- improve repo loading error handling ([#31])
- add CentOS 7 release configuration

### Changed

- `fedrq.config.Release.get_base` - allow omitting `config` arg.
  This previously emitted a deprecation warning ([`efc2828`][efc2828]).
- `ReleaseConfig` - make `repogs` a proper pydantic model field ([`d8cff5a`][d8cff5a]).

### Fixed

- fix Changelog URL in Python/PyPI metadata
- fix typo in help message for `--latest`. Contributed by Sandro (~penguinpee).
- backends - fix MissingBackendError message grammar


### New contributors

Thanks to Sandro (~penguinpee) for your first fedrq contribution!

[#31]: https://todo.sr.ht/~gotmax23/fedrq/31
[efc2828]: https://git.sr.ht/~gotmax23/fedrq/commit/efc2828b75b60fe325429ddff39f9082d7f03b1e
[d8cff5a]: https://git.sr.ht/~gotmax23/fedrq/commit/d8cff5af8696d4c1df8e90cf0d76f9dde09ae45c

## 0.7.1 - 2023-05-31 <a id='0.7.1'></a>

### Fixed

- libdnf5: fix downloadsize and size formatters compat.
  This change is needed to maintain compat after
  [rpm-software-management/dnf5#766fb3a][766fb3a].

[766fb3a]: https://github.com/rpm-software-management/dnf5/commit/766fb3ad8745e42e4d5b73417aa54898e2d0f89f

## 0.7.0 - 2023-05-30 <a id='0.7.0'></a>

### Highlighted examples

fedrq now has a Fedora ELN release configuration builtin!

You can preform simple queries

```
$ fedrq pkgs -b eln -F plainwithrepo ansible-core
ansible-core-2.15.0-2.eln126.noarch eln-appstream
ansible-core-2.15.0-2.eln126.src eln-appstream-source
```

or use more complex pipelines to determine how a package's build dependencies differ between ELN and Rawhide

```
$ comm -13 \
    <(fedrq pkgs -b eln -s -F requires ansible-core | sort -u) \
    <(fedrq pkgs -b rawhide -s -F requires ansible-core | sort -u)
git-core
glibc-all-langpacks
python3dist(bcrypt)
python3dist(passlib)
python3dist(pexpect)
python3dist(pytest)
python3dist(pytest-forked)
python3dist(pytest-mock)
python3dist(pytest-xdist)
python3dist(pywinrm)
python3dist(pyyaml)
python3-systemd
/usr/bin/python
```

(This difference is expected, as tests are disabled when `%rhel` is defined.)

fedrq also has a new `repolist` command to list enabled repos for a release.

```
$ fedrq repolist -b eln -r @no-crb
eln-baseos
eln-baseos-source
eln-appstream
eln-appstream-source
```


### Added

- add `local` and `local:...` branches to allow querying the enabled system repos in
- add `repolist` sucommand to display enabled repos
  the same way that plain `dnf repoquery` does.
- add Fedora ELN release configuration
- add/document `@koji` and `@koji-src` generic repo classes

---

- add EPEL 9 packages to the upstream gotmax23/copr and gotmax23/copr-dev repositories
- doc: add sig_policy.py to API examples
- doc: add dnf and libdnf5 intersphinx

### Changed

- docs: show full function signatures w/ annotations
- relicense CI files that are shared with tomcli to MIT
- libdnf5 backend: use `libdnf5.conf.Vars.detect_release()` when available (libdnf5 >= 5.0.10)
- backends: cache result of get_releasever()
- config: check that release `matcher`s match the entire `--branch` not just
  the beginning of it.

### Fixed

- doc: fix improper NEWS.md formatting
- doc: correct `smartcache` description in fedrq(5).
- libdnf5 backend: make the `BaseMaker.load_filelists()` method compatible with
  libdnf5 >= 5.0.12.
- packaging: remove remanent rpmautospec changelog file
- packaging: remove unneeded fedora-repos-rawhide BR

## 0.6.0 - 2023-04-06 <a id="0.6.0"></a>

### Changed

This release shouldn't introduce any backwards incompatibilities.

### Added

- add `@metaurl` repo class
- add builtin amazonlinux release configuration
- add builtin almalinux release configuration
- add @kojihub alias to the cXs (CentOS Stream) release configuration.
- add @compose-latest repo group to the the cXs (CentOS Stream) release
  configuration.
- add initial shell completions
- README: update links (by Benson Muite)
- README: expand section about installation with pip
- doc: create a mkdocs docsite at https://fedrq.gtmx.me
- doc: add dnf repoquery comparison

### Fixed

- releases: fix regression in @epel from the CentOS Stream release configurations.
  previously, `fedrq CMD -b cXs -r epel` resulted in an Exception.
- config: fix docstring typos and add links

### New contributors

Thank you to Benson Muite (~bvkcm) for improving the README and correcting
outdated information.

## 0.5.0 - 2023-03-18 <a id="0.5.0"></a>

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

## 0.4.1 - 2023-03-13 <a id="0.4.1"></a>

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


## 0.4.0 - 2023-02-21 <a id="0.4.0"></a>

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


## 0.3.0 - 2023-02-13 <a id="0.3.0"></a>

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


## 0.2.0 - 2023-01-14 <a id="0.2.0"></a>

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


## 0.1.0 - 2033-01-02 <a id="0.1.0"></a>

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


## 0.0.2 - 2022-12-20

- pyproject.toml: Add project.urls
- pyproject.toml: Change Development Status to Alpha
- Truncate RPM changelog
- Exclude rpmautospec `changelog` from sdist
- fedrq.spec: Workaround F36's old flit-core
- fedrq.spec: Remove unnecessary rpmdevtools BR
- Add fedrq-dev copr


## 0.0.1 - 2022-12-19

Initial release
