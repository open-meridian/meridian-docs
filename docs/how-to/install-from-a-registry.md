# Install a plugin from a registry

A plugin listed in the platform's community registry, such as `open-meridian/snaptrade`, is
installed into your deployment's own registry by digest, verified, and then launched the way any
version is. What the registries are, and what each checks, is in
[Registries](../concepts/registries.md). Read
[Who checks a plugin](../concepts/plan-your-deployment.md#who-checks-a-plugin) first: community
plugins are unsupervised.

You need to be a deployment admin.

!!! note "TODO: core, not built yet"
    Core's v25 branch has not landed the Plugins page's **Browse**, **Installed** and
    **Registries** tabs, or their tools (`dashboard__search_registry_plugins`,
    `dashboard__read_registry_plugin`, `dashboard__install_plugin`, `dashboard__update_plugin`,
    `dashboard__acknowledge_pull`, `dashboard__read_registries`,
    `dashboard__set_reports_plugin_usage`). The steps below are the accepted spec's; check every
    label against core as built, and add the browser check's screenshots.

## Find it

On the dashboard's **Plugins** page, **Browse** lists the catalogue your deployment last pulled:
one line per listing, with its registry, latest version, roles, whether its floor fits your
deployment, stars and installs. Search by words, or filter by registry and role. The notice's title
heads the list and opens its full text.

A listing opens on three tabs: **Overview** (the notice in full, the vendor and its attributes,
the build's repository, commit, tag and signing key, the floor against your deployment, stars and
installs), **Documentation** (the version's sections and its Reference) and **Versions**.

The catalogue is pulled hourly; **Pull now** on the **Registries** tab pulls it at once.

## Install it

**Install** opens a dialog showing the notice, the roles the version asks for, the floor's result
and the verification's result. Installing pulls the image and its attachments by digest into your
deployment's registry, and the conductor verifies them against the platform's keys your chart
carries. A version failing a check is refused, naming the check. Install launches nothing.

Then launch it as any version, approving its roles (see
[Launching, and approval](../concepts/plugins.md#launching-and-approval)). For a verified version
you can approve no role beyond those its review approved. (TODO: how `meridian plugin launch` and
`meridian plugin list` name a listed version, as core builds it.)

An instance already running a local version of the same plugin is offered **Move to this listing**
in the same dialog. The move keeps the instance's state, is checked as an update, and is recorded.

## Update it

**Installed** shows each version's registry and listing, and **Update to x.y.z** where a newer
version is listed in the same registry. **Update** opens a dialog showing the difference and the
notice; a version asking for more roles or scope shows **Needs approval** and waits for yours.
Every update is a person's act: nothing updates by itself.

## A pulled version

When the platform pulls a version, the next catalogue pull warns every deployment that installed
it, with why (a breach of the terms, or a copyright notice), and the platform emails your project's
Owners and Admins. The warning heads the instance's **Summary** and the **Installed** line. Nothing
is removed: stop the instance, or keep it with a note, and either is recorded.

## Report plugin usage

**Report plugin usage**, on the **Registries** tab, is on by default and shown at your first
install. While on, the conductor sends the platform a weekly report of each installed registry
version's instances, how many people hold each level, and its daily operation and request counts,
naming no person, account or instrument. Each report sent is listed on the tab. Turn it off there,
with a note.

## A deployment that reaches nothing

A deployment with no route to the platform installs from a **plugin bundle** carried in by hand.

On a connected machine with CLI 0.1.46:

```bash
meridian plugin download open-meridian/snaptrade@0.18.0
```

It signs in to the platform in your browser the first time, asks where the version is, pulls it,
and verifies the image, its provenance, bill of materials, scan results and listing statement
against the platform's keys this CLI release carries. Only then does it write
`open-meridian-snaptrade-0.18.0.plugin-bundle.tar` (`--to` names another file), with the
version's documentation and a dated copy of the signing keys' status. `--registry` names the
registry, community by default.

On a machine connected to the air-gapped deployment (`meridian connect`):

```bash
meridian plugin upload --bundle open-meridian-snaptrade-0.18.0.plugin-bundle.tar
```

The deployment verifies the bundle again, as at install, and records the version with its listing
and registry. The **Installed** list shows how old the key status it was checked against is. Such a
deployment reports nothing, and learns of a pull only from a later bundle.

## Related

- [Registries](../concepts/registries.md).
- [Plugins, roles and grants](../concepts/plugins.md): launching and approval.
- [Command line](../api/cli.md#meridian-plugin-download): `plugin download` and `plugin upload --bundle`.
