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
sealed is never shown, whatever the plugin declares of it later: a plugin
re-declaring it as not secret clears it (see
[A setting re-declared](#a-setting-re-declared)). What changed for secrets in
v14 is in their records: a setting that becomes secret has its earlier plain
values redacted (see [Who changed what](#who-changed-what)).

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
| Text | One line of plain text, at most 500 characters: no newline or tab, and no control character, nor one that hides or reorders what a reader sees (a bidirectional override, a zero-width, tag or private-use character). |
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
when: **Last changed by** a person's name, and the time in UTC. It is read
from the change records, so a clear counts as a change: where the latest was
the plugin's re-declaring a setting, it says **Last changed by the plugin's
re-declaring a setting, which cleared it**, and when.

Behind it, from contract v14, every change is its own record in the
deployment's configuration: which setting, whether it was set or cleared, the
value it was set to, who, through which delegation where they used one, and
when. A secret's record says only that it was set or cleared, never its value.

Records are never changed or deleted, with one exception. When a setting
becomes secret, because the plugin re-declares it secret or its value is
stored sealed, the plain values its earlier records hold are redacted: each
value is blanked, and every record stays, with who and when. The redaction is
a record of its own, saying which records it blanked and why, made by no
person, and when. On upgrading to v14, the deployment redacts the records of
every setting already secret, at its own clock as it upgrades.

The changes made before v14 were recorded with who and when, and without the
value. Where the setting still holds the value its latest change set, that
change's record is filled in from it, and says so. For every setting changed
before v14, one more record says the earlier values are not known before the
moment the deployment was upgraded, by the deployment's clock. Nothing is
back-dated or guessed.

### A setting re-declared

A plugin's new version may declare a setting it already had with another
type, such as text become a table, or as secret where it was not, or the
reverse. The value the deployment held for it is then cleared when the
version registers, and the clear is its own record, naming the
re-declaration and no person. Give the setting again on the form. A value
held is also checked against the declaration as it stands before it is
delivered or shown, and one that does not read is withheld.

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

A retirement plan may report a fund under a code only the plan uses, such as
Fidelity's `OQKR` for the plan's VIGIX. SnapTrade 0.11.0 resolves such a code
only where an admin of the plugin has linked it, in the table setting
**Plan-code links** (`plan_code_links`) on SnapTrade's **Settings** tab:

| Column | What to give |
|---|---|
| Account | The external account the code is used on, chosen from those SnapTrade reported. Required. |
| Plan code | The code as SnapTrade names it in the account's activity, such as `OQKR`. Required. |
| Instrument | The deployment's instrument record the code stands for, found by searching. Required. |

One row links one code on one account; the table holds at most 200. An
activity under a linked code is reported as that instrument, and its
provenance names who added or last changed the row, and when, as the
deployment stamped them. A code nobody linked travels as reported, with no
instrument, and nothing is resolved by symbol. The plugin only
reads the table: no page of its own sets it, and its **Account links** tab
says only how many links the settings hold. See
[The custodian's activity](../concepts/the-custodians-activity.md#snaptrade-0110).

### SnapTrade: positions counted as cash

<!-- PENDING the product owner's confirmation (2026-10-05): the setting's
name, counted_as_cash, and its label were proposed at the build of
meridian-snaptrade 360e40e. Check both before publishing. -->

Whether a custodian's position is cash or a holding is the plugin's to
decide, from what its vendor says; the street and operations take what it
sends. A custodian may hold an account's cash as something else, such as
Fidelity's FDIC-insured bank deposit as an IRA's core position
(`FDIC99532`), which SnapTrade reports as a position beside the cash.
SnapTrade 0.11.0 decides in this order:

1. **SnapTrade's own flag first.** A position SnapTrade marks a cash
   equivalent that is not a fund is already counted in the cash it reports
   for that currency, so the plugin does not send it separately: the cash row
   stands for it, its quantity and value derived by a named rule that names
   the position's symbol and SnapTrade's description. With no price, no cash
   in its currency, or worth more than that cash, the statement is withheld
   and the **Statements** page says why.
2. **Else the admin's table.** A position SnapTrade does not mark is cash
   only where an admin of the plugin lists it in **Positions counted as
   cash** (`counted_as_cash`) on SnapTrade's **Settings** tab. It is then
   added to the cash of the row's currency, and the provenance names who
   added or last changed the row, and when.

| Column | What to give |
|---|---|
| Symbol | The position as SnapTrade names it, such as `FDIC99532`. Required. |
| Currency | The ISO 4217 code of the cash it is, such as `USD`. Required. |
| Account | The external account it is on, or blank for every account holding it. A row naming the account comes before a blank one. |

The table holds at most 200 rows. A money market fund stays a fund, whatever
lists it. A row whose currency is not an ISO 4217 code or differs from the
currency SnapTrade states for the position, or a position with no price,
counts nothing: the plugin says so and sends the position as it is. Where
SnapTrade marks the position itself, its flag decides and the row is not
read. The **Statements** page says, beside a cash row, which deposit it
stands for and whether SnapTrade marked it or a person listed it.

A position that becomes cash leaves the account's next statement. Where the
book holds it, from an opening balance say, the difference shows as a break,
which a person confirms once, as an adjustment.

## Related

- [Plugins, roles and grants](../concepts/plugins.md#manage-open-and-view):
  the tabs under Manage.
- [Give people access](administer-access.md#to-make-someone-a-plugins-admin):
  making a plugin's admins.
- [Python SDK](../api/python-sdk.md#settings): `settings()`, `Setting`,
  `Column` and `Settings`.
- [The sidecar](../boundaries/sidecar.md#meridian.v1.SettingColumn): each
  field of a table's declaration in the data dictionary.
