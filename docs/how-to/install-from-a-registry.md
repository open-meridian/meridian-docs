# Install a plugin from a registry

A plugin listed in the platform's Community registry, such as
[`open-meridian/snaptrade`](https://open-meridian.com/plugins/open-meridian/snaptrade), is
installed into your deployment's own registry by digest, verified, and then launched the way any
version is. What the registries are, and what each checks, is in
[Registries](../concepts/registries.md) and
[Who checks a plugin](../concepts/plan-your-deployment.md#who-checks-a-plugin).

Installing a plugin from a registry is covered by the platform's Terms of Service, section 9,
[Plugins and registries](https://open-meridian.com/terms#plugins-and-registries).

You need to be a deployment admin.

Through an agent, the same is done with core's tools, at the same level and with a note on every
act: see [The Plugins page's registries](../api/core-tools.md#the-plugins-pages-registries).

## Find it

On the dashboard's **Plugins** page, `/admin/plugins/versions`, **Browse** lists the catalogue
your deployment last pulled: one line per listing, with its registry, latest version, roles,
whether its floor fits your deployment, stars and installs ("Fewer than three deployments" below
three). Search by words, or filter by registry and role.

A listing's page, `/admin/plugins/registry/<namespace>/<plugin>`, has three tabs:
**Overview** (the build's repository, commit, tag and signing key; the floor against your
deployment; the vendor's attributes and support contact, marked as stated by the vendor),
**Documentation** (the version's Reference; its sections arrive, verified, with the install) and **Versions** (pulled and withdrawn marked).

The catalogue is pulled hourly; **Pull now** on the **Registries** tab pulls it at once.

## Install it

**Install** on the listing's page opens a sheet. Read its first step and choose **Continue**. The
sheet then shows the roles the version asks for, the floor's result, that it is verified at the
install, and the **Report plugin usage** setting, with a note to write and the act at its foot.
Installing pulls the image and its attachments by digest into your deployment's registry, and the conductor verifies them against the platform's keys your chart
carries. A version failing a check is refused, naming the check. Install launches nothing.

The version is recorded under its listing, as `meridian plugin list` shows it. Launch it as any
version, by that name, approving its roles (see
[Launching, and approval](../concepts/plugins.md#launching-and-approval)):

```bash
meridian plugin launch open-meridian/snaptrade <version> --instance snaptrade
```

For a Verified version you can approve no role beyond those its review approved. Each launch of a
registry version is verified again.

An instance already running a local version of the same plugin is offered **Move to this listing**
in the same sheet. The move is checked as an update, keeps the instance's ID, and is recorded.

## From the command line

[`meridian plugin install`](../api/cli.md#meridian-plugin-install), from
CLI 0.1.51, does the same through the session `meridian connect` keeps, as
the deployment admin, and launches nothing:

```bash
meridian plugin install open-meridian/snaptrade@0.20.0 --note "the family office's brokerage"
meridian plugin install open-meridian/snaptrade --note "the newest offered, as Browse shows it"
```

## A starter pack { #a-starter-pack }

A **starter pack** is a curated list of plugins for an asset class: its
members, each installed as its own version, never one merged plugin. The
platform publishes five, by `open-meridian`: `equities-options`, `fx`,
`crypto`, `event-contracts` and `multi-asset`. Each pack's page on the
platform, under [its plugins](https://open-meridian.com/plugins), lists
its members and which are preselected. From contract 28 the deployment
installs a pack and keeps it, at the dashboard or with the CLI.

**Install it.** On **Browse**, switch from **Plugins** to **Starter
packs**: one line a pack, with its title, asset classes, members and its
state here ("Not installed", or "Installed: 7 of 9 members"). **Install**
opens the sheet, **Install {pack title}**, one step a group in the
curator's order (**Step n of m**, with **Next** and **Back**): the data
members ticked, brokers and venues to choose, none preselected. A member
your deployment already holds is never moved; one that is unavailable, or
"Not permitted here" (its floor not met, or a registry the deployment does
not take), cannot be ticked, with why beneath the table. The review says
each data source's terms are accepted on **Data sources**, never by a pack,
and links the Terms where a member is community. Write a note and install.

The deployment installs the members one by one, as
[Install it](#install-it) does each, going on past a failure and rolling
nothing back. Each member's install record names the pack, and the pack's
install is one record of the members ticked and how each went. It launches
nothing.

**The pack's page** is its setup checklist: a tab per group, and **About**.
Each member is one line, with its version installed and the latest
offered, its state, its connection from its instance's **Setting up**, and
its next act: **Install**, **Retry**, **Launch**, or its setup step. A
member a later revision added says **Added to this pack**; one it dropped
says **No longer in this pack** and stays installed. A pack its curator
withdrew says **Withdrawn by its curator**. Launch each member from here,
approving the roles each asks for.

**Update all** moves each launched member to the newest version offered in
its source registry, each its own update; a member asking for more roles is
skipped as **Needs approval**, approved on its own **Update** sheet
(**Update to {version}**). **Remove pack** removes only this deployment's
record of the pack, through a confirmation with a note: every member stays
installed, and running where it runs.

Through an agent, the same is done with core's
[starter pack tools](../api/core-tools.md#starter-packs), each act with a
note.

**From the command line,** CLI 0.1.53 installs a pack through the
deployment, as the sheet does, and reads and keeps it with
[`meridian plugin pack`](../api/cli.md#meridian-plugin-pack):

```bash
meridian plugin install --pack crypto --with plugin-coinbase --note "the crypto desk"
meridian plugin pack list
meridian plugin pack show crypto
meridian plugin pack update crypto --note "monthly update"
meridian plugin pack remove crypto --note "the desk closed" --yes
```

`--pack` installs the members the curator preselected, and none of those
you choose: add one with `--with`, leave a preselected one out with
`--without`. The plan is shown version by version and asked about first;
`--yes` approves it without asking. The command follows the install one
line a member, then lists `meridian plugin launch` for each member ready to
launch. A deployment whose core is older than contract 28 installs no pack,
and the CLI says so in one line.

## Update it

**Installed** shows each version with its source registry, and each instance it runs with
**Update to x.y.z** where a newer version is listed in the same registry, never a pre-release over
a release. The **Update** sheet starts, like Install's, with a step to read and **Continue**,
then shows the roles now and the roles asked; a version asking for more roles shows
**Needs approval**, a deployment admin's to approve. A plugin's admin may update where the roles are unchanged. Every
update is a person's act: nothing updates by itself.

## A pulled version

When the platform pulls a version, the next catalogue pull warns every deployment that installed
it, with why (a breach of the terms, or a copyright notice), and the platform emails your project's
Owners and Admins. The warning heads the instance's **Summary** and the **Installed** line, with
**Keep or stop**. Nothing is removed: stop the instance (`meridian plugin stop`), or **Keep it**
with a note, and either is recorded.

## Report plugin usage

**Report plugin usage**, on the **Registries** tab, is on by default and shown at your first
install. While on, the conductor sends the platform a weekly report of each installed registry
version's instances, how many people hold each level, and its daily operation and request counts,
naming no person, account or instrument. Each report sent is listed on the tab. Turn it off there,
with a note.

## A deployment that reaches nothing

A deployment with no route to the platform installs from a **plugin bundle** carried in by hand.

On a connected machine with CLI 0.1.53:

```bash
meridian plugin download open-meridian/snaptrade@0.20.0
```

It signs in to the platform in your browser the first time, asks where the version is, pulls it,
and verifies the image, its provenance, bill of materials, scan results and listing statement
against the platform's keys this CLI release carries: CLI 0.1.53 carries the platform's
registry-signing key, version 1. Only then does it write
`open-meridian-snaptrade-0.20.0.plugin-bundle.tar` (`--to` names another file), with the
version's documentation and a dated copy of the signing keys' status. `--registry` names the
registry, community by default.

On a machine connected to the air-gapped deployment (`meridian connect`):

```bash
meridian plugin upload --bundle open-meridian-snaptrade-0.20.0.plugin-bundle.tar
```

The CLI verifies the bundle first, as `plugin download` did. The deployment verifies it again, as at
install, against the platform's keys its chart carries, asking nothing of the platform, and records
the version under its listing with its registry. The **Installed** list shows how old the key status
it was checked against is, and the bundle's key status is kept as the newest the deployment holds,
so each later launch verifies again without the platform. Such a
deployment reports nothing, and learns of a pull only from a later bundle.

## Related

- [Registries](../concepts/registries.md).
- [Plugins, roles and grants](../concepts/plugins.md): launching and approval.
- [Command line](../api/cli.md#meridian-plugin-download): `plugin download` and `plugin upload --bundle`.
