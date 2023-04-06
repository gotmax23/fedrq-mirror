FEDRQ(5)

# NAME

fedrq - Simplified repository querying

# SYNTAX

fedrq uses the TOML syntax for its configuration files.


# DIRECTORIES

*PYTHON_SITELIB/fedrq/data/\*.toml* Builtin configuration files. These should not be
modified directly but may be overridden or used as examples.

*/etc/fedrq/\*.toml* System wide configuration files. Has precedence over
builtin configuration files.

*~/.config/fedrq/\*.toml* User configuration files. Highest precedence

Top level options and releases in the *[releases]* table can be redefined
by creating a configuration file with higher precedence.

# OPTIONS

*default_branch* <str> (default: _rawhide_)
	What branch to query by default when *-b*/*--branch* is not specified.
*smartcache* <bool> (default: _true_)
	Different releases have different _releasever_\s.
	Switching the releasever clears the dnf cache.
	When *smartcache* is _true_\, fedrq sets *base.conf.cachedir* to
	_/var/tmp/USER/BRANCH_ when changing the releasever.
	The system cache is used if the requested branch's releasever is the
	same as the system's releasever.
*releases* <dict[str, ReleaseConfig]>
	Keys are a friendly name for the distribution.
	RELEASE specifies the format for the values.
*filelists* <always|never|auto> (default: _auto_)
	See *--filelists* in fedrq(1)
*backend* <dnf|libdnf5>
	See *--backend* in fedrq(1)

## RELEASE

*defs* <dict[str, list[str]]>
	Keys are repo types to pass to *-r*/*--repo*. Each repo type takes a
	list of repo ids to query. All releases MUST have a _base_ def.
	```
	 defs.base = ["rawhide", "rawhide-source"]
	 # These are defined in rawhide-buildroot.repo which
	 # is referenced in `releases.rawhide.defpaths`.
	 defs.buildroot = ["fedrq-koji-rawhide", "fedrq-koji-rawhide-source"]
	```
*matcher* <regex>
	Python regex to match *-b*/*--branch* names against. Regexes must have
	one capture group to use as the branch's releasever. ++
	(example: *matcher = "^(rawhide)$"* or *matcher = "^f(\\d{2})$"*)
*defpaths* <list of paths> (default: _[]_)
	List of .repo files to load. All repo(s) MUST have _enabled=0_.
	fedrq will enable the appropriate repos that are specified in *defs* for
	the user's requested repo type.
	Paths can be relative or absolute.
	Relative paths are searched for in the following directories:
	- PYTHON_SITELIB/fedrq/data/repos/
	- /etc/fedrq/repos/
	- ~/.config/fedrq/repos/

*copr_chroot_fmt* <str> (e.g. _fedora-{version}_ or _epel-{version}_ or
_fedora-rawhide_)
	Name of the Copr chroot that corresponds to this release.
	_{version}_ will be replaced with the releasever.
*system_repos* <bool> (default: _true_)
	Whether to load the system repository configuration.
	If all of the repository definitions are specified in *defpaths*,
	then it's a good idea to turn this off to avoid conflicts
	(if e.g. the system configuration defines the same repository IDs)
	and save time.

## EXAMPLES


Here are some example configuration snippets.

Configuring RPMFusion:

1. Install the applicable rpmfusion release packages.
```
$ sudo dnf install \
	rpmfusion-free-release rpmfusion-free-release-rawhide \
	rpmfusion-nonfree-release rpmfusion-nonfree-release-rawhide \
```

2. Create a configuration
```
# ~/.config/fedrq/rpmfusion.toml

# `releases.rawhide` exists in the default configuration.
# fedrq will merge the extras keys in the `defs` table with the default config.
[releases.rawhide]
# Note that the corresponding -source repositories are enabled.
# All fedrq release defs must have these to ensure all functionality works
# properly (notably subpkgs and whatrequires-src).

# `fedrq CMD -b rawhide -r fusion-free` will enable the following two
# repositories and nothing more.
#
# Use `fedrq CMD -b rawhide -e fusion-free` to enable these repositories
# *in addition* to the default rawhide repositories.
defs.fusion-free = [
    "rpmfusion-free-rawhide", "rpmfusion-free-rawhide-source",
]
defs.fusion-nonfree-only = [
    "rpmfusion-nonfree-rawhide", "rpmfusion-nonfree-rawhide-source"
]
# Enable everything
defs.rpmfusion = [
    # Include all repositories in defs.rpmfusion-free above
    "@fusion-free",
    # Include all repositories in defs.rpmfusion-nonfree-only above.
    "@fusion-nonfree-only",
]
# Make sure that fedrq loads repositories from the system configuration.
# This is the default but better to explicitly specify.
system_repos = true

[releases.branched]
defs.fusion-free = [
    "rpmfusion-free", "rpmfusion-free-source",
    "rpmfusion-free-updates", "rpmfusion-free-updates-source"
]
defs.fusion-nonfree-only = [
    "rpmfusion-nonfree", "rpmfusion-nonfree-source",
    "rpmfusion-nonfree-updates", "rpmfusion-nonfree-updates-source"
]
defs.rpmfusion = [
    "@fusion-free",
    "@fusion-nonfree-only",
]

system_repos = true
```

# AUTHOR

fedrq is maintained by Maxwell G <maxwell@gtmx.me>.
See https://fedrq.gtmx.me/ for more information about fedrq.

# SEE ALSO

fedrq(1)
