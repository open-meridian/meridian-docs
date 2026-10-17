# Let your agent manage a plugin's settings and archive

An agent connected to your deployment can do in a plugin's area what you can
do there yourself: read its Summary and settings, set a value, allow its
archive, and launch or stop it. It acts as you, on a delegation you make,
and only as far as you could at the same page. This page shows the steps;
each tool is in [Core's tools](../api/core-tools.md).

Your agent may also **prepare** any of these changes for you, or someone
else, to make, instead of making it, and your firm sets, per act, whether
agents may make it, only prepare it, or not reach it (see
[Prepare instead of make](#prepare-instead-of-make)).

Two things it never does: read or type a secret setting's value (you enter
a secret at the plugin's **Settings** form; the agent may clear one), and
change who holds access.

Your agent acts for you, while your delegation lasts. Work with no person
behind it, such as an agent inside a plugin or a nightly sweep, runs as a
[service account](../concepts/service-accounts.md), never on your
delegation.

## Connect the agent

In your agent, add the deployment's MCP surface as a connector, at your
dashboard's address followed by `/mcp`. Sign in when it asks, and on
**Allow a client to act as you** tick what the work needs:

| To | Tick |
|---|---|
| Read a plugin's Summary and settings, and set them | The plugin's role at **Manage**, for each role whose settings it sets |
| Allow or withdraw an archive, set holds, launch and stop | **Deployment admin** |

A narrowed delegation never grows; to widen it, connect again. Each row
also offers **Make** or **Prepare
only**: Prepare only lets the agent prepare that row's changes for you and
make none of them, whatever the deployment allows. It can only make the
agent stricter than the deployment's own levels, never looser.

## Read the plugin

Ask the agent to find the plugin and read it. It calls
`dashboard__list_plugins` for the instance's name, then:

- `dashboard__read_plugin_summary` for its status, figures and raw records;
- `dashboard__read_plugin_documentation` for its vendor's documentation and
  its Reference: what it declares, and its tools;
- `dashboard__read_plugin_settings` for each setting that is not secret,
  each table's rows, which secrets are set and by whom, and `may_set` on
  each setting, saying whether you may change it.

## Set a value, with a note

Every change takes a note saying why, and the agent passes back the
`updated_at_ns` it read, so a change made since is refused rather than
overwritten:

```json
{
  "plugin_instance_id": "snaptrade-1",
  "value": {"activity_window_days": 2600},
  "against_updated_at_ns": 1791417600000000000,
  "note": "Keep activity a little past seven years."
}
```

That is `dashboard__set_plugin_settings`. A table's rows go under `table`,
whole; `clear` clears a setting, a secret included, as the form's
**Remove** does. A cell that does not read is refused by its path, as the
form marks its cell, and a setting serving a role you do not administer is
refused naming the role.

## Allow an archive

As a deployment admin, `dashboard__allow_archive` with the instance, the
most bytes it may hold (0 for no bound) and a note. The instance restarts
with its archive, and the Summary's raw records show it allowed.
`dashboard__withdraw_archive` withdraws it; what the archive holds is kept.
`dashboard__set_hold` sets a hold, 0 days clearing it. See
[The archive](../concepts/the-archive.md).

## Launch and stop

As a deployment admin, `dashboard__read_plugin_catalogue` lists the versions
uploaded and their launches, as `meridian plugin list` does.
`dashboard__stop_plugin` stops an instance, and `dashboard__launch_plugin`
launches a version, naming exactly the roles the version declares, as
`meridian plugin launch` does. Each takes a note.

## Prepare instead of make

Every change on this page can be prepared instead: the agent calls `dashboard__prepare_call` with the act's
tool, its arguments as above, and why. The dashboard checks it as the act
would and keeps it, changing nothing, and answers its `PC-` ID:

```json
{
  "tool": "dashboard__set_plugin_settings",
  "arguments": {"plugin_instance_id": "snaptrade-1",
                "value": {"activity_window_days": 2600},
                "against_updated_at_ns": 1791417600000000000,
                "note": "Keep activity a little past seven years."},
  "reason": "Your custodian's statements go back seven years; this keeps all of them."
}
```

You see it in your **Inbox**, under **Prepared changes**. A settings change
opens on the plugin's Settings form, started from what the agent prepared,
marked "prepared by" with its reason: **Save settings** makes it as your own
act, or change it first. Any other act is made with **Make** on the prepared
change's page; **Discard** drops it. It lapses after 30 days unmade, or the
period your deployment admin set.

Where the deployment admin or the plugin's admin has set an act to **Prepare
only**, a direct call is refused with `prepare_only`, saying to prepare it;
at **May not** the agent is not offered the act at all. Where the act needs
a **second pair of eyes**, nobody makes it alone: someone other than you
makes what your agent prepared. `dashboard__list_prepared` tells the agent
what it prepared and what became of each, and the level and gate of every
act it reaches. See [Prepared changes](../concepts/prepared-changes.md).

## See what it did

Every call is listed in your **Connected clients**: when, which client,
which tool and the gate it was admitted under, and what each client
prepared and what became of it. Each change is its own record
naming you, the delegation and the client; see
[Where a change is recorded](../api/core-tools.md#where-a-change-is-recorded).
**Revoke** there stops the agent at its next call.
