# Licences and entitlements

Market data comes with terms. A deployment records two things about each
dataset in [the lake](the-lake.md), both set by a deployment admin and kept
by the deployment alone, never sent to the platform:

- its **licence**: the terms the lake keeps it on;
- its **entitlements**: which plugin instances may read it, and which of
  its fields.

!!! note "Contract v18"
    This page describes contract v18, core's lake, from chart 0.1.292.

A licence records what the admin entered. Neither it nor anything else in a
deployment says the deployment meets a vendor's or an exchange's terms:
reading those terms, and keeping to them, stays the firm's.

## The licence

Each dataset has the licence its plugin's catalogue declares by default,
what the vendor's standard terms say, until a deployment admin sets the
deployment's own, which confirms or replaces it. The one enforced is shown
on the Data sources page with where it came from: *the catalogue's default*,
or *set by* a person.

| Term | What it says |
|---|---|
| Kept | Whether the lake may keep the dataset's rows. Not kept, they are **served, not kept**: answered to the reader waiting and recorded only as served, never their values. |
| Retention | How many days a kept row stays, from when it was recorded, up to 36,500; 0 sets no limit. Past it the lake removes the row and records the removal. |
| Derived use | Whether data derived from it may be made. |
| Display | Whether it may be shown to people. Never redistribution outside the deployment, which no licence here grants. |
| Default fields | The fields readable by default, each by its [data dictionary](../boundaries/lake.md) entry, such as `meridian.v1.Bar.vwap`; none for every field. |
| One person's terms | Whether the terms are one person's, as a retail brokerage account holder's market data is (`personal_use`). |

**The one-person warning.** A dataset whose terms are one person's is
flagged on the Data sources page, and in `dashboard__list_datasets`, where
more than one person holds `read` or `write` on a plugin entitled to it,
naming them: each person who has signed in, and each login a user group
names, signed in yet or not. It warns; it does not refuse. A deployment
enforces entitlements per plugin and per field in v18, not per person.

## Entitlements

An entitlement names a dataset, a running plugin instance, and the fields it
may read: every field, or a list, each a dictionary entry of the dataset's
data types. Withdrawing one clears its fields. A plugin with no entitlement
to a dataset reads none of it, whatever its roles allow.

The deployment enforces an entitlement in three places:

1. **The bus.** Only a plugin entitled to a dataset may subscribe to its
   subject. The deployment writes each launched plugin's entitled datasets
   into its bus permissions as the entitlement changes.
2. **The plugin's sidecar**, which strips the fields its plugin may not read
   from every delivery and every answer.
3. **The lake**, which answers a read only from entitled datasets and
   fields, and names each dataset or field it did not answer, with the
   reason `not entitled`.

An entitlement follows at once: a newly entitled plugin starts hearing the
dataset, and a withdrawn one stops. Entitlements per person, derived from
each person's access to a plugin and the data the plugin depends on, are
specified for later.

**A pricing tier is a dataset.** A source's higher-resolution feed, or its
data at a different price, is a dataset of its own, licensed and entitled
per plugin instance like any other, with nothing more in the contract. So a
deployment admin can give the live trades to an `ems` plugin and the
closes to everything else. Trades and quotes are read only by plugins
holding `signal` or `ems` (contract v19, built, not released), whatever
they are entitled to: see [Who reads what](the-lake.md#who-reads-what).

## Which dataset a default read takes

A reader that names no dataset takes the deployment's **source priority**:
for each data type (prices, bars, and from contract v19 trades and
quotes), and for prices each kind (close, last, NAV, settlement), an
ordered list of datasets, first to last. A read falls
through to the next where one is silent beyond its cadence, does not cover
the subject, or is not entitled, and says why. With no priority set, a
default read takes the datasets in the order the lake lists them.

A priority is replaced whole, against the priority as it was read: a change
made from a reading older than another person's change is refused as
changed, and nothing is lost. Each priority keeps who set it, when, through
which delegation and client, and why, so "which source served the default
on that date" is a question the record answers.

## Every change is its own record

Each licence, entitlement and priority set is its own record: who, what, to
what, when, the delegation and client where an agent made it, and the note
saying why. A note is required through the tools, and optional at the page.

## Through an agent

The Data sources page has five tools on the deployment's MCP surface, at
the deployment admin's level: see
[Core's tools](../api/core-tools.md#the-data-sources-page). None reads a
price. A tool's answer is the page shown to the same person.

A plugin's own page reached through an agent answers what it shows the
person, prices included where the plugin shows them. An agent's client may
pass what it reads to its model's host; whether a vendor's terms allow that
is for those terms to decide, and a deployment admin licensing a dataset
should read them with that in mind.

## Related

- [License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md):
  the page and its tools, step by step.
- [Add a data plugin's key](../how-to/add-a-data-plugins-key.md): Alpaca's,
  Tradier's and Tiingo's terms, summarised; and
  [Add a public data plugin](../how-to/add-a-public-data-plugin.md):
  Coinbase's, Kraken's and the Federal Reserve Board's.
- The data dictionary, field by field:
  [`DatasetLicence`](../boundaries/sidecar.md#meridian.v1.DatasetLicence),
  [`DatasetEntitlement`](../boundaries/lake.md#meridian.v1.DatasetEntitlement)
  and [`SourcePriority`](../boundaries/lake.md#meridian.v1.SourcePriority).
