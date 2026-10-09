# Core's tools

A deployment serves one MCP surface, at its dashboard's `/mcp`. Beside each
plugin's own tools it lists core's, named `dashboard__...`: the
[Instruments tools](../concepts/instruments.md), the
[ticket and inbox tools](../concepts/tickets-and-the-inbox.md#through-an-agent),
and, from contract v17, thirteen tools over the parts of a plugin's area the
dashboard draws: its Summary, its moves, its settings and table settings,
who holds access to it (read only), its archive, the deployment's holds,
and launching and stopping it. This page is the reference for those
thirteen. An agent calls them as the person who delegated to it, and only
as far as that person could at the page each tool mirrors.

!!! note "Built, not released"
    This page describes core's plugin-area tools, contract v17, built into
    the dashboard and not yet released in a chart. Nothing changes for a
    plugin: the SDK, the CLI and every plugin stay as they are, and a plugin
    still declares contract v16.

## What every one of them does

- **The page's gate.** Each tool is listed only through a delegation that
  covers the gate of the page it mirrors, and is checked again on every
  call (see [Who may call them](#who-may-call-them)).
- **The instance is an argument.** A tool on one plugin takes its instance
  by name, `plugin_instance_id`, or `instance_id` on the archive, launch
  and stop tools, as those records name it. `dashboard__list_plugins` finds
  the instances. A call naming an instance the delegation does not reach at
  that page's level is refused at that argument, naming the instances it
  does reach.
- **A note on every change.** Every tool that changes something takes a
  `note` saying why, required, up to 2,000 characters, and keeps it with the
  change. The pages ask for none.
- **Each change its own record**, as the same change made at the page,
  naming the person, the delegation and the client (see
  [Where a change is recorded](#where-a-change-is-recorded)).
- **Two exceptions, and only two.** No tool reads or takes a secret
  setting's value, in either direction: a person enters a secret at the
  plugin's **Settings** form. A tool says that a secret is set, by whom and
  when, and clearing one is allowed, as the form's **Clear it**. And no tool
  changes who holds access: none defines a user, account or access group,
  and none grants or withdraws a permission.

Every answer has an `outcome`: `made` for a change, `unchanged` for a read
or a change that changed nothing, `refused` with a `reason`, a `detail` and
the `fields` it refused, each by its path in the tool's input. Its `data`
is the record's own fields by their names: an enumeration is its proto name,
such as `ACCESS_LEVEL_ADMIN`; a time is nanoseconds since the epoch; a
decimal is a string.

## Who may call them

| Tool | Reads or acts | Who |
|---|---|---|
| [`dashboard__list_plugins`](#dashboard__list_plugins) | reads | Anyone holding a level on a plugin, or the deployment admin |
| [`dashboard__read_plugin_summary`](#dashboard__read_plugin_summary) | reads | An admin of any of the plugin's roles, or the deployment admin |
| [`dashboard__read_moves`](#dashboard__read_moves) | reads | An admin of any of the plugin's roles |
| [`dashboard__read_plugin_settings`](#dashboard__read_plugin_settings) | reads | An admin of any of the plugin's roles |
| [`dashboard__set_plugin_settings`](#dashboard__set_plugin_settings) | acts | An admin of any of the plugin's roles; a setting serving several roles, an admin of every one |
| [`dashboard__read_plugin_access`](#dashboard__read_plugin_access) | reads | An admin of any of the plugin's roles, or the deployment admin |
| [`dashboard__allow_archive`](#dashboard__allow_archive) | acts | The deployment admin |
| [`dashboard__withdraw_archive`](#dashboard__withdraw_archive) | acts | The deployment admin |
| [`dashboard__read_holds`](#dashboard__read_holds) | reads | The deployment admin |
| [`dashboard__set_hold`](#dashboard__set_hold) | acts | The deployment admin |
| [`dashboard__read_plugin_catalogue`](#dashboard__read_plugin_catalogue) | reads | The deployment admin |
| [`dashboard__launch_plugin`](#dashboard__launch_plugin) | acts | The deployment admin |
| [`dashboard__stop_plugin`](#dashboard__stop_plugin) | acts | The deployment admin |

"An admin of a role" is `admin` on that role of the plugin, at **Manage**,
held through the delegation (see [Admin per role](../concepts/access.md#admin-per-role));
on a plugin holding no role, `admin` on the plugin. "The deployment admin"
means a delegation covering the deployment admin's capabilities. A person
holding only `read` or `write` on a plugin is listed
`dashboard__list_plugins` and none of the others.

The call's record, listed in the person's **Connected clients**, names the
gate it was admitted under as its level: `admin on snaptrade-1:custody`,
`deployment admin`, or, for `dashboard__list_plugins`, `any level on a
plugin`.

## The plugin's area

### `dashboard__list_plugins`

The dashboard home's plugin entries: each instance the person holds any
level on through the delegation, every one for the deployment admin.

**Input:** nothing.

**Answer:** `plugins`, each with `plugin_instance_id`, `title`, `roles`,
`entries` (what the person holds, each a `role` and a `level`),
`registered`, `healthy`, `health_detail` and `reported_at_ns`.

### `dashboard__read_plugin_summary`

The plugin's **Summary**, as its admin reads it under Manage, and the admin
view's **Overview** with its connections.

**Input:** `plugin_instance_id`.

**Answer:** for anyone it admits, the Overview's parts: `roles`,
`registered`, `healthy`, `health_detail`, `last_heartbeat_at_ns`,
`reported_at_ns`, `contract_version`, `refused_grants`,
`last_refusal_reason`, its `launch` from the catalogue where it has one, and
`sync`, each external account's sync state. An admin of any of its roles
also reads the Summary's own parts: `figures`, `declaration`,
`not_carried_seen`, `declared_tools`, `tool_refusals` and `stored`, what
storage holds of each kind of raw record; and on an edge plugin keeping raw
records, the `holds` over it, `archived`, what the archive holds of each
kind, and its `archive` as allowed. A deployment admin who administers none
of its roles reads the Overview's parts alone. Nothing of a raw record's
content is answered.

### `dashboard__read_moves`

The Summary's **Moves**: an edge plugin's moves of its raw records, newest
first, a page at a time.

**Input:** `plugin_instance_id`; `cursor`, the `next_cursor` of the page
before, for the next.

**Answer:** `moves`, each a `move` (`record_kind`, `unit`, `record_count`,
`first_received_ns`, `last_received_ns`, `outcome`, `rule`), the `person`
where one made it, `at_ns`, and the `acting_through_delegation` and
`client_name` they acted through; `next_cursor`; `archived`; and `archive`.

### `dashboard__read_plugin_settings`

The plugin's **Settings** form and each table setting's tab, as they show
this person.

**Input:** `plugin_instance_id`.

**Answer:**

| Field | What it holds |
|---|---|
| `values` | Each setting that is not secret, by `name` and `value`. A table's value is its rows, each with `changed_by` and `changed_at`. |
| `secrets_set` | The names of the secrets that are set. Never a value. |
| `changes` | Each setting's last change, a secret's included: `name`, `changed_by`, `changed_at_ns`, `acting_through_delegation`, `client_name` ([`SettingLastChange`](../boundaries/conductor.md#meridian.v1.SettingLastChange)). |
| `updated_at_ns`, `updated_by` | The record's latest change. A change names `updated_at_ns` as `against_updated_at_ns`. |
| `declared_settings` | Each setting as the form shows it ([`SettingShown`](../boundaries/dashboard.md#meridian.v1.SettingShown)): what the plugin declared of it, the roles it serves, `may_set`, whether this person may set it, and where they may not, `detail`, saying why. A developer setting only on a development deployment. |
| `accounts` | The external accounts a table's column offers, each `external_account_id` and `name`. |

### `dashboard__set_plugin_settings`

**Save** on the Settings form or a table's tab. The tool takes the form's
own field names as JSON and runs the form's own checks, so an argument is
refused where the form refuses its cell, by the same path.

**Input:**

| Argument | What it takes |
|---|---|
| `plugin_instance_id` | Required. |
| `value` | `{"<name>": value}`: a setting that is not secret, set to text, a whole number, or true or false. |
| `table` | `{"<name>": [rows]}`: a table's rows, whole, each row its cells by column. It replaces the table. |
| `clear` | `{"<name>": true}`: clears a setting, a table or a secret. |
| `against_updated_at_ns` | `updated_at_ns` as read. The change is refused if the settings changed since. |
| `note` | Required: why. |

```json
{
  "plugin_instance_id": "snaptrade-1",
  "value": {"activity_window_days": 2600},
  "against_updated_at_ns": 1791417600000000000,
  "note": "Keep activity a little past seven years."
}
```

**Answer:** `made` with the settings as `dashboard__read_plugin_settings`
answers them, or `unchanged` when nothing named differs from what is set.

It never takes a secret's value: a secret named under `value` or `table`, or
any argument under `secret`, is refused by its path, such as
`secret.api_key`, saying a person enters it at the Settings form. A setting
serving several roles is refused, at its path and naming the roles, unless
the person administers every one. The deployment's own checks then apply as
at the page: a window below a hold, for one, is refused at that setting's
path.

## Who holds access

### `dashboard__read_plugin_access`

The admin view's **Access** tab, read only.

**Input:** `plugin_instance_id`.

**Answer:** the plugin's `roles`; the `access_groups` with entries on it,
and **All plugins (admin)**, each with its entries on this plugin (`role`
and `level`) and whether it is built in;
the `permissions` to those groups; and the `user_groups` and
`account_groups` those permissions join. No tool changes any of it: grants
are made at the page, by a deployment admin (see
[Give people access](../how-to/administer-access.md)).

## The archive and the holds

### `dashboard__allow_archive`

**Allow archive** on the Summary's raw records, or a change to its bound.
See [The archive](../concepts/the-archive.md).

**Input:** `instance_id`; `most_bytes`, the most the archive may hold, 0 for
no bound; `note`.

**Answer:** `made`, the archive as allowed (`allowed`, `most_bytes`, who,
when, and the delegation and client), saying the instance restarts with it.

### `dashboard__withdraw_archive`

**Withdraw**.

**Input:** `instance_id`, `note`.

**Answer:** `made`, saying the instance restarts without its archive and
that what the archive holds is kept; `unchanged` where it was allowed none.

### `dashboard__read_holds`

The **Holds** tab of the deployment's Settings.

**Input:** nothing.

**Answer:** `holds`, each with its `role` (empty for every edge role),
`days`, `write_once`, `updated_by`, `updated_at_ns`, and the
`acting_through_delegation` and `client_name` it was set through. An admin
of a plugin reads the hold over it in `dashboard__read_plugin_summary`.

### `dashboard__set_hold`

The hold's dialog, and its **Clear**.

**Input:** `role`, an edge role or empty for every one; `days`, 0 to 36,500,
0 clearing the hold; `write_once`; `note`.

**Answer:** `made`, the hold as set. Write-once is refused where the
deployment's archive cannot lock, as at the page.

## Launching and stopping

These mirror `meridian plugin list`, `launch` and `stop`; see
[Command line](cli.md). Uploading a version stays the CLI's.

### `dashboard__read_plugin_catalogue`

**Input:** nothing.

**Answer:** `versions`, each version uploaded with its name, version, roles,
interface, SDK version and declaration, its image digest, and who uploaded
it and when; and `launches`, each launch, live or ended: its instance,
version, roles, state, who launched and stopped it and when, and the
delegation and client each acted through (`acting_through_delegation`,
`client_name`, `stopped_through_delegation`, `stopped_client_name`).

### `dashboard__launch_plugin`

**Input:** `name`, `version`, `instance_id`; `approved_roles`, exactly the
version's roles, as `meridian plugin launch` approves them; `live`, only on
a development deployment; `note`.

**Answer:** `made`, the launch. Roles other than the version's own are
refused, as are a version not in the catalogue and `live` anywhere but a
development deployment.

### `dashboard__stop_plugin`

**Input:** `instance_id`, `note`.

**Answer:** `made`, the launch as stopped. An instance with no live launch
is refused.

## Refusals

| `reason` | When |
|---|---|
| `not_listed` | The tool is not listed through this delegation, such as a settings tool called by a person holding only `write`; recorded like any call. Also a plugin that has not reported, so its settings are not known yet, and, on `dashboard__set_plugin_settings`, an instance the delegation does not reach. |
| `invalid_arguments` | An argument that does not read, or is not the tool's, by its path: a missing `note`, a secret's value (`secret.<name>`, `value.<name>`), a table's cell that does not read (`table.<name>[<row>].<column>`), an instance the delegation does not reach at that page's level, naming those it does. |
| `not_administered` | A setting serving a role the person does not administer, at its path, naming the roles. |
| `REFUSAL_REASON_RECORD_CHANGED` | The settings changed since `against_updated_at_ns` was read, at that argument. Nothing was changed: read them again. |
| the deployment's own | The same refusal the page meets, with its sentence: a window below a hold, write-once where the archive cannot lock, roles other than the version's, no live launch to stop. |
| `rate_limited`, `unavailable` | As for any tool on the surface. |

## Where a change is recorded

A change made through one of these tools is recorded as the same change
made at the page, and names the person, the delegation and the client, with
the note: in the deployment's configuration, a record for each setting
changed, each hold, each archive allowed or withdrawn, each launch and each
stop. From contract v17 a launch or stop made with `meridian plugin` names
the CLI's delegation and client too.

Where a person sees it:

- **Connected clients**, under their name at the dashboard's top right,
  lists every call: when, which client, which tool, the gate it was admitted
  under, and how it came out. Never what was asked or answered.
- **The Settings form**, on hover over a secret's **set**: who set it, when,
  and through which client, such as *Set by Ada, 2026-10-09 14:02 UTC,
  through Claude*.

Elsewhere the records say it and no page does yet: the client a setting,
hold, archive, launch or stop was changed through is answered by
`dashboard__read_plugin_settings` (`changes`), `dashboard__read_holds`,
`dashboard__read_plugin_summary` and `dashboard__read_moves` (`archive`),
and `dashboard__read_plugin_catalogue`. The note is kept with the change,
and no page or tool shows it yet.

Changes made in a browser before v17 name no delegation or client, which is
true: a browser acts through none. Every launch and stop before v17 was made
through the CLI on a delegation that was not recorded, and each has a record
saying so, at the moment the deployment was upgraded.

## Related

- [Let your agent manage a plugin's settings and archive](../how-to/let-your-agent-manage-a-plugin.md):
  these tools, step by step.
- [Set a plugin's settings](../how-to/set-a-plugins-settings.md): the same
  settings at the page.
- [Keep older records in the archive](../how-to/keep-older-records-in-the-archive.md):
  the archive and holds at the page.
- [Offer your plugin's pages to agents](../how-to/offer-your-pages-to-agents.md):
  a plugin's own tools on the same surface.
