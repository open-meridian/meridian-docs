# Licences and entitlements

Market data comes with terms. A deployment records two things about each
dataset in [the lake](the-lake.md), both set by a deployment admin and kept
by the deployment alone, never sent to the platform:

- its **licence**: the terms the lake keeps it on;
- its **entitlements**: which plugin instances may read it, and which of
  its fields.

A licence records what the admin entered. Neither it nor anything else in a
deployment says the deployment meets a vendor's or an exchange's terms:
reading those terms, and keeping to them, stays the firm's.

## The licence

A deployment admin sets each dataset's licence. Until one does, the
dataset is **kept and read, each use right restrictive**: the lake keeps its
rows with no retention bound, every field readable and shown, while derived
data stays inside the deployment, nothing is passed on, nothing is computed
outside the deployment, and every use the terms could list (training a
model, replicating the service, making an index) is prohibited. The Data
sources page says which: *not licensed: kept and read, each use right
restrictive*, or *set by* a person.

**The vendor's terms and pricing.** A data plugin describes each dataset's
terms in words: the sources behind the vendor, what it charges and on what
meters, and what it forbids, in at most 2,000 characters. Data sources shows
them in the vendor cell's title, the plugin's docs carry them, and
`dashboard__list_datasets` answers them in the catalogue entry, as the
plugin's words. They are what an admin, or the admin's agent, reads before
setting a licence. They grant nothing and are never enforced: the licence a
deployment admin sets is.

| Term | What it says |
|---|---|
| Kept | Whether the lake may keep the dataset's rows. Not kept, they are **served, not kept**: answered to the reader waiting and recorded only as served, never their values. |
| Retention | How many days a kept row stays, from when it was recorded, up to 36,500; 0 sets no limit. Past it the lake removes the row and records the removal. |
| Derived use | Whether data derived from it may be made. |
| Display | Whether it may be shown to people. Never redistribution outside the deployment, which no licence here grants. |
| Default fields | The fields readable by default, each by its [data dictionary](../boundaries/lake.md) entry, such as `meridian.v1.Bar.vwap`; none for every field. |
| One person's terms | Whether the terms are one person's, as a retail brokerage account holder's market data is (`personal_use`). |

**A licence a person sets replaces the one before it.** Setting the
licence on the Data sources page, or with `dashboard__set_dataset_licence`,
records what the person states, and keeps every term it does not state as
the licence held it. **Who may take it**: a licence may record who is
eligible to license the data at all, as a vendor's price list says
(the licence's `eligibility`): personal use, commercial use, or both, and
a buyer's annual revenue below or at least a threshold, in an ISO 4217
currency. `dashboard__list_datasets` answers it. It is shown, never
enforced: whether the firm is eligible is the deployment admin's to judge
from the terms.

**What the deployment counts.** Core keeps the deployment's counts of its use of a licensed dataset, display persons
and non-display plugins against the dataset's meters with their CSV
export, and the professional test a person answers on first access (see
[The lake: filings, quality states and data use](the-lake.md#not-served-yet)).

**The one-person warning.** A dataset whose terms are one person's is
flagged on the Data sources page, and in `dashboard__list_datasets`, where
more than one person holds `read` or `write` on a plugin entitled to it,
naming them: each person who has signed in, and each login a user group
names, signed in yet or not. It warns; it does not refuse. A deployment
enforces entitlements per plugin and per field, not yet per person.

**The data plugin knows its datasets' licences.** A data plugin reads the licence a deployment admin set on each
dataset its own catalogue declares, and no other's, so its **Datasets** page
says **Licensed** or **Not licensed yet** exactly, and the plugin's admin,
who sets no licence, sees what is still waiting for the deployment admin.
Every licence change is answered there with the plugin's next read.
A licence still says only what the admin entered.

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
per plugin instance like any other, with nothing more in the interface. So a
deployment admin can give the live trades to an `ems` plugin and the
closes to everything else. Trades and quotes are read only by plugins
holding `signal` or `ems`, whatever
they are entitled to: see [Who reads what](the-lake.md#who-reads-what).

## Which dataset a default read takes

A reader that names no dataset takes the deployment's **source priority**:
for each data type (prices, bars, trades and quotes), and for prices each kind (close, last, NAV, settlement), an
ordered list of datasets, first to last. A read falls
through to the next where one is silent beyond its cadence, stalled (no
sign of life within its stale ceiling), quarantined (its latest rows held
quarantined), does not cover the subject, or is not entitled, and says why.
With no priority set, a default read takes the datasets in the order the
lake lists them.

**Switched to backup source.** Each time a default read switches to the
next source, and each time it switches back, the lake records it: the data
type, the datasets from and to, the subjects, why (silent, stalled,
quarantined, or restored) and when. While a default read stands on a
backup, Data sources says **switched to backup source** on its priority's
row and in one line above the tabs, and the Summary of each data plugin
whose dataset it switched from or to says the same.
`dashboard__list_source_switches` reads them. A plugin holding a role that
reads the lake reads the priorities too, each with only the datasets it is
entitled to read, so its page can say where its values come from next.

## Gaps

In the HA configuration a data plugin's writes reach the lake through a
write-ahead stream that holds them for a bounded time
(`lake.writeAhead.maxAge`, 10 minutes). A lake writer gone longer than that
leaves a **gap** in each dataset whose writes the stream dropped. The lake
records it: its ID (`GAP-` and a ULID), the dataset (not yet known until
the dataset writes again), the subjects, the valid range, why and its
state. Where the dataset declares `backfill`, the lake asks its plugin for
the span again through the want and the gap is **refetching**, then
**recovered**; otherwise it is **unrecovered**. Rows inside a gap are never
invented: a read over it answers what was recorded.

Each gap is a line on Data sources' **Gaps** tab until it is recovered,
and a **Gap found** notice (`gap_found`) in every deployment admin's
inbox, once per gap. `dashboard__list_dataset_gaps` reads them.

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

The Data sources page has its tools on the deployment's MCP surface, at
the deployment admin's level: see
[Core's tools](../api/core-tools.md#the-data-sources-page). None reads a
price. A tool's answer is the page shown to the same person. Each of the
page's three acts, setting a licence,
an entitlement and a source priority, can also be
[prepared](prepared-changes.md) by an agent or a person, for the deployment
admin to make.

A plugin's own page reached through an agent answers what it shows the
person, prices included where the plugin shows them. An agent's client may
pass what it reads to its model's host; whether a vendor's terms allow that
is for those terms to decide, and a deployment admin licensing a dataset
should read them with that in mind.

## Related

- [License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md):
  the page and its tools, step by step.
- [Using a data plugin](../how-to/using-a-data-plugin.md#the-data-plugins):
  each data plugin's terms, summarised: Alpaca's, Tradier's, Tiingo's,
  Coinbase's, Kraken's, the Federal Reserve Board's, the New York Fed's,
  US Treasury's, FRED's and the ECB's.
- The data dictionary, field by field:
  [`DatasetLicence`](../boundaries/sidecar.md#meridian.v1.DatasetLicence),
  [`DatasetGap`](../boundaries/lake.md#meridian.v1.DatasetGap),
  [`DatasetEntitlement`](../boundaries/lake.md#meridian.v1.DatasetEntitlement)
  and [`SourcePriority`](../boundaries/lake.md#meridian.v1.SourcePriority).
