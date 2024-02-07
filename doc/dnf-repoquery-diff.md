<!--
Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>

SPDX-License-Identifier: GPL-2.0-or-later
-->

# Differences between fedrq and dnf repoquery

While fedrq and `dnf repoquery` have similar functionality,
their respective interfaces have some key differences.
The author believes these differences make fedrq more powerful and more user
friendly, but experienced `dnf repoquery` users should keep them in mind.

## Default repositories

By default, `dnf repoquery` reads the system configuration and queries the
repositories with `enabled=1` and nothing more.
fedrq, on the other hand, behaves more like `fedpkg`.
Queries default to `rawhide` and enable the `rawhide` and `rawhide-source`
repositories.
This can be changed using the `-b` / `--branch` flags on the CLI or permanently
with the `default_branch` option in the configuration.
See the [BUILTIN RELEASES](fedrq1.md/#builtin-releases) section of `man fedrq`
for valid `--branch` options.
Users can of course configure their own custom release profiles.
You can use the pseudo `-b local` release which uses the default repositories
with `enabled=1` in /etc/yum.repos.d and the system's releasever.

## Source repositories

fedrq enables source repositories by default in its builtin release configs.
While users are free to include whichever repositories they wish in their local
configurations,
commands such as `fedrq subpkgs` and `fedrq whatrequires-src` will not work
properly without source repositories enabled.

## Release configurations

Release configurations contain three main parts:

- `version` - this is a regex of matching branches. For example, the repository
  definition for the Fedora branches configuration is `^f(\d{2})$`. Therefore,
  `--branch f37` and `--branch f36` will match this configuration and the
  `$releasever` will
  be set to `37` and `36`, respectively.
- `defs` - this is a mapping of profile names to a list of repository IDs. Each
  release has a `base` profile which is the default profile for that release.
  Others can be selected with `-r` / `--repo`.

fedrq can read configuration from .repo files located outside of
`/etc/yum.repos.d/` if they're specified in the release's `defpaths`.

The configuration syntax is described more in [`man 5 fedrq`](fedrq5.md).

## --latest

`fedrq` applies `--latest=1` by default. This means that only one package
version will be shown for each architecture. `dnf repoquery`, on the other
hand, shows everything. You can pass `--latest=all` to fedrq to change this
behavior.

## --repo and --enablerepo

fedrq also supports these options, but they have additional functionality.
In addition `repoid`s, these options accept release-specific group names (these
are configured in a release's `defs` as explained above), and generic repo
classes.

For example, you can pass `-b f37 -r @copr:gotmax23/fedrq` to query *only* the
`fedora-37` chroot's repositories. You can pass `-b f37 --enablerepo
@copr:gotmax23/fedrq` if you want to enable that copr's repository on top of
the base repositories.

See the [REPO CLASSES](fedrq1.md/#repo-classes) section of `man fedrq` for more
information.

## Subcommands

fedrq's CLI interface is split into subcommands unlike `dnf repoquery` which
relies on flags.

See [`man fedrq`](fedrq1.md) for an in depth orientation of fedrq's CLI
interface.

## `--requires`, `--provides`, and other package attributes

`dnf repoquery` has flags such as `--requires` and `--provides` to determine
certain package attributes.
`fedrq` supports these operations via the `pkgs` subcommand and
the `-F` / `--formatter` flag.

<table>
    <tb>
        <tr>
            <td>dnf repoquery --requires PACKAGE</td>
            <td>fedrq pkgs -F requires PACKAGE</td>
        </tr>
        <tr>
            <td>dnf repoquery --provides PACKAGE</td>
            <td>fedrq pkgs -F provides PACKAGE</td>
        </tr>
        <tr>
            <td>dnf repoquery --qf "%{name}\n" PACKAGE</td>
            <td>fedrq pkgs -F name PACKAGE</td>
        </tr>
    </tb>
</table>
