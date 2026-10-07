# Set a plugin's settings

A plugin declares the settings it needs in its code, and an admin of the
plugin gives them in the dashboard: on its **Settings** form, and each table
on a tab of its own beside it. Those are the only places a setting is set: a
plugin reads its settings as they arrive, and never sets one, its own
included. Every change is recorded, naming who made it.

From contract v14 a setting may also be a **table**: rows of typed columns,
such as, per account, a plan's own fund code and the instrument it is. This
page shows an admin how to fill the form and a table's tab, and a plugin's
developer how to declare a table and read its rows.

!!! note "Released 2026-10-05"
    This page describes open-meridian 0.19.0 (contract v14), on PyPI, with
    CLI 0.1.34, the runtime chart 0.1.262 and the SnapTrade plugin 0.11.1.
    The data dictionary marks the table setting's rows `preview` in the
    contract. A runtime serving v13 refuses a plugin built on 0.19.0, naming
    both versions.

## Open the form

Only an admin of the plugin sees it; a deployment admin is one through the
**All plugins (admin)** group, unless that permission was withdrawn (see
[To make someone a plugin's admin](administer-access.md#to-make-someone-a-plugins-admin)).
The same form, and the same tab for each table, is in two places:

- On the dashboard's home, choose **Manage** on the plugin, then its
  **Settings** tab, after **Summary**, and its tables' tabs after that.
- In the dashboard's admin view of the plugin, at `/admin/plugins/<instance>`,
  its **Settings** tab and its tables' tabs. A deployment admin reaches it
  from the **Plugins** tab of the dashboard's Settings.

The form fits one screen. Its head is one line: **Settings**, and who last
changed them (see [Who changed what](#who-changed-what)). Its settings are
grouped in tabs: **Required**, **Optional** and, on a
[development deployment](../concepts/development-deployments.md) alone,
**Developer**, for whoever develops the plugin. A group of more than six
fields goes on in another tab, such as **Optional 2**, and a tab says how
many of its required settings are missing, so none is left unseen behind
it. Without script every group shows, one under another, each under its
title.

Each field is under its label, marked required or optional. A choice is
radio buttons, and only the fields that apply to the choice made are shown. A
default is greyed in its empty field: the plugin uses it while nothing is
set, and it is never stored. Choose **Save settings**: it saves every group
as it stands, the ones not shown included, and the deployment checks every
value against what the plugin declared before it keeps any, and refuses the
save, saying why, when one does not read. Once saved, the settings reach the
plugin without a restart.

### On a plugin holding several roles

From contract v15 a person is an admin of a plugin's role rather than of the
plugin (see [Admin per role](../concepts/access.md#admin-per-role)), and a
plugin holding several roles names the roles each setting serves. The form
shows a setting to an admin of any role it serves, and lets only one holding
admin on every one of them change it. To an admin of some of them it is
shown read-only, saying which roles it serves, such as **Serves custody and
operations: set by an admin of every one**, and posts nothing; a change to
it from anyone else is refused before anything is sent, naming the roles
they do not administer. A setting declared before v15, naming no role,
serves every role the plugin holds. On a plugin holding one role, nothing
changes.

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

A table setting is not on the Settings form. It has a tab of its own, after
**Settings** and titled with the setting's label, such as SnapTrade's
**Plan-code links** and **Cash links**, holding the table alone and fitting
one screen. Its head is one line: the label, how many rows it holds of the
most the plugin allows, and who changed the latest row, and when. What the
table is for is one line under it.

The table is an entry grid: one line a row, its columns in the order the
plugin declared them, a typed input in each.

- **Add a row** adds one at the end, as Enter on the last row does, up to
  the most the plugin allows; **Remove** takes one away.
- Rows past what fits the screen are paged, with **Previous**, "Rows 1–8 of
  40" and **Next** under them. Every row is saved, whichever page shows.
- Cells copied from a spreadsheet and pasted into a cell fill across and
  down from it, adding rows as needed up to the most. The grid says how many
  rows it pasted and how many cells are left to fix.
- On a phone each row is one line, its first two columns and "…", which
  opens the whole row.

Choose **Save**: it sends this table whole, through the same checks as the
form, leaves every other setting as it stands, and comes back to the tab.
Without script the tab is a plain table of inputs, the rows held and up to
three blank ones below them; type into a blank row to add one, and clear
every cell of a row to remove it.

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
read is marked, and the tab names it by row and column, with its path, as in
**Plan-code links, row 3, Instrument: names no instrument record this
deployment holds (`plan_code_links[2].instrument`)**. Nothing is sent while
any cell is refused, and the deployment refuses an update whole rather than
keep part of it.

Each row carries who added or last changed it, and when. The deployment
stamps them when it stores the table, by its own clock; a row you leave as it
was keeps its own; the tab's head names who changed the latest. Nobody
types those stamps, and a plugin declaring a column named `changed_by` or
`changed_at` is refused when it registers.

A table is never a secret.

## Who changed what

Each **Settings** tab's head says, on one line beside its title, who made
the latest change, and when: **Last changed by** a person's name, and the
time in UTC, cut short where the line must be, the whole of it on hover. It
is read from the change records, so a clear counts as a change: where the
latest was the plugin's re-declaring a setting, it says **Last changed by
the plugin's re-declaring a setting, which cleared it**, and when.

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
re-declaration and no person. Give the setting again, on the form or on
its table's tab. A value held is also checked against the declaration as it
stands before it is delivered or shown, and one that does not read is
withheld.

## Declare a table setting, and read its rows

In the plugin's code, a table is a `meridian.Setting` whose kind is `list`,
with its columns. The dashboard draws it as a tab of its own titled with its
`label`, its columns in the order declared:

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
**Plan-code links** (`plan_code_links`), its own tab beside SnapTrade's
**Settings** under Manage:

| Column | What to give |
|---|---|
| Account | The external account the code is used on, chosen from those SnapTrade reported. Required. |
| Plan code | The code as SnapTrade names it in the account's activity, such as `OQKR`. Required. |
| Instrument | The deployment's instrument record the code stands for, found by searching. Required. |

One row links one code on one account; the table holds at most 200. An
activity under a linked code is reported as that instrument, and its
provenance names who added or last changed the row, and when, as the
deployment stamped them. A code nobody linked travels as reported, with no
instrument, and nothing is resolved by symbol. The plugin only reads the
table: no page of its own sets any setting, and its **Account links** tab
only shows how many plan-code links and cash links the settings hold. See
[The custodian's activity](../concepts/the-custodians-activity.md#snaptrade-0110).

From SnapTrade 0.12.0 (contract v15), activity
that arrived before a row was added is re-resolved too: on the read the
change wakes, each activity already recorded under that code on that account
is re-resolved as the row's instrument, naming who added or last changed the
row and when, beside the activity as it first arrived, which is kept.
Changing the row re-resolves them again; removing it sends nothing, and they
keep their latest resolution. A restart re-resolves nothing twice. See
[SnapTrade 0.12.0](../concepts/the-custodians-activity.md#snaptrade-0120-a-plan-code-linked-later).

### SnapTrade: cash links

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
   only where an admin of the plugin lists it in the table setting **Cash
   links** (`counted_as_cash`), its own tab beside SnapTrade's **Settings**
   under Manage. It is then added to the cash of the row's currency, and the
   provenance names who added or last changed the row, and when.

Its columns are in the order of Plan-code links':

| Column | What to give |
|---|---|
| Account | The external account it is on, chosen from those SnapTrade reported. Optional: blank applies the row to every account holding the symbol, and a row naming the account comes before a blank one. |
| Symbol | The position as SnapTrade names it, such as `FDIC99532`. Required. |
| Currency | The ISO 4217 code of the cash it is, such as `USD`. Required. |

The table holds at most 200 rows. In SnapTrade 0.11.0 it was labelled
Positions counted as cash, the account its last column; 0.11.1 relabels it
and moves the account first, the setting's name unchanged, and a row saved
in the old order reads the same. A money market fund stays a fund, whatever
lists it. A row whose currency is not an ISO 4217 code or differs from the
currency SnapTrade states for the position, or a position with no price,
counts nothing: the plugin says so and sends the position as it is. Where
SnapTrade marks the position itself, its flag decides and the row is not
read. The **Statements** page says, beside a cash row, which deposit it
stands for and whether SnapTrade marked it or a person listed it.

A position that becomes cash leaves the account's next statement. Where the
book holds it, from an opening balance say, the difference shows as a break,
which a person confirms once, as an adjustment.

### An edge plugin's windows

From contract v16 every plugin at the edge that
declares kinds of raw record has two settings per kind on this form, the
same for every such plugin: *Kind*: **window**, in days, and *Kind*: **past
the window**, archived, kept or deleted. SnapTrade 0.13.0's are **Reported
activity: window** and **Raw responses: window**, with a past-the-window
choice for each; they replace 0.12.0's **Keep activity records for** and
**Keep raw responses for**, whose values are not carried over. The
deployment refuses a window below the hold over the plugin, and archived
where no archive is allowed. See
[Set a plugin's windows](keep-older-records-in-the-archive.md#set-a-plugins-windows)
and [Upgrade SnapTrade to 0.13.0](keep-older-records-in-the-archive.md#upgrade-snaptrade-to-0130).

## Related

- [Plugins, roles and grants](../concepts/plugins.md#manage-open-and-view):
  the tabs under Manage.
- [Give people access](administer-access.md#to-make-someone-a-plugins-admin):
  making a plugin's admins.
- [Python SDK](../api/python-sdk.md#settings): `settings()`, `Setting`,
  `Column` and `Settings`.
- [The sidecar](../boundaries/sidecar.md#meridian.v1.SettingColumn): each
  field of a table's declaration in the data dictionary.
