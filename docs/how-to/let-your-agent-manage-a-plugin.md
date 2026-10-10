# Let your agent manage a plugin's settings and archive

An agent connected to your deployment can do in a plugin's area what you can
do there yourself: read its Summary and settings, set a value, allow its
archive, and launch or stop it. It acts as you, on a delegation you make,
and only as far as you could at the same page. This page shows the steps;
each tool is in [Core's tools](../api/core-tools.md).

!!! note "Contract v17"
    This page describes core's plugin-area tools, contract v17, from chart
    0.1.288.

Two things it never does: read or type a secret setting's value (you enter
a secret at the plugin's **Settings** form; the agent may clear one), and
change who holds access.

## Connect the agent

In your agent, add the deployment's MCP surface as a connector, at your
dashboard's address followed by `/mcp`. Sign in when it asks, and on
**Allow a client to act as you** tick what the work needs:

| To | Tick |
|---|---|
| Read a plugin's Summary and settings, and set them | The plugin's role at **Manage**, for each role whose settings it sets |
| Allow or withdraw an archive, set holds, launch and stop | **Deployment admin** |

A narrowed delegation never grows; to widen it, connect again.

## Read the plugin

Ask the agent to find the plugin and read it. It calls
`dashboard__list_plugins` for the instance's name, then:

- `dashboard__read_plugin_summary` for its status, figures, raw records,
  what it declares and its tools;
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
whole; `clear` clears a setting, a secret included. A cell that does not
read is refused by its path, as the form marks its cell, and a setting
serving a role you do not administer is refused naming the role.

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

## See what it did

Every call is listed in your **Connected clients**: when, which client,
which tool and the gate it was admitted under. Each change is its own
record naming you, the delegation and the client; see
[Where a change is recorded](../api/core-tools.md#where-a-change-is-recorded).
**Revoke** there stops the agent at its next call.
