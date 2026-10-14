# Core's tools

A deployment serves one MCP surface, at its dashboard's `/mcp`. Beside each
plugin's own tools it lists core's, named `dashboard__...`: the
[Instruments tools](../concepts/instruments.md), the
[ticket and inbox tools](../concepts/tickets-and-the-inbox.md#through-an-agent),
and, from contract v17, thirteen tools over the parts of a plugin's area the
dashboard draws: its Summary, its moves, its settings and table settings,
who holds access to it (read only), its archive, the deployment's holds,
and launching and stopping it. From contract v18, five more mirror the
**Data sources** page: the lake's datasets, their licences and
entitlements, and the source priority. From contract v20, seven more work [prepared changes](../concepts/prepared-changes.md)
and one reads the accounts a plugin may link to. From contract v21, one reads the [service accounts](#service-accounts). From
contract v22, four set and list the
[trading instructions and account attributes](#trading-instructions-and-account-attributes),
and two read the Instruments page's [Calendars tab](#the-calendars-tab). This
page is the reference for those thirty-three. An agent calls them as the person who
delegated to it, and only as far as that person could at the page each tool
mirrors, and from v20 only as far as the deployment lets agents go with each
act.

!!! note "Contract v17"
    This page describes core's plugin-area tools, contract v17, from chart
    0.1.288. Nothing changes for a
    plugin: the SDK, the CLI and every plugin stay as they are, and a plugin
    still declares contract v16.

!!! note "Contract v18"
    [The Data sources page](#the-data-sources-page) and its five tools, and
    v17's security fixes marked *from contract v18* below, are in chart
    0.1.292.

!!! note "Contract v19"
    Released 2026-10-10 in chart 0.1.294. From chart 0.1.293 the source
    priority takes trades and quotes, and the
    [Instruments tools](../concepts/instruments.md#through-an-agent) answer
    and take a binary event contract's payout and close, each identifier's
    window, and a conflict's reason. No tool is added, and no core tool
    reads a trade or a quote, as none reads a price.

!!! note "Contract v20"
    [Prepared changes](#prepared-changes) and their seven tools; what agents
    may do with each act (may make, prepare only, may not) and its second
    pair of eyes, answered by `dashboard__read_plugin_access` and
    `dashboard__list_prepared` and set at the page only;
    [`dashboard__read_linkable_accounts`](#dashboard__read_linkable_accounts);
    the Summary's **Setting up** part; and a secret's last four characters
    (`hint`) in a setting's last change. Released 2026-10-12 in chart 0.1.298. Every act listed below that changes something can be
    prepared, but for the prepared changes' own tools.

!!! note "Contract v21"
    [`dashboard__list_service_accounts`](#dashboard__list_service_accounts)
    reads the Service accounts tab; `dashboard__read_plugin_access` answers
    each role's `runs_as`; `dashboard__read_inbox` answers a service
    account's owner its notices; and `dashboard__read_prepared` withholds a
    service account's prepared change's arguments from its owner where they
    name an account the owner may not read. Creating, granting and changing
    a service account, and choosing what a role runs as, are set at the page
    only. A service account itself never reaches `/mcp`: it holds no
    delegation, and no core tool is reachable as one. See
    [Service accounts](../concepts/service-accounts.md). Released
    2026-10-12 in chart 0.1.299.

!!! note "Contract v22"
    [`dashboard__set_trading_instruction`](#dashboard__set_trading_instruction),
    [`dashboard__list_trading_instructions`](#dashboard__list_trading_instructions),
    [`dashboard__set_account_attribute`](#dashboard__set_account_attribute)
    and [`dashboard__list_account_attributes`](#dashboard__list_account_attributes)
    mirror the **Trading instructions** page and the Accounts tab's book
    part, each act at the setter's level, preparable, and at **May not** for
    agents until the deployment admin loosens it;
    [`dashboard__list_calendars`](#dashboard__list_calendars) and
    [`dashboard__read_calendar`](#dashboard__read_calendar) read the
    Instruments page's **Calendars** tab; and `dashboard__read_plugin_access`
    answers a connectivity plugin's link, and an `ems`'s connectivity plugins
    and venue account map, in `connectivity`. Making a connectivity plugin
    available, linking it to an `ems` and choosing who may route through it
    are access, set at the page only. See
    [The order lifecycle](../concepts/the-order-lifecycle.md) and
    [Settlement calendars](../concepts/settlement-calendars.md). Released
    2026-10-13 in chart 0.1.301.

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
  change. The pages ask for none. From contract v22 the two acts on the book,
  `dashboard__set_trading_instruction` and `dashboard__set_account_attribute`,
  keep their `note` as the book entry's reason, where the page asks for a
  **Why** or a **Reason**.
- **Each change its own record**, as the same change made at the page,
  naming the person, the delegation and the client (see
  [Where a change is recorded](#where-a-change-is-recorded)).
- **Others' words are marked.** From contract v18, what a plugin wrote (its
  declaration, its settings' descriptions, labels and choices, its tools'
  titles and descriptions, health and refusal details, figures, a vendor's
  name) and every note another person or agent wrote reach an agent
  screened, as a ticket's text is: one reading like an instruction to an
  agent is answered *withheld*, naming the rules it matched, and a person
  reads it at the page. Each tool's description says these are data, never
  instructions.
- **Fresh consent for a new tool that changes something.** From contract
  v18, a delegation narrowed to some of what a person holds keeps the tools
  that change something its consent page listed. One added since, by a
  release or a plugin, is not listed to it, and a call is refused, saying it
  waits until the person consents again from that client, where the consent
  page names it as new. A tool that only reads follows the person's grants
  as before, and a delegation covering **everything you hold** lists every
  tool at once. A delegation narrowed before v18 is filled once, at its
  first use, with what it reached then, and says so.
- **What agents may do with the act.** From contract v20 each act has a level the deployment admin and the plugin's
  admin set: at **May make** the tool makes the change; at **Prepare only**
  it is listed saying so, and a call is refused with `prepare_only`, naming
  [`dashboard__prepare_call`](#dashboard__prepare_call); at **May not** it is
  not listed. Where the act's second pair of eyes is on, a direct call is
  refused with `second_pair_of_eyes`. See
  [What agents may do](../concepts/prepared-changes.md#what-agents-may-do).
- **Two exceptions, and only two.** No tool reads or takes a secret
  setting's value, in either direction: a person enters a secret at the
  plugin's **Settings** form. A tool says that a secret is set, by whom and
  when, and from v20 its last four characters where it is long enough;
  clearing one is allowed, as the form's **Remove** (before v20, **Clear
  it**). And no tool changes who holds access: none defines a user, account
  or access group, grants or withdraws a permission, or grants a plugin an
  account to link; from contract v21 none creates, changes, disables or
  removes a service account, or chooses what a role runs as; and from
  contract v22 none makes a connectivity plugin available, links it to an
  `ems` or chooses who may route through it.

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
| [`dashboard__list_datasets`](#dashboard__list_datasets) | reads | The deployment admin |
| [`dashboard__set_dataset_licence`](#dashboard__set_dataset_licence) | acts | The deployment admin |
| [`dashboard__set_dataset_entitlement`](#dashboard__set_dataset_entitlement) | acts | The deployment admin |
| [`dashboard__list_source_priorities`](#dashboard__list_source_priorities) | reads | The deployment admin |
| [`dashboard__set_source_priority`](#dashboard__set_source_priority) | acts | The deployment admin |
| [`dashboard__read_linkable_accounts`](#dashboard__read_linkable_accounts) | reads | An admin of any of the plugin's roles, or the deployment admin |
| [`dashboard__prepare_call`](#dashboard__prepare_call) | acts | Anyone whose delegation may make the act named, or holds it on a Prepare only row, where agents may make or prepare it |
| [`dashboard__list_prepared`](#dashboard__list_prepared) | reads | The delegation's own |
| [`dashboard__read_prepared`](#dashboard__read_prepared) | reads | One this delegation prepared, or one shown to the person |
| [`dashboard__withdraw_prepared`](#dashboard__withdraw_prepared) | acts | The delegation's own, while it waits |
| [`dashboard__make_prepared`](#dashboard__make_prepared) | acts | Whoever may make the act, once an admin loosens it from May not |
| [`dashboard__discard_prepared`](#dashboard__discard_prepared) | acts | Whoever it is shown to, once an admin loosens it from May not |
| [`dashboard__share_prepared`](#dashboard__share_prepared) | acts | Its person, once an admin loosens it from May not |
| [`dashboard__list_service_accounts`](#dashboard__list_service_accounts) | reads | Any delegation that reaches anything: every account for the deployment admin, the person's own otherwise |
| [`dashboard__list_trading_instructions`](#dashboard__list_trading_instructions) | reads | The deployment admin, every instruction; a plugin's admin, those naming a plugin they administer |
| [`dashboard__set_trading_instruction`](#dashboard__set_trading_instruction) | acts | The deployment admin, on any target; a plugin's admin, on their plugin or a person, service account or account within it; once an admin loosens it from May not |
| [`dashboard__list_account_attributes`](#dashboard__list_account_attributes) | reads | The deployment admin |
| [`dashboard__set_account_attribute`](#dashboard__set_account_attribute) | acts | The deployment admin, once loosened from May not |
| [`dashboard__list_calendars`](#dashboard__list_calendars) | reads | The deployment admin |
| [`dashboard__read_calendar`](#dashboard__read_calendar) | reads | The deployment admin |

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
`sync`, each external account's sync state. From contract v18 the `launch`
record is the deployment admin's: an admin of the plugin who is not a
deployment admin reads the version it runs instead. An admin of any of its roles
also reads the Summary's own parts: from contract v20 `setting-up`, the role's first-use steps as **Setting up** draws
them (`set_up`, and `steps`, each its `step`, `done` (true, false, or null
where the plugin's own page says), `where` and `deployment_admins`); `figures`, `declaration`,
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
| `changes` | Each setting's last change, a secret's included: `name`, `changed_by`, `changed_at_ns`, `acting_through_delegation`, `client_name` ([`SettingLastChange`](../boundaries/conductor.md#meridian.v1.SettingLastChange)); from contract v20 `hint`, a secret's last four characters where it has 16 or more, and `prepared_call_id` where the change was made from a prepared change. |
| `updated_at_ns`, `updated_by` | The record's latest change. A change names `updated_at_ns` as `against_updated_at_ns`. |
| `declared_settings` | Each setting as the form shows it ([`SettingShown`](../boundaries/dashboard.md#meridian.v1.SettingShown)): what the plugin declared of it, the roles it serves, `may_set`, whether this person may set it, and where they may not, `detail`, saying why. A developer setting only on a development deployment; from contract v18 neither its value nor its changes are read on a production deployment. |
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
| `against_updated_at_ns` | Required from contract v18: `updated_at_ns` as read, 0 for settings never saved. The change is refused if the settings changed since, and 0 is refused once any setting is saved, so a change read before a person's first save never replaces it. |
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
`account_groups` those permissions join. From contract v20 also each of the plugin's acts, with what agents may do with it
(`agents_may`: `may_make`, `prepare_only` or `may_not`; the ceiling where it
caps; each access group's stricter level) and whether it needs a
`second_pair_of_eyes`. From contract v21 also
`runs_as`, one line for each of the plugin's roles: the `role`, the
`service_account_id` its autonomous work runs as, its `name` and `state`
(`active`, `disabled`, `removed`), the `level` chosen, and the level the
account is `granted` on the role now; all but `role` empty where it runs as
none. From contract v22 also `connectivity`: for a
plugin holding `connectivity`, its `connectivity_link` (the
`connectivity_instance_id`, whether it is `available`, the
`ems_instance_id` it is linked to, empty for none, and its `users`, each a
`subject`, a `service_account_id` or a `user_group_id`); for a plugin
holding `ems`, its `connectivity_links`, each in the same shape, and its
`venue_account_map` (`ems_instance_id` and `mappings`, each a
`connectivity_instance_id`, a `venue_account_code` and an `account_id`);
empty for a plugin holding neither. See
[Route orders through a connectivity plugin](../how-to/route-orders-through-a-connectivity-plugin.md).
No tool changes any of it: grants are made at the
page, by a deployment admin (see
[Give people access](../how-to/administer-access.md)), levels at the
page, by the plugin's admin, and from v21 what a role runs as at the page,
by the role's admin; from v22 a connectivity plugin's availability by a
deployment admin, and its link and who may route through it by the `ems`'s
admin, at the page.

### `dashboard__read_linkable_accounts`

From contract v20. The admin view's **Accounts** tab,
read only: the accounts a deployment admin granted the instance to link its
external accounts to, nothing by default, with who last changed the grant
and when. A grant lets the plugin's admins link; it gives nobody anything to
read or write. No tool sets it. See
[Accounts a plugin may link to](../concepts/accounts.md#accounts-a-plugin-may-link-to).

**Input:** `plugin_instance_id`.

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
`client_name`, `stopped_through_delegation`, `stopped_client_name`), and
from contract v18 the note a stop was made with, `stopped_note`, beside the
launch's `note`.

### `dashboard__launch_plugin`

**Input:** `name`, `version`, `instance_id`; `approved_roles`, exactly the
version's roles, as `meridian plugin launch` approves them; `live`, only on
a development deployment; `note`.

**Answer:** `made`, the launch. Roles other than the version's own are
refused, as are a version not in the catalogue and `live` anywhere but a
development deployment. From contract v18 so are core's own names as an
instance (a component's, or the runtime's), and an instance ID a stopped
launch used for a different plugin.

### `dashboard__stop_plugin`

**Input:** `instance_id`, `note`.

**Answer:** `made`, the launch as stopped. An instance with no live launch
is refused.

## The Data sources page

From contract v18, chart 0.1.292. The dashboard's **Data sources**
page, on **Settings** beside **Instruments**, at the deployment admin's
level: the datasets each launched data plugin's catalogue serves the
[lake](../concepts/the-lake.md), their licences and entitlements, and the
source priority. See [Licences and entitlements](../concepts/licences-and-entitlements.md)
and, at the page, [License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md).

A tool's answer is what the page shows the same person, read from the same
rows. **None reads a price**: prices are the reading roles', on their
plugins' pages. A read answers `outcome: "unchanged"` from contract v23, as
core's other reads do; before v23, `dashboard__list_datasets` and
`dashboard__list_source_priorities` answered `outcome: "read"`, so a client
written against them accepts either (chart 0.1.303). A licence records
what was entered; no answer says the deployment meets a vendor's terms.

### `dashboard__list_datasets`

The page's **Datasets** and **Entitlements** tabs.

**Input:** nothing.

**Answer:** `datasets`, each with:

| Field | What it holds |
|---|---|
| `dataset`, `instance` | The dataset's ID, the instance, a colon and its key (`alpaca-1:daily`), and the instance serving it. |
| `vendor`, `aggregator` | Who originated it, and who carries it where an aggregator does, as the plugin names them: others' words, screened. |
| `catalogue_entry` | The catalogue's entry as the plugin declared it ([`DatasetDeclaration`](../boundaries/sidecar.md#meridian.v1.DatasetDeclaration)): data types and fields, modes, cadence, history, its default licence, its day's zone and end, its venue. Screened as others' words. |
| `licence` | The licence enforced: `set_by_the_deployment`, false while it is the catalogue's default; `kept`, `retention_days`, `derived_use`, `display`, `default_fields`, `personal_use`; and who set it, when, the `acting_through_delegation` and `client_name`, and its `note`. |
| `entitlements` | Each instance entitled now: `instance`, `allowed`, `fields` (none for every field), who set it, when, the delegation and client, and its `note`. |
| `unconverted_count` | How many of its values its plugin left unconverted. |
| `miss_count` | How many identifiers and venues its plugin reported missing. |
| `closed_day_count` | From contract v23: how many of its daily rows are dated on a closed day of its calendar, the page's **Closed days**. See [A daily value on a closed day](../concepts/the-lake.md#a-daily-value-on-a-closed-day). |
| `outside_coverage_count` | From contract v23: how many are dated outside its calendar's coverage, counted apart, shown beside the closed days ("(2 outside)"). |
| `one_person_warning` | Where its terms are one person's and more than one person holds `read` or `write` on a plugin entitled to it, the warning naming them; otherwise `null`. |

### `dashboard__set_dataset_licence`

The **Licence** dialog: replaces a dataset's licence whole.

**Input:**

| Argument | What it takes |
|---|---|
| `dataset` | Required: a dataset a launched instance's catalogue declares. |
| `kept` | Required: whether the lake may keep its rows; false serves them, not kept. |
| `retention_days` | Required: days a row is kept from when it was recorded, 0 to 36,500; 0 for no limit set. |
| `derived_use`, `display` | Required: whether derived data may be made, and whether it may be shown. |
| `default_fields` | The fields readable by default, by their dictionary entries, at most 64; none for every field. |
| `personal_use` | Required: whether its terms are one person's. |
| `note` | Required: why. |

```json
{
  "dataset": "alpaca-1:daily",
  "kept": true,
  "retention_days": 0,
  "derived_use": true,
  "display": true,
  "personal_use": true,
  "note": "Alpaca's terms read 2026-10-10: one account holder's, kept for their own use."
}
```

**Answer:** `made`, with the `dataset` and its `licence` as recorded.
Refused: a dataset no launched instance declares, a field that is no entry
of the dataset's data types, a retention out of bounds.

### `dashboard__set_dataset_entitlement`

The **Entitle** dialog, and **Withdraw** on the Entitlements tab.

**Input:** `dataset`; `instance`, a running plugin instance; `allowed`,
false to withdraw; `fields`, the dictionary entries it may read, at most
64, none for every field; `note`. All but `fields` are required.

**Answer:** `made`, the `entitlement` as recorded. Its deliveries follow at
once, and stop at once on a withdrawal, which clears its fields. Refused:
an instance that is not running, a dataset no launched instance declares,
a field that is no entry of the dataset's types.

### `dashboard__list_source_priorities`

The **Priority** tab.

**Input:** nothing.

**Answer:** `priorities`, each with its `data_type` (`meridian.v1.Price` or
`meridian.v1.Bar`, and from contract v19 `meridian.v1.Trade` or
`meridian.v1.Quote`), its `kind` for a price (`close`, `last`, `nav`,
`settlement`; `null` for any other type), its `datasets` first to last, who set it,
`updated_at_ns`, the delegation and client, and its `note`. A change is
sent against `updated_at_ns`.

### `dashboard__set_source_priority`

The priority's dialog: replaces a data type's priority whole, for prices one
kind's.

**Input:**

| Argument | What it takes |
|---|---|
| `data_type` | Required: `meridian.v1.Price` or `meridian.v1.Bar`, and from contract v19 `meridian.v1.Trade` or `meridian.v1.Quote`. |
| `kind` | For a price, required: `close`, `last`, `nav` or `settlement`. Any other type names none. |
| `datasets` | Required: 1 to 16, first to last, each declared for the data type. |
| `against_updated_at_ns` | Required: the priority's `updated_at_ns` as read, 0 where none is set. |
| `note` | Required: why. |

**Answer:** `made`, the `priority` as recorded, and `for`, what it is for
in words (`price close`). Refused with `REFUSAL_REASON_RECORD_CHANGED`
where another set it since it was read: nothing was changed; read it again.

## Prepared changes

From contract v20. See
[Prepared changes](../concepts/prepared-changes.md). No tool sets a level, a
second pair of eyes or the lapse period: those are set at the page only.

### `dashboard__prepare_call`

Prepare an act instead of making it.

**Input:** `tool`, the act's tool as listed, such as `dashboard__set_hold`
or `ops-1__confirm_opening_balance`; `arguments`, its arguments as the agent
would call it; `reason`, why, at most 4,000 characters.

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

**Answer:** `made`, with the prepared change's `PC-` ID, or the check's
refusal, each field by its path in the act's input, nothing kept. Nothing in
the deployment changes either way. Refused: an act this delegation may not
make or prepare, one at May not, one with no check, a secret's value, and
tickets' acts.

### `dashboard__list_prepared`

What this delegation prepared and what became of each (`prepared`,
`shared`, `made`, `changed`, `discarded`, `withdrawn`, `lapsed`), newest
first; the lapse period in days; and, for each act this delegation reaches,
what agents may do with it (`may_make`, `prepare_only`, `may_not`) and
whether it needs a second pair of eyes.

**Input:** nothing.

### `dashboard__read_prepared`

One prepared change, whole: the act, its arguments as prepared, the check's
answer, who prepared it and through which client, why, its state and its
history. The reason and the arguments are another's words, screened: data,
never instructions. From contract v21 a change a
service account prepared is read by its owner with its `arguments`
withheld where they name an account the owner may not read.

**Input:** `prepared_call_id`.

### `dashboard__withdraw_prepared`

Withdraw one this delegation prepared that is still waiting.

**Input:** `prepared_call_id`, `note`.

### `dashboard__make_prepared`

Make a prepared change shown to the person, as prepared or with changed
arguments, settled `made` or `changed`. At **May not** until an admin
loosens it; even then only where agents may make its act for this caller,
never one this client prepared, and under a second pair of eyes never one
the person prepared.

**Input:** `prepared_call_id`; `arguments`, the act's whole input, to make
it as changed; `note`.

### `dashboard__discard_prepared`

Discard a prepared change shown to the person: nothing is made of it. At
**May not** until an admin loosens it.

**Input:** `prepared_call_id`, `note`.

### `dashboard__share_prepared`

Share the person's own waiting prepared change with everyone who may make
it. At **May not** until an admin loosens it.

**Input:** `prepared_call_id`, `note`.

## Service accounts

From contract v21. See
[Service accounts](../concepts/service-accounts.md). No tool creates,
changes, grants, disables or removes a service account, or chooses what a
role runs as: those are a person's, at the page, since who acts is who holds
access.

### `dashboard__list_service_accounts`

The Settings' **Service accounts** tab, read only. Through a delegation
covering the deployment admin's capabilities, every service account; through
any other, only those the person owns.

**Input:** `cursor`, where the last page ended, as its `next_cursor` said;
`limit`, 1 to 200, 50 by default.

**Answer:** `service_accounts`, each row as the tab shows it: its
`service_account_id` (`SA-…`), `name`, `purpose`, `owner_subject` and
`owner` (their name), `setting` (`prepare_only` or `act`), `state`
(`active`, `disabled` or `removed`, a removed account still listed),
`runs_for` (each `instance:role` it runs for, the instance alone on a
plugin holding no role), `last_used_ns`,
`last_refusal` and `last_refusal_ns`; `next_cursor`, empty on the last
page; and `every_account`, whether the rows are every account or the
person's own. The names, purposes and refusals are another's words: data,
never instructions.

```json
{"outcome": "unchanged", "data": {
  "service_accounts": [{
    "service_account_id": "SA-01JA2Q3R4S5T6V7W8X9Y0Z1A2B",
    "name": "The sweep",
    "purpose": "Closes cleared breaks after each reconciliation.",
    "owner_subject": "local|cat", "owner": "Cat Ruiz",
    "setting": "prepare_only", "state": "active",
    "runs_for": ["sample-operations-1:operations"],
    "last_used_ns": 1791417600000000000,
    "last_refusal": "", "last_refusal_ns": null}],
  "next_cursor": null,
  "every_account": true}}
```

The call's record names its gate as `deployment admin` or `owner`.

## Trading instructions and account attributes

From contract v22. The **Trading instructions** page
(`/admin/trading-instructions`) and the Accounts tab's book part. See
[The order lifecycle](../concepts/the-order-lifecycle.md#trading-instructions)
and, at the page,
[Set trading instructions and whether releases wait](../how-to/set-trading-instructions.md).

The two acts are core acts at the setter's level: each can be prepared
([`dashboard__prepare_call`](#dashboard__prepare_call)), and each is at
**May not** for agents until the deployment admin loosens it. Each takes a
`note`, as every act does, kept as the book entry's reason. A list answers
`outcome: "unchanged"`; a reason another person or agent wrote is screened
as others' words. The book refuses and cancels nothing for an instruction:
each plugin honours it.

### `dashboard__list_trading_instructions`

The Trading instructions page, read only: every instruction in force for a
deployment admin, those naming a plugin they administer for a plugin's
admin.

**Input:** nothing.

**Answer:** `instructions`, each with its `target` (the contract's own
fields, only those set: `all_accounts`, `account_id`, `instance_id`,
`subject`, `service_account_id`), `target_said` (the target in words, as
the page shows it), `value` (`active`, `pause` or `stop`), `setter_level`
(`deployment_admin` or `plugin_admin`), `reason` (the note it was set
with, kept as the entry's reason), `set_by`, the
`entry_id` that set it and its `last_change` (`partition` and `sequence`);
and `control_sequence`, the sequence of the trading instructions as of the
read.

### `dashboard__set_trading_instruction`

The page's **Set an instruction** dialog.

**Input:**

| Argument | What it is |
|---|---|
| `target` | What it is on, the contract's fields, one target: `{"all_accounts": true}` (a deployment admin's); `{"instance_id": "…"}`, a plugin; or `account_id`, `subject` (a person, by their deployment-local subject) or `service_account_id`, each beside the plugin's `instance_id` where it is within one. A plugin's admin always names their plugin. A user group is not a target in v22, and `target.user_group_id` is refused |
| `value` | `active`, `pause` or `stop` |
| `note` | Why, kept as the instruction's reason |

The level is stamped from the caller's access, never an argument: a
deployment admin's, or a plugin admin's for a plugin they administer. A
target outside the caller's reach is refused `not_permitted`, naming
`target`.

**Answer:** `outcome: "made"` and `instruction`, as the list answers each.

```json
{"target": {"instance_id": "desk-1"}, "value": "pause",
 "note": "Pausing the desk's new orders while the venue is degraded."}
```

### `dashboard__list_account_attributes`

The Accounts tab's book part, read only: each account's attributes in the
book. No account's positions or orders.

**Input:** nothing.

**Answer:** `accounts`, each with its `account_id`, `base_currency_code`,
`lot_relief_default` (`first_in_first_out`, `last_in_first_out`,
`highest_cost`, `lowest_cost` or `average_cost`, empty where not set),
`waits_for_compliance` and `opening_balance_as_of`, the date its opening
balance stands for, empty for none.

### `dashboard__set_account_attribute`

An account's **Edit**, **In the book**: one attribute at a time, each its own
entry.

**Input:** `account_id`, `note` (kept as the entry's reason), and exactly one of `base_currency_code`
(three capital letters), `lot_relief_default` (as above) or
`waits_for_compliance` (`false` lets a release pass the gate without a
compliance verdict).

**Answer:** `outcome: "made"`, the account's `attributes` as they stand,
and the `entry_id`.

```json
{"account_id": "ACC-01JA2Q3R4S5T6V7W8X9Y0Z1A2B", "waits_for_compliance": false,
 "note": "No compliance plugin covers this account; releases are reviewed by the desk."}
```

## The Calendars tab

From contract v22. The Instruments page's
**Calendars** tab, at the deployment admin's level, read only: nothing sets
a calendar in a deployment. See
[Settlement calendars](../concepts/settlement-calendars.md).

### `dashboard__list_calendars`

The calendars and date rules the deployment holds, one line each at its
latest version.

**Input:** `cursor`, the `next_cursor` of the page before; `page_size`, 1
to 200. From contract v23, as the instrument store's list takes them:
`kind`, one calendar kind, none for every kind; and `query`, text matched,
ignoring case, on the name and the subject's codes.

**Answer:** `calendars`, each with its `calendar_id` (`CAL-…`), `name`,
`kind` (`CALENDAR_KIND_CURRENCY`, `CALENDAR_KIND_TRADING` or
`CALENDAR_KIND_SECURITIES_SETTLEMENT`), `version`, `coverage_to_date` and
`refreshed_at_ns`, and from contract v23 its subject as platform IDs:
`instrument_id` (a currency's cash instrument), `venue_ids`, or
`settlement_system` (its name and country); `rules`, each with its `kind`
(`DATE_RULE_KIND_SETTLEMENT` or `DATE_RULE_KIND_SPOT`), `subject` (such as
`US/equity`), `version` and `refreshed_at_ns`; and `next_cursor`, empty on
the last page.

### `dashboard__read_calendar`

One calendar's days over a range, as the tab shows a year.

**Input:** `calendar_id`; `from_date` and `to_date`, `YYYY-MM-DD`,
inclusive, `to_date` on or after `from_date`; `as_of_ns`, a recorded time,
absent or 0 for the latest version.

**Answer:** `found`, false for a calendar the deployment does not hold yet,
which is then asked of the platform; its `calendar_id` and `version`; its
`weekends`, each with its `weekdays` (`WEEKDAY_SATURDAY`, …) and
`valid_from_date`; the `days` listed in the range, each with its `date`,
`kind` (`CALENDAR_DAY_KIND_CLOSED`, or `CALENDAR_DAY_KIND_OPEN` for a
weekend day that is a business day), `name` and `source`; its `coverage`
(`from_date`, `to_date`); and its `sources`, each with its `source_id`,
`name`, `address` and `read_at_ns`. A read answers `outcome: "unchanged"`.

## Refusals

| `reason` | When |
|---|---|
| `not_listed` | The tool is not listed through this delegation, such as a settings tool called by a person holding only `write`; recorded like any call. Also a plugin that has not reported, so its settings are not known yet, and, on `dashboard__set_plugin_settings`, an instance the delegation does not reach. From contract v18, also a tool that changes something added after a narrowed delegation was consented to, saying it waits for fresh consent from that client. |
| `invalid_arguments` | An argument that does not read, or is not the tool's, by its path: a missing `note`, a secret's value (`secret.<name>`, `value.<name>`), a table's cell that does not read (`table.<name>[<row>].<column>`), an instance the delegation does not reach at that page's level, naming those it does. |
| `not_administered` | A setting serving a role the person does not administer, at its path, naming the roles. |
| `not_permitted` | From contract v22: a trading instruction on a target outside the caller's reach, at `target`, saying why; and a book's refusal sent with a permission status and no code. |
| `REFUSAL_REASON_RECORD_CHANGED` | The settings, or from contract v18 a source priority, changed since `against_updated_at_ns` was read, at that argument. Nothing was changed: read them again. |
| `prepare_only` | From contract v20: the act is at Prepare only for agents in this deployment, naming who set it. Prepare it with `dashboard__prepare_call`, and a person makes it. |
| `second_pair_of_eyes` | From contract v20: the act needs a second pair of eyes; nobody makes it directly. Prepare it, and someone other than whoever prepared it makes it. |
| the deployment's own | The same refusal the page meets, with its sentence: a window below a hold, write-once where the archive cannot lock, roles other than the version's, no live launch to stop. |
| `rate_limited`, `unavailable` | As for any tool on the surface. |

## Where a change is recorded

A change made through one of these tools is recorded as the same change
made at the page, and names the person, the delegation and the client, with
the note: in the deployment's configuration, a record for each setting
changed, each hold, each archive allowed or withdrawn, each launch and each
stop, and from contract v18 each dataset's licence and entitlement; in the
lake, each source priority. From contract v17 a launch or stop made with `meridian plugin` names
the CLI's delegation and client too. From contract v20 a change made from a
prepared change also names it (`prepared_call_id`), and each step of the
prepared change is its own record in the dashboard. From contract v21
each change to a service account, and to what a role
runs as, is its own record in the dashboard, made at the page; a call a
service account made is recorded on its own page, **Its calls**, not in
anyone's Connected clients. From contract v22 a
trading instruction or an account attribute set through a tool is an entry
in the book, as one set at the page is, with the person, the delegation,
the client and the note, kept as the entry's reason; and each change to a connectivity plugin's
availability, link or users, made at the page, is its own record in the
deployment's configuration.

Where a person sees it:

- **Connected clients**, under their name at the dashboard's top right,
  lists every call: when, which client, which tool, the gate it was admitted
  under, and how it came out. Never what was asked or answered.
- **The Settings form**, in a secret's field: who set it, when, and through
  which client, such as *Set by Ada, 2026-10-09 14:02 UTC, through Claude*.

Elsewhere the records say it and no page does yet: the client a setting,
hold, archive, launch or stop was changed through is answered by
`dashboard__read_plugin_settings` (`changes`), `dashboard__read_holds`,
`dashboard__read_plugin_summary` and `dashboard__read_moves` (`archive`),
and `dashboard__read_plugin_catalogue`. The note is kept with the change
and returned by the same read tools, beside who made it and the client, for
a setting, a hold, an archive allowed or withdrawn, and a launch, and from
contract v18 a stop (`stopped_note`), a licence, an entitlement and a
priority. No page shows a note yet, but for the Data sources page, where an
entitlement's or a priority's note shows on hover over who set it.

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
- [License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md):
  the Data sources page and its tools.
- [Service accounts](../concepts/service-accounts.md): the users a plugin's
  autonomous work runs as, and `dashboard__list_service_accounts`.
- [Set trading instructions and whether releases wait](../how-to/set-trading-instructions.md):
  the trading instructions and account attributes, at the page and through
  their tools (contract v22).
- [Settlement calendars](../concepts/settlement-calendars.md): the
  Calendars tab and its two tools (contract v22).
