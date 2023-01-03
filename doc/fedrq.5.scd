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

*system_repos* <bool> (default: _true_)
	Whether to load the system repository configuration.
	If all of the repository definitions are specified in *defpaths*,
	then it's a good idea to turn this off to avoid conflicts
	(if e.g. the system configuration defines the same repository IDs)
	and save time.
