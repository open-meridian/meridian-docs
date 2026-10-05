# Set a plugin's settings

A plugin declares the settings it needs in its code, and an admin of the
plugin gives them on the dashboard's **Settings** form. That form is the one
place a setting is set: a plugin reads its settings as they arrive, and never
sets one, its own included. Every change is recorded, naming who made it.

From contract v14 a setting may also be a **table**: rows of typed columns,
such as, per account, a plan's own fund code and the instrument it is. This
page shows an admin how to fill the form, table included, and a plugin's
developer how to declare a table and read its rows.

!!! note "Built, not released"
    This page describes open-meridian 0.19.0 (contract v14) on a runtime
    serving v14, built and not yet released. The table setting is `preview`
    in v14. A runtime serving v13 refuses a plugin built on 0.19.0, naming
    both versions.

## Open the form

Only an admin of the plugin sees it; a deployment admin is one through the
**All plugins (admin)** group, unless that permission was withdrawn (see
[To make someone a plugin's admin](administer-access.md#to-make-someone-a-plugins-admin)).
The same form is in two places:

- On the dashboard's home, choose **Manage** on the plugin, then its
  **Settings** tab, after **Summary**.
- In the dashboard's admin view of the plugin, at `/admin/plugins/<instance>`,
  its **Settings** tab. A deployment admin reaches it from the **Plugins** tab
  of the dashboard's Settings.

Each field is under its label, marked required or optional. A choice is
radio buttons, and only the fields that apply to the choice made are shown. A
default is greyed in its empty field: the plugin uses it while nothing is
set, and it is never stored. A setting meant for whoever develops the plugin
is shown only on a [development deployment](../concepts/development-deployments.md).
Choose **Save**: the deployment checks every value against what the plugin
declared before it keeps any, and refuses the save, saying why, when one does
not read. Once saved, the settings reach the plugin without a restart.

## A secret

A secret, such as a vendor's API key, is write-only. Its field is always
empty and says only **set** or **not set**. Typing into it replaces the
value; leaving it empty leaves it as it is; ticking **Clear it** removes it.
Nobody reads a secret back, a deployment admin included: it is never shown,
logged, reported or bundled, and is sealed before it is stored. A setting held
sealed stays a secret whatever the plugin declares of it later. Nothing about
secrets changed in v14.

## A table setting

A table setting is an editable table on the form: one line a row, a typed
input in each column, the rows held and up to three blank ones below them,
within the most rows the plugin allows. Type into a blank row to add one;
clear every cell of a row to remove it. Saving sends the table whole.

The dashboard checks every cell as you type and again before it sends
anything, and the deployment checks every cell again before it stores
anything, so the two refuse alike:

| Column | A cell must be |
|---|---|
| Text | Any text, at most 500 characters. |
| Integer | A whole number. |
| Decimal | An exact decimal, such as `12.5`, at most 18 places. |
| Date | A real date, `YYYY-MM-DD`. |
| Choice | One of the column's options, chosen from them. |
| External account | One of the external accounts this plugin reported, chosen from them. |
| Instrument | One of the deployment's instrument records, found by searching them and held by its ID, never a symbol. One the deployment does not hold is refused. |

A column marked required must be filled on every row. A cell that does not
read is marked, and the form names it by row and column, with its path, as in
**Plan-code links, row 3, Instrument: names no instrument record this
deployment holds (`plan_code_links[2].instrument`)**. Nothing is sent while
any cell is refused, and the deployment refuses an update whole rather than
keep part of it.

Each row carries who added or last changed it, and when. The deployment
stamps them when it stores the table, by its own clock; a row you leave as it
was keeps its own. Below the table the form says how many rows it holds and
who changed the latest, and when. Nobody types those stamps, and a plugin
declaring a column named `changed_by` or `changed_at` is refused when it
registers.

A table is never a secret.

## Who changed what

Above the form, each **Settings** tab says who made the latest change, and
when: **Last changed by** a person's name, and the time in UTC.

Behind it, from contract v14, every change is its own record in the
deployment's configuration: which setting, whether it was set or cleared, the
value it was set to, who, through which delegation where they used one, and
when. A secret's record says only that it was set or cleared, never its value.

The changes made before v14 were recorded with who and when, and without the
value. Where the setting still holds the value its latest change set, that
change's record is filled in from it, and says so. For every setting changed
before v14, one more record says the earlier values are not known before the
moment the deployment was upgraded, by the deployment's clock. Nothing is
back-dated or guessed.

## Declare a table setting, and read its rows

In the plugin's code, a table is a `meridian.Setting` whose kind is `list`,
with its columns:

```python
import meridian
from meridian import edge

PLAN_CODES = meridian.Setting(
    "plan_code_links",
    list,
    label="Plan-code links",
    description="A plan's own fund code on an account, and the instrument it is",
    columns=(
        meridian.Column("account", "external_account", label="Account", required=True),
        meridian.Column("code", label="Plan code", required=True),
        meridian.Column("instrument", "instrument", label="Instrument", required=True),
    ),
    most_rows=200,
)

async with await meridian.connect(settings=[PLAN_CODES], reads_external_accounts=True) as plugin:
    async for current in plugin.settings():
        links = {
            (row["account"], row["code"]): row
            for row in current.values.get("plan_code_links", [])
        }
```

A column's kind is `"text"` (the default), `"integer"`, `"decimal"`,
`"date"`, `"choice"` with its `choices`, `"external_account"` or
`"instrument"`. `most_rows` bounds the table, at most 500, which is also what
0 means. A table has no default and is never secret; the SDK refuses either,
an unknown kind, a column named twice or named `changed_by` or `changed_at`,
and a choice column without options, before the plugin registers.

The table arrives in `Settings.values` as a list of rows, every time any
setting changes. Each row is a `dict` of its cells as text, by column name,
with `changed_by`, the person who added or last changed it, and `changed_at`,
when, in RFC 3339 UTC. Hold the latest delivery, as for any setting: the
plugin keeps nothing of its own.

A value a person supplied is evidence of who said so. Where a row decides
something the plugin reports, such as the instrument an activity names, carry
the row's stamps into its provenance:

```python
row = links.get((external_account_id, plan_code))
if row is not None:
    instrument_id = row["instrument"]
    provenance = [edge.supplied("instrument_id", f"{row['changed_by']}, {row['changed_at']}")]
```

See [Report the custodian's activity](report-the-custodians-activity.md#convert-each-activity)
for where that provenance goes, and
[`Setting`](../api/python-sdk.md#setting) and
[`Column`](../api/python-sdk.md#column) for every field.

## In the plugins

### SnapTrade: plan-code links

!!! info "To be filled when SnapTrade 0.11.0 lands"
    SnapTrade 0.11.0 declares its plan-code links as the table setting
    `plan_code_links`. This section will say how an admin fills it once that
    version is released.

## Related

- [Plugins, roles and grants](../concepts/plugins.md#manage-open-and-view):
  the tabs under Manage.
- [Give people access](administer-access.md#to-make-someone-a-plugins-admin):
  making a plugin's admins.
- [Python SDK](../api/python-sdk.md#settings): `settings()`, `Setting`,
  `Column` and `Settings`.
- [The sidecar](../boundaries/sidecar.md#meridian.v1.SettingColumn): each
  field of a table's declaration in the data dictionary.
