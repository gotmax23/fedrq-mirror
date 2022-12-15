FEDRQ(1)

# NAME

fedrq - Simplified repository querying

# SYNOPSIS

fedrq [subcommand] [options...] [package...]

fedrq check-config [--dump] [--debug]

python -m fedrq [subcommand] [options...] [package...]

python -m fedrq check-config [--dump] [--debug]


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

*-b*, *--branch* <branch name> (default: _rawhide_)
	Distribution release. This matches distgit branch names by convention.
	See BUILTIN RELEASES for the releases available out of the box. Extra
	configurations may be specified by the user.
*-r*, *--repo* <repo class> (default: _base_)
	Special repos may be specified for specific releases.
	See BUILTIN RELEASES for the releases available out of the box. Extra
	configurations may be specified by the user.
*-l*, *--latest* <int|all> (default: 1)
	How many package versions to show for a given _name.arch_.
	By default, only the latest is included. ++
	*NOTE*: *dnf repoquery* includes _all_ by default.
*-F*, *--formatter* <str> (default: _plain_)
	How the output should be formatted.
	This is similar to *dnf repoquery --qf* but more limited.
	Any Package attribute from *dnf repoquery --querytags* is supported
	here. Some custom formatters are also available. Examples:

	Package attributes (nonexhaustive):
		- *-F name*: Show package names
		  (example line: *yt-dlp*)
		- *-F arch*: Show package arches only.
		  (example line : *noarch*)
		- *-F repoid*: Show package source repo.
		  (example line: *updates-testing*)

	Custom formatters:
		- *-F na*: Show package _name_._arch_
		  (example line: *yt-dlp.noarch*)
		- *-F nv*: Show package _name_-_version_
		  (example line: *yt-dlp-2022.11.11*)
		- *-F nev*: Show package _name_-_epoch_:_version_
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

	*NOTE*: *--formatter* is provisional and may be removed or have its
	interface changed in the near future.
	Give your feedback at https://todo.sr.ht/~gotmax23/fedrq/3.
*--debug*
	Enable debug logging. Useful for development or bug reporting.
*-P*, *--resolve-packages*
	Resolve the correct Package when given a virtual Provide or file path.
	For instance, /usr/bin/yt-dlp would resolve to yt-dlp.
*-A*, *--arch* <str>
	Only include packages that match this arch. This does not apply
	\--forcearch.
	*NOTE*: Unlike other tools, the -source repositories are always enabled.
	You need to filter out src packages if you don't want them in the query.
*--src*
	Equivalent to *--arch=src*.
	*NOTE*: The semantics of this option are different than *dnf
	repoquery*'s version. Our *--arch* does not affect the way the input is
	handled. In dnf repoquery, *--arch=src* effectively disables querying
	for source packages that depend on a virtual Provide of the input
	packages, because arch filtering is applied when resolving the input
	packages' virtual Provides and files.
*--notsrc*
	Equivalent to *--arch=notsrc*. This is a pseudo arch that does not exist
	in rpm. It includes noarch and the system architecture. It does NOT
	include multilib.

# BUILTIN RELEASES

[- Name
:- Matcher (*--branch*)
:- Repo classes (*--repo*)
:- Special cases
|[ Fedora Rawhide
:[ rawhide
:[ base, buildroot
:[
|  Fedora stable/branched
:  fXX
:  base, testing, release, updates, testing-only
:  *release* only contains *fedora* and *fedora-source* (i.e. no *updates*)
|  EPEL
:  epelX
:  base, testing, testing-only
:  does not include any EL distribution
|  EPEL Next
:  epelX-next
:  base, testing, next-only, next-testing-only
:  *base* and *testing* are supersets of *epelX*.

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

TODO

# AUTHOR

fedrq is maintained by Maxwell G <gotmax@e.email>.
See https://sr.ht/~gotmax23/fedrq/ for more information about fedrq.

# SEE ALSO

fedrq(5), dnf(1)
