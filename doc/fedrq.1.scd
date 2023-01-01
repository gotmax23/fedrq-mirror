FEDRQ(1)

# NAME

fedrq - Simplified repository querying

# SYNOPSIS

*\[fedrq \| python -m fedrq]* *[query type]* [options...] *[package...]*

*\[fedrq \| python -m fedrq]* *[query type]* [options...] *\[-i \| --stdin ]*

*\[fedrq \| python -m fedrq]* *check-config* [--dump] [--debug]

# DESCRIPTION

fedrq is a tool to simplify querying the Fedora and EPEL repositories.

# SUBCOMMANDS

[[ check-config
:[ Verify fedrq configuration. Only has *--debug* and *--dump* to dump the
   config. *--dump* requires *tomli-w*.
|  pkgs
:  Find the packages that match a list of package specs. Allows
   *--whatprovides* like functionality with *--resolve-packages*.
|  subpkgs
:  Find the subpackages provided by a list of SRPMs.
   Doesn't have *--src*, because subpkgs aren't SRPMs.
|  whatenhances
:  Find the packages that Enhance *[package...]*
|  whatrecommends
:  Find the packages that Recommend *[package...]*
|  whatrequires
:  Find the packages that Require *[package...]*
|  whatsuggests
:  Find the packages that Suggest *[package...]*
|  whatsupplements
:  Find the packages that Supplement *[package...]*

# OPTIONS

## GLOBAL OPTIONS

*-h*, *--help*
	Show help message and quit.
	Can be used after a command to get more information it.

## SHARED OPTIONS

These options have the same meaning across multiple subcommands.

*-i*, *--stdin*
	Read package names from stdin. Cannot be used when passing postional
	*[packages...]*.
*-b*, *--branch* <branch name> (default: _rawhide_)
	Distribution release. This matches distgit branch names by convention.
	See BUILTIN RELEASES for the releases available out of the box. Extra
	configurations may be specified by the user.
*-r*, *--repo* <repo class> (default: _base_)
	Special repos may be specified for specific releases.
	See BUILTIN RELEASES for the releases available out of the box. Extra
	configurations may be specified by the user.
*-l*, *--latest* <integer|"all"> (default: _1_)
	How many package versions to show for a given _name.arch_.
	By default, only the latest is included.

	*NOTE*: *dnf repoquery* includes _all_ by default.
*-F*, *--formatter* <str> (default: _plain_)
	How the output should be formatted.
	This is similar to *dnf repoquery --qf* but more limited.
	All Package attributes from *dnf repoquery --querytags* are supported.
	Some custom formatters are also available. See FORMATTERS for a list.

	*NOTE*: *--formatter* is provisional and may be removed or have its
	interface changed in the near future.
	Give your feedback at https://todo.sr.ht/~gotmax23/fedrq/3.
*--debug*
	Enable debug logging. Useful for development or bug reporting.
*-P*, *--resolve-packages*
	Resolve the correct Package when given a virtual Provide or file path.
	For instance, /usr/bin/yt-dlp would resolve to yt-dlp.
*-A*, *--arch* <str>
	Only include packages that match this arch.
	This does not apply \--forcearch.

	*NOTE*: Unlike other tools, the -source repositories are always
	enabled. You need to filter out src packages if you don't want them in
	the output.
*-s*, *--src*
	Equivalent to *--arch=src*.

	*NOTE*: The semantics of this option are different than *dnf
	repoquery*'s version. Our *--arch* does not affect the way the input is
	handled. In dnf repoquery, *--arch=src* effectively disables querying
	for source packages that depend on a virtual Provide of the input
	packages, because arch filtering is applied when resolving the input
	packages' virtual Provides and files.
*-S*, *--notsrc*
	Equivalent to *--arch=notsrc*. This is a pseudo arch that does not exist
	in rpm. It includes noarch and the system architecture. It does NOT
	include multilib.
*-X*, *--exclude-subpackages* (only available for the *what\** subcommands)
	Filter out reverse dependencies that are built from the same source
	package as _any_ of the input packages. See the whatrequires EXAMPLES.

# FORMATTERS

Package attributes (nonexhaustive; see *dnf repoquery --querytags*):
- *-F name*: Show package names ++
(example line: *yt-dlp*)
- *-F arch*: Show package arches only ++
(example line : *noarch*)
- *-F repoid*: Show package's repo. ++
(example line: *updates-testing*)

Custom formatters:
- *-F na*: Show package _name_._arch_ ++
(example line: *yt-dlp.noarch*)
- *-F nv*: Show package _name_-_version_ ++
(example line: *yt-dlp-2022.11.11*)
- *-F nev*: Show package _name_-_epoch_:_version_ ++
(example line: *bind-32:9.18.8*)
- *-F source*: Package queries can include source and binary
  RPMs. The *source* formatter combines and deduplicates all of
  the source names.
  For example, if *python3-setuptools.noarch* is in the result,
  it'll become *python-setuptools*.
  If *python-setuptools.src* is also in the result, it'll become
  *python-setuptools*, but *python-setuptools* won't be
  duplicated in the output.
- *-F breakdown*: Only supported by *fedrq --whatrequires*.
  Shows a breakdown of runtime and buildtime dependencies.
- *-F json:[comma seperated list of Package attrs]*:
  Return an array of objects containing the specified Package attributes. The
  JSON output is formatted with _indent=2_. The output can be piped to jq.

# BUILTIN RELEASES

[- Name
:- Matcher (*--branch*)
:- Repo classes (*--repo*)
:- Special cases
|[ Fedora Rawhide
:[ rawhide
:[ base, buildroot
:[
|  Fedora stable and branched
:  fXX
:  base, testing, release, updates, testing-only
:  *release* only contains *fedora* and *fedora-source* (i.e. no *updates*)
|  EPEL
:  epelX
:  base, testing, testing-only
:  does not include any EL distribution
|  EPEL Next
:  epelX-next
:  base, testing, testing-only, next-base, next-testing, next-testing-only
:  *base*, *testing*, *testing-only* are supersets of the *epelX* equivalent.
   *next-base*, *next-testing*, and *next-testing-only* only contain epel-next.

## SPECIAL REPOS

The examples are from Fedora stable.

*base*
	Release repositories enabled by default in the distribution++
	(e.g. *fedora*, *fedora-source*, *updates*, *updates-source*)
*testing*
	Superset of *base* with *-testing* repos enabled.++
	(e.g. *fedora*, *fedora-source*, *updates*, *updates-source*,
	*updates-testing-source*)
*testing-only*
	Includes *-testing* repositories without *base*++
	(e.g. *updates-testing*, *updates-testing-source*)

*buildroot* (rawhide only)
	Koji buildroot repositories
	Buildroot repositories are available for stable Fedora releases, but
	they don't have corresponding source repos. This causes problems for
	fedrq, so those definitions are not available.

# FILES

## CONFIGURATION

*PYTHON_SITELIB/fedrq/data/\*.toml* Builtin configuration files. These should not be
modified directly but may be overridden or used as examples.

*/etc/fedrq/\*.toml* System wide configuration files. Has precedence over
builtin configuration files.

*~/.config/fedrq/\*.toml* User configuration files. Highest precedence

See fedrq(5) (TODO) for configuration file syntax.

# EXAMPLES

## pkgs

Find a package's runtime dependencies:
```
$ fedrq pkgs -S -F requires ansible
/usr/bin/python3
/usr/bin/bash
python(abi) = 3.11
(python3.11dist(ansible-core) >= 2.14.1 with python3.11dist(ansible-core) < 2.15)
```

Find a package's runtime dependencies:
```
$ fedrq pkgs -S -F requires ansible | fedrq pkgs -iSP
ansible-core-2.14.1-1.fc38.noarch
bash-5.2.9-3.fc38.x86_64
python3-3.11.1-1.fc38.x86_64
```

Find the package(s) that contain(s) a file on f35
```
$ fedrq pkgs -b f35 -P /usr/bin/ansible
ansible-2.9.27-4.fc35.noarch
ansible-core-2.12.10-1.fc35.noarch
```

Return a JSON object containing certain package attributes
```
fedrq pkgs scdoc -F json:name,evr,arch,files,requires
[
  {
    "name": "scdoc",
    "evr": "1.11.2-3.fc37",
    "arch": "x86_64",
    "requires": [
      "rtld(GNU_HASH)",
      "libc.so.6(GLIBC_2.34)(64bit)",
      "/usr/bin/pkg-config"
    ],
    "files": [
      "/usr/bin/scdoc",
      "/usr/lib/.build-id",
      "/usr/lib/.build-id/c1",
      "/usr/lib/.build-id/c1/62fcbc2f7d9b41ce409071b05905bdbfa6ffe7",
      "/usr/share/doc/scdoc",
      "/usr/share/doc/scdoc/README.md",
      "/usr/share/licenses/scdoc",
      "/usr/share/licenses/scdoc/COPYING",
      "/usr/share/man/man1/scdoc.1.gz",
      "/usr/share/man/man5/scdoc.5.gz",
      "/usr/share/pkgconfig/scdoc.pc"
    ]
  },
  {
    "name": "scdoc",
    "evr": "1.11.2-3.fc37",
    "arch": "src",
    "requires": [
      "make",
      "gcc",
      "sed"
    ],
    "files": [
      "/scdoc-1.11.2.tar.gz",
      "/scdoc.spec"
    ]
  }
]
```

## whatrequires

Find the packages that require another package, at buildtime or runtime:
```
$ fedrq whatrequires yt-dlp
audiotube-22.11-1.fc38.src
audiotube-22.11-1.fc38.x86_64
celluloid-0.24-4.fc38.x86_64
gpodder-3.11.0-1.fc37.noarch
media-downloader-2.7.0-2.fc38.x86_64
persepolis-3.2.0-11.fc37.noarch
video-downloader-0.10.12-1.fc38.noarch
yt-dlp-bash-completion-2022.11.11-1.fc38.noarch
yt-dlp-fish-completion-2022.11.11-1.fc38.noarch
yt-dlp-zsh-completion-2022.11.11-1.fc38.noarch
```

Find a package's reverse dependencies, excluding subpackages:
```
$ fedrq whatrequires -X yt-dlp
audiotube-22.11-1.fc38.src
audiotube-22.11-1.fc38.x86_64
celluloid-0.24-4.fc38.x86_64
gpodder-3.11.0-1.fc37.noarch
media-downloader-2.7.0-2.fc38.x86_64
persepolis-3.2.0-11.fc37.noarch
video-downloader-0.10.12-1.fc38.noarch
```

## subpkgs

Find an epel9 SRPM's subpackages
```
$ fedrq subpkgs -b epel9 -F na epel-release
epel-next-release.noarch
epel-release.noarch
```

Find the components that would be directly affected by the removal of pcre:
```
$ fedrq subpkgs pcre | fedrq whatrequires -iX -F source
ClanLib
Thunar
adanaxisgpl
aide
[...]
xgrep
xmlcopyeditor
yara
zsh
```

# AUTHOR

fedrq is maintained by Maxwell G <gotmax@e.email>.
See https://sr.ht/~gotmax23/fedrq/ for more information about fedrq.

# SEE ALSO

fedrq(5), dnf(1)
