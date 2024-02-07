FEDRQ(1)

# NAME

fedrq - Simplified repository querying

# SYNOPSIS

*\[fedrq \| python -m fedrq]* *[query type]* [options...] *[package...]*

*\[fedrq \| python -m fedrq]* *[query type]* [options...] *\[-i \| --stdin ]*

*\[fedrq \| python -m fedrq]* *check-config* [--dump] [--debug]

*\[fedrq \| python -m fedrq]* *formatters* [formatters options...]

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
|  wr
:  Alias for _whatrequires_
|  whatrequires-src
:  Find the packages Require the subpackages of *[package...]*.
   *[package...]* must be source package(s).
|  wrsrc
:  Alias for _whatrequires-src_
|  whatsuggests
:  Find the packages that Suggest *[package...]*
|  whatsupplements
:  Find the packages that Supplement *[package...]*
|  make-cache
:  Load the repodata for the current branch/repo config
|  download
:  Download an RPM from the repos. No GPG checking is performed.
|  download-spec
:  Download an (S)RPM and extract its specfile. No GPG checking is performed.

# OPTIONS

## GLOBAL OPTIONS

*-h*, *--help*
	Show help message and quit.
	Can be used after a command to get more information it.

## SHARED OPTIONS

These options have the same meaning across multiple subcommands.

*-i*, *--stdin*
	Read package names from stdin. Cannot be used when passing positional
	*[packages...]*.
*-b*, *--branch* <branch name> (default: _rawhide_)
	Distribution release. This matches distgit branch names by convention.
	See BUILTIN RELEASES for the releases available out of the box. Extra
	configurations may be specified by the user. The chosen release impacts
	what the releasever will be set to and which repositories will be
	enabled by default.
*-r*, *--repo* <repo class> (default: _@base_)
	Enable <repo class> and disable all others for this operation. <repo
	class> can be a standard repoid that's configured in /etc/yum.repos.d in
	a ReleaseConfig's *defpaths* (see fedrq(5)). In addition, release
	specifc repo groups and generic release class macros (e.g. *@copr*) are
	accepted. When *--repo* isn't specified, the repositories in a Release's
	*@base* repo group are selected. See REPO CLASSES for more information.
*-e*, *--enablerepo* <repo class>
	Enable certain repositories for this operation. All repositories in the
	system configuration and any fedrq repo classes are accepted. Can be
	specified multiple times. Accepts comma separated values. See REPO
	CLASSES.
*-l*, *--latest* <integer|"all"> (default: _1_)
	How many package versions to show for a given _name.arch_.
	By default, only the latest is included.

	*NOTE*: *dnf repoquery* includes _all_ by default.
*-F*, *--formatter* <str> (default: _plain_)
	How the output should be formatted.
	This is similar to *dnf repoquery --qf* but more limited.
	All Package attributes from *dnf repoquery --querytags* are supported.
	Some custom formatters are also available. See FORMATTERS for a list.
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
*--forcearch* <str>
	Query a foreign architecture's repositories
*-B*, *--backend* <dnf|libdnf5>
	Which package manager backend to use.
	By default, fedrq uses dnf and falls back to libdnf5. Set *-B* /
	*--backend* to make an explicit choice.
	If you explicitly choose a backend whose dependencies are not met on
	your system, fedrq will not fallback to another one.
*-L*, *--filelists* <always|auto|never> (default: _auto_)
	Whether to load filelists. By default, filelists are only loaded when
	using the files formatter (i.e. *-F files* or *-F json:files*). This
	only applies when using the libdnf5 backend, which doesn't load
	filelists by default to save memory and bandwidth. dnf4 always loads
	filelists.

## whatrequires, whatrecommends, whatsuggests

*-X*, *--exclude-subpackages*
	Filter out reverse dependencies that are built from the same source
	package as _any_ of the input packages. See the whatrequires EXAMPLES.


## subpkgs

*-M*, *--match* <pattern> (can be repeated to match against multiple patterns)
	Only show subpackages whose name matches this string. Glob
	patterns are permitted. When specified multiple times, _any_
	match is included.

## download and download-spec

*-o*, *--destdir* <path>
	Directory in which to download/extract files

## formatters

The *formatters* subcommand lists available formatters.
By default, all available formatters are shown,
but they can be filtered by passing one or more of the following options.

*--attrs*, *--only-attrs*
	Only list package attributes
*--formatters*, *--only-formatters*
	Only list regular formatters
*--special-formatters*, *--only-special-formatters*
	Only list special formatters
	(i.e., formatters that accept their own arguments)

# FORMATTERS

## Package attributes

This list is nonexhaustive. See *fedrq formatters --attrs*.

*-F* name
	Show package names ++
	(example line: *yt-dlp*)
*-F* arch
	Show package arches only ++
	(example line : *noarch*)
*-F* repoid
	Show package's repo. ++
	(example line: *updates-testing*)

## Regular formatters

*-F* na
	Show package _name_._arch_ ++
	(example line: *yt-dlp.noarch*)
*-F* nv
	Show package _name_-_version_ ++
	(example line: *yt-dlp-2022.11.11*)
*-F* nev
	Show package _name_-_epoch_:_version_ ++
	(example line: *bind-32:9.18.8*)
*-F* source
	Package queries can include source and binary
	RPMs. The *source* formatter combines and deduplicates all of
	the source names.
	For example, if *python3-setuptools.noarch* is in the result,
	it'll become *python-setuptools*.
	If *python-setuptools.src* is also in the result, it'll become
	*python-setuptools*, but *python-setuptools* won't be
	duplicated in the output.
*-F* breakdown
	Only supported by *fedrq --whatrequires*.
	Shows a breakdown of runtime and buildtime dependencies.

## Special formatters

"Special formatters" accept arguments.

*-F* json:_[comma separated list of Package attrs]_
	Return an array of objects containing the specified Package attributes.
	The JSON output is formatted with _indent=2_.
	The output can be piped to jq.
*-F* line:_[comma separated list of Package attrs]_
	Return the specified package attributes on a single line.++
	*NOTE*: The attributes provided must fit on one line. Attributes such as
	_files_ or _requires_ that contain a list of items are not supported by
	the *line* formatter.
	See *-F* multiline for that usecase.
*-F* multiline:_[single line attribute]_,_[multiline attribute]_
	Display two package attributes together.++
	(example call: -F multiline:name,files)++
	(example line: _yt-dlp : /usr/bin/yt-dlp_)
*-F* plainwithrepo
	Show default format and repoid separated by space: ++
	(example line: *yt-dlp-2023.01.06-2.fc38.noarch rawhide*)
*-F* nevrr
	Alias to plainwithrepo formatter.
*-F* requiresmatch:_[comma- or semicolon-separated list of packages]_
	List the Requires of *[package ...]* that resolve to the list of
	packages provided to requiresmatch.
	For example, *python3dist(ansible-core)* resolves to
	requiresmatch:_ansible-core_.
*-F* rm:_[comma- or semicolon-separated list of packages]_
	Alias for *-F* requiresmatch
*-F* na-requiresmatch:_[comma- or semicolon-separated list of packages]_
	Combine the *-F* na and *-F* requiresmatch on a single line.
	See the whatrequires EXAMPLES for usage.
*-F* narm:_[comma- or semicolon-separated list of packages]_
	Shortcut for *-F* na-requiresmatch

There are also _requiresmatch-src_ / _rmsrc_ and _na-requiresmatch_ / _narmsrc_
formatters that work similarly to their non-src conterparts, expect they take a
list of source packages.
The list of source packages is converted into a list of binary packages
(like the *subpkgs* subcommand) and then processed in the same way.
If, say, a source package named *foo* has *foo*, *foo-devel*, and *foo-static*
subpackages, *-F* _rmsrc:foo_ is equivalent to *-F* _rm:foo,foo-devel,foo-static_

# REPO CLASSES

The following generic repo class macros are available for all releases:

*@file:[url or local path]*
	Load a .repo file from a local path or a url. Repositories with
	*enabled=0* won't be loaded unless they are enabled explicitly with
	*--enablerepo*.
*@baseurl:[url]*
	Load a repository from *url*. gpgcheck will be disabled.
*@baseurl:[url],[gpgkey]*
	Load a repository from *url* and set its gpgkey to *gpgkey*
*@copr:[user/name]* or *@copr:[@group/name]*
	Load a Copr repository. The Copr instance defaults to
	*https://copr.fedoraproject.org* but may be configured in fedrq's
	configuration. *copr_chroot_fmt* must be specifced in the selected
	branch's release configuration for this repo class to work. This is
	configured for the builtin releases.
*@copr:[user/name@copr_baseurl]* or *@copr:[@group/name@copr_baseurl]*
	The *@copr* repo class also accepts a custom Copr instance.
	Append *@* and a url.
*@source-repos*
	Enable the corresponding -source repos of the currently enabled
	repositories
*@base* or *base* or other group
	The default repositories for a release specified in a ReleaseConfig's
	*defs.base*. Any other repo group specified in a release's is accepted,
	with or without the *@*. See SPECIAL REPOS for which repo groups are
	available for each release.
*@repo:[key]* or *key* (fallback)
	Accepts any repoid available in the system configuration or a .repo file
	specific in the current ReleaseConfig's *defpaths*. If *key* is the name
	of a release's repo group (see above), that will be enabled instead.

The following generic repo class macros are available for Fedora releases:

*@koji:[key]*
	Load the repositories for a koji.fedoraproject.org tag. ++
	Example: *@koji:f39-build-side-XXXX*
*@koji-src:[key]*
	Load the source repositories for a koji.fedoraproject.org tag.
	It does not seem that Fedora Koji provides source repositories
	for tags other than *rawhide* and *eln-build*.
	For rawhide, see the preconfigured *@buildroot* repository group.



# BUILTIN RELEASES

[- Name
:- Matcher (*--branch*)
:- Release repo groups (*--repo*)
:- Special cases
|[ Fedora Rawhide
:[ rawhide
:[ *@base*, *@buildroot*
:[
|  Fedora stable and branched
:  fXX
:  *@base*, *@testing*, *@release*, *@updates*, *@testing-only*
:  *@release* only contains fedora and fedora-source (i.e. no updates)
|  EPEL
:  epelX
:  *@base*, *@testing*, *@testing-only*
:  does not include any EL distribution
|  EPEL Next
:  epelX-next
:  *@base*, *@testing*, *@testing-only*, *@next-base*, *@next-testing*,
   *@next-testing-only*
:  *@base*, *@testing*, and *@testing-only* are supersets of the _epelX_
   equivalent.
   *@next-base*, *@next-testing*, and *@next-testing-only* only contain epel-next.
|  CentOS 7
:  c7
:  *@base*
:  
|  CentOS Stream
:  cXs
:  *@base*, *@epel*, *@no-crb*, *@compose-latest*
:  *@epel* contains epel, epel-next, and crb.
   *@no-crb* contains base minus the crb repo.
|  CentOS Stream 8 (legacy)
:  c8s
:  *@base*, *@epel*, *@no-powertools*, *@compose-latest*
:  *@epel* contains epel, epel-next, baseos, appstream, and powertools.
   *@no-powertools* contains *@base* minus the powertools repo.
|  Almalinux
:  alX
:  *@base*, *@epel*, *@no-crb*
:  *@base* always includes crb. *@epel* contains *@base* along with the EPEL
   repository. *@no-crb* contains *@base* minus the crb repository.
|  Almalinux 8 (Legacy)
:  al8
:  @*base*, *@epel*, *@no-powertools*
:  *@base* always includes powertools. *@epel* contains *@base* along with the EPEL
   repository. *@no-powertools* contains *@base* minus the powertools repository.
|  UBI
:  ubiX
:  *@base*, *@epel*, *@no-crb*
:  
|  Oracle Linux 8 and 9
:  ol8 / ol9
:  *@base*, *@epel*, *@no-crb*, *@extra*
:  *@extra* contains the distro_builder and UEK repos
|  Rocky Linux 8
:  rl8
:  *@base*, *@epel*, *@no-powertools*
:  
|  Rocky Linux 9+
:  rl9
:  *@base*, *@epel*, *@no-crb*
:  
|  Amazon Linux
:  amazon2023
:  *@base*
: 
|  Fedora ELN
:  eln
:  *@base*, *@no-crb*, *@buildroot*
: 
|  Default local system repositories
:  local
:  N/A
:  This uses the default repositories with *enabled=1* in /etc/yum.repos.d and
   and the system's releasever.
|  Default local system repositories with a different releasever
:  local:[releasever]
:  N/A
:  This uses the default repositories with *enabled=1* in /etc/yum.repos.d and
   and a custom releasever.

; local should always be last in the above table

## SPECIAL REPOS


*@base*
	Release repositories enabled by default in the distribution++
	(e.g. *fedora*, *fedora-source*, *updates*, *updates-source* for Fedora
	stable)
*@testing*
	Superset of *base* with *-testing* repos enabled.++
	(e.g. *fedora*, *fedora-source*, *updates*, *updates-source*,
	*updates-testing-source* for Fedora stable)
*@testing-only*
	Includes *-testing* repositories without *base*++
	(e.g. *updates-testing*, *updates-testing-source* for Fedora stable)

*@buildroot* (rawhide only)
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

See fedrq(5) for configuration file syntax.

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

Resolve a package's runtime dependencies:
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

Return a JSON object containing certain package attributes:
```
$ fedrq pkgs scdoc -F json:name,evr,arch,files,requires
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

Show packages' name, evr, arch, and reponame with each package on a single line:
```
$ fedrq pkgs ansible ansible-core -F line:name,evr,arch,reponame
ansible : 7.2.0-1.fc38 : noarch : rawhide
ansible : 7.2.0-1.fc38 : src : rawhide-source
ansible-core : 2.14.2-1.fc38 : noarch : rawhide
ansible-core : 2.14.2-1.fc38 : src : rawhide-source
```

Incorrect usage of the *line* filter:

```
$ fedrq pkgs ansible ansible-core -F line:name,evr,files
ERROR: 'line' FormatterError: invalid argument 'files'
See fedrq(1) for more information about formatters.
```

(*files* cannot fit on a single line)

Find the latest version of `fedrq` available in the gotmax23/fedrq-dev copr:
```
$ fedrq pkgs -F nevrr -b f36 -r @copr:gotmax23/fedrq-dev fedrq
fedrq-0.4.1^25.20230318.76d7910-1.fc36.noarch copr:copr.fedorainfracloud.org:gotmax23:fedrq-dev
fedrq-0.4.1^25.20230318.76d7910-1.fc36.src copr:copr.fedorainfracloud.org:gotmax23:fedrq-dev
```


In a single query, print the Requires of more than one package:
```
$ fedrq pkgs -F requires ansible-core.src yt-dlp.noarch
make
python3-devel
python3dist(packaging)
[...]
/usr/bin/python3
python3.12dist(requests)
python3.12dist(urllib3)
[...]
```

In a single query, print the Requires of more than one package, qualified by
package name:
```
$ fedrq pkgs -F multiline:name,requires ansible-core.src yt-dlp.noarch
ansible-core : make
ansible-core : python3-devel
ansible-core : python3dist(packaging)
[...]
yt-dlp : /usr/bin/python3
yt-dlp : python3.12dist(requests)
yt-dlp : python3.12dist(urllib3)
[...]
```


## whatrequires

Find the packages that require another package, at buildtime or runtime:
```
$ fedrq whatrequires yt-dlp
audiotube-24.01.95-1.fc40.src
audiotube-24.01.95-1.fc40.x86_64
celluloid-0.26-1.fc40.x86_64
gpodder-3.11.4-4.fc40.noarch
lollypop-1.4.37-7.fc40.noarch
media-downloader-4.2.0-4.fc40.x86_64
persepolis-3.2.0-16.fc40.noarch
video-downloader-0.12.10-3.fc40.noarch
yt-dlp-bash-completion-2023.12.30-2.fc40.noarch
yt-dlp-fish-completion-2023.12.30-2.fc40.noarch
yt-dlp-zsh-completion-2023.12.30-2.fc40.noarch
```

Find a package's reverse dependencies, excluding subpackages:
```
$ fedrq whatrequires -X yt-dlp
audiotube-24.01.95-1.fc40.src
audiotube-24.01.95-1.fc40.x86_64
celluloid-0.26-1.fc40.x86_64
gpodder-3.11.4-4.fc40.noarch
lollypop-1.4.37-7.fc40.noarch
media-downloader-4.2.0-4.fc40.x86_64
persepolis-3.2.0-16.fc40.noarch
video-downloader-0.12.10-3.fc40.noarch
```

Find the packages that require another package, at buildtime or runtime and show
which package spec it depends on.
```
$ fedrq whatrequires -F multiline:plain,rm:ansible-core: ansible-core
ansible-9.2.0-1.fc40.noarch : (python3.12dist(ansible-core) >= 2.16.3 with python3.12dist(ansible-core) < 2.17)
ansible-9.2.0-1.fc40.src : (python3dist(ansible-core) >= 2.16.3 with python3dist(ansible-core) < 2.17)
ansible-bender-0.10.1-5.fc40.noarch : (ansible-core or ansible)
ansible-collection-ansible-netcommon-6.0.0-3.fc40.noarch : (ansible-core or (ansible < 2.10.0 with ansible >= 2.9.10))
[...]
```

Shortcut for the above:
```
$ fedrq whatrequires -F narm:ansible-core ansible-core
ansible.noarch : (python3.12dist(ansible-core) >= 2.16.3 with python3.12dist(ansible-core) < 2.17)
ansible.src : (python3dist(ansible-core) >= 2.16.3 with python3dist(ansible-core) < 2.17)
ansible-bender.noarch : (ansible-core or ansible)
ansible-collection-ansible-netcommon.noarch : (ansible-core or (ansible < 2.10.0 with ansible >= 2.9.10))
[...]
```

## subpkgs

Find an epel9 SRPM's subpackages
```
$ fedrq subpkgs -b epel9 -F na epel-release
epel-next-release.noarch
epel-release.noarch
```


## whatrequires-src / wrsrc (alias)

Find the components that would be directly affected by the removal of pcre:
```
$ fedrq whatrequires-src -X -F source pcre
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

Find the packages the need to be rebuilt when libindi's .so name is bumped:
```
$ fedrq whatrequires-src -X -F source libindi
indi-3rdparty-drivers
indi-3rdparty-libraries
kstars
phd2
```


# AUTHOR

fedrq is maintained by Maxwell G <maxwell@gtmx.me>.
See https://fedrq.gtmx.me/ for more information about fedrq.

# SEE ALSO

fedrq(5), dnf(1)
