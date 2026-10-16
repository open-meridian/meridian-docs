# One ID per instrument

Every instrument a deployment holds is named by the
platform master's ID, `INS-` followed by a unique value, once the platform
holds it. Two deployments holding one security name it by one ID. The
platform mints that record; a deployment mints no permanent ID of its
own.

A deployment still keeps working when the platform cannot answer. It then
keeps a **local record** of its own, under an `LCL-` ID, until the
platform answers. This page explains both, what a person sees of each, and
what a plugin needs to know.

## An `INS-` record: minted by the platform

When a plugin reports a security nothing in the deployment matches, the
instrument store picks the security's **template** from the class and type
the source stated, and the conductor asks the platform to match or mint it.

The request only says **what to look for**:

- the identifiers the record carries in schemes on the platform's
  [licence list](#the-licence-list);
- the template;
- what the source states of the security, sent as offers.

It never carries a holding, a quantity, an account, a price paid, a value
from a licensed vendor's feed, the `LCL-` ID or who is asking.

**The platform verifies the security against a source of its own**:
OpenFIGI for a security a FIGI identifies, the listing venue's reference
data for a binary event contract or a crypto asset, the ISO 4217 list for a
currency. Confirmed, and its template met, the platform mints the record
from its source's values, not from what the request said. If the source
does not confirm it, the request goes to the platform's staff to review.
For venues with many listings the platform also mints ahead of demand.

If the answer arrives within a short, bounded wait, the deployment keeps
the record under the platform's `INS-` ID from the start, and nobody acts.

### Templates

Every record names its **template** and the template's version. The
platform writes, versions and publishes every template, and a published
version never changes. Each asset class has a **base template**:
identifiers, a description and a currency. A type's template adds its
terms.

The first six templates are cash and currency, crypto asset, equity, fund,
money market fund and binary event contract, each matching on identifiers
only. They ship with every core release, so a deployment that has never
reached the platform still names a record's template and what it lacks.
The conductor pulls newer versions daily and on reconnecting.

## An `LCL-` record: a local record until the platform answers

The instrument store mints a **provisional** record of its own, under an
`LCL-` ID, when no `INS-` record answers:

- the platform was not reached within the bounded wait;
- the platform's staff must review the request;
- the security has no identifier the platform may be sent, such as a
  vendor's own code alone.

So a data plugin that names a security only by its vendor's own symbol
gets a local record for it, and the lake never prices a local record. For
the security to be priced, its record needs an identifier the platform can
match, such as a FIGI.

The local record carries the vendor's identifiers, which never leave the
deployment, names its template, and lists any fields it lacks. The prefix
`LCL-` only says that the deployment minted the ID. Whether a record is
still waiting is its `provisional` field.

**The minimum** for any record is an identifier (a vendor's own code
counts), a description and a currency, each as the source stated it.

### Why a thinly described security stays unrecognised

A source thinner than that minimum, such as a statement line with a code
and nothing else, makes **no record**. There is one master for every
deployment, and a record built from too little would be a guess: it could
match the wrong security, or mint a duplicate beside the right one.

So the holding is kept in the street as a **placeholder**, outside the
book, carrying the identifiers the statement gave. On reconciliation the
`operations` plugin records it as a break of its own kind, an
**unrecognized security** (`BREAK_CATEGORY_UNRECOGNIZED_SECURITY`),
naming the street record and its identifiers. It stays visible while it
persists.

Once the source, or a person, gives what the minimum needs, the next
resolve makes the record, and the next statement records the position on
it.

### A local line is never priced

In the book a position under a local record is a **local line**: the
quantity and the cost the statement gives, lots and all, recorded and
reconciled as any position. It has **no price, valuation or analytics**. A
reader shows it as not priced because it is a local record, never valued
at zero, and the lake is never asked a price for it.

The home page counts the local records: "4 provisional instrument records,
the oldest 12 days: local records, not priced, until the platform
answers", with **See why** opening the Instruments page's
[Provisional tab](../how-to/review-provisional-records.md#the-provisional-tab).

A record still lacking an asset class ("class needed") is refused by the
book until a person sets its class on the **Instruments** page, as any
record the book cannot use is, because the book's lot rules follow the
class.

### Why a record is provisional

Each provisional record says why, in words, on the Instruments page and to
its tools:

- **The platform not reached**: asked again on reconnecting
  (`PROVISIONAL_REASON_UNREACHABLE`).
- **Incomplete or offline**: the fields its template wants that it lacks
  are listed, or it carries nothing on the licence list to look for yet
  (`PROVISIONAL_REASON_INCOMPLETE`).
- **With the platform's staff**: asked again daily
  (`PROVISIONAL_REASON_AWAITING_STAFF`).
- **Class needed**: the source stated no asset class, so no template is
  named yet (`PROVISIONAL_REASON_CLASS_NEEDED`).
- **Held back at the migration**: a deployment admin held its line back
  at the upgrade (`PROVISIONAL_REASON_HELD_BACK`; see
  [Review provisional records and the migration](../how-to/review-provisional-records.md)).

## When the platform answers

A provisional record **resolves** without anybody acting once the platform
answers for it: on reconnecting, from the staff's review, or by a backfill
once the licence list names a scheme the record carries.

- The `INS-` record starts from the local record: every value in force,
  each with its original source, person and time; its offers; its
  identifiers with their windows. The platform's differing values arrive as
  offers, never over a person's.
- The `LCL-` ID stays on it for life as an identifier under the
  deployment-only scheme `open_meridian_local`. It is accepted on every
  write, answered as the record it became, and never leaves the
  deployment.
- The record's history reads across the link, its first version naming the
  resolution.
- Positions, lots and pending settlements move to the `INS-` record. Two
  local records answered by one `INS-` ID are both replaced by it, and the
  book sums them.

**Nothing is rewritten.** Journal entries, holding rows, orders,
executions and rows in the lake keep the ID they were recorded with. A
read naming a replaced ID answers for the record it became, and every
check of "the same instrument" compares the record each ID became. An
instrument cell in a plugin's table setting is re-pointed by core as a
recorded settings change, so the page and the plugin show one ID.

**The replacement feed.** When the platform's staff merge two `INS-`
records, or decommission one, the conductor reads it from the platform's
feed, daily and on reconnecting. A held record the platform merged is
followed automatically. A decommission is shown on the record and never
moves a position. Every deployment reads the same feed, so the platform
never learns what one holds.

## Orders on local records

An order may name a local record while the deployment's setting **Allow
orders on local records** is on, as it is by default. It is an escape
hatch, for when the platform cannot be reached: the order is marked
"local record: not priced".

A deployment admin turns it off on the **Trading instructions** page (see
[Allow orders on local records](../how-to/set-trading-instructions.md#allow-orders-on-local-records)).
Off, from the change on:

- a new order naming a local record is refused,
  `REFUSAL_REASON_LOCAL_RECORD_NOT_ALLOWED`;
- accepting a venue-originated fill on one is refused the same way;
- orders already working on a local record continue, with their placements
  and child orders: to stop them, set a trading instruction;
- an order the `oms` records for a telephoned or outside order is recorded
  whatever the setting.

The page and the home page show how many live orders name a local record,
a count naming no account and no order.

## The licence list

The platform publishes a **licence list**: the identifier schemes it may
be sent, its version, and the pace a batch may be sent at. The conductor
pulls it daily and on reconnecting, and the instrument store filters every
request by it before anything is sent. A value in a scheme not on the list
never reaches the platform, whatever a plugin reported.

With no list read yet, only the open schemes are sent: FIGI (including the
share-class and composite FIGI), LEI, a ticker with its venue, CAIP-19,
ISO 4217 and the SEC's series and class IDs. `open_meridian_local` and the
`LCL-` ID are never on it.

When the list gains a scheme, the deployment **backfills**: each local
record carrying that scheme is sent, exact matches resolve automatically,
and uncertain ones become prepared changes for a person. The Provisional
tab counts each backfill.

Which identifiers a deployment may hold, and under what terms, is the
deployment's to settle with its vendors. The list only says what the
platform accepts.

## Usage reporting

Weekly, the conductor sends the platform the deployment's **identifier
usage** for the last whole week, Monday to Sunday: per identifier scheme,

- how many records carry it;
- how many resolve only through it;
- how many misses arrived with it as their only identifier;

with the period. **Counts only**: never an identifier's value, a holding, a
quantity or an account. The report has room for the schemes the deployment
declares it is licensed for, but a deployment cannot declare them yet, so
that list is sent empty. The first weekly report after the upgrade's
migration carries its effect; a report the platform did not receive is not
sent again, the next week's replacing it.

It is **on by default**. A deployment admin turns it off at the
Instruments page's **Licensed identifiers** tab, **Report identifier
usage**, with a reason; each change is its own record. The tab lists each
report sent, its period, how many schemes it counted and whether the
platform received it.

## Through an agent

The Instruments tools take and answer the one-ID model's fields (see
[Core's tools](../api/core-tools.md)):

- `dashboard__list_instruments_to_complete` takes `provisional`, the
  provisional records alone, each with its `provisional_reason`; every
  record answers `provisional`, `template_id`, `template_version` and
  `missing_fields`; and the answer carries `migration_counts` and
  `backfill_counts`.
- `dashboard__apply_migration` makes the upgrade's migration lines, or
  holds lines back, with a note; agents may only prepare it until a
  deployment admin loosens it.
- `dashboard__set_reports_usage` turns the usage report on or off, with a
  note.
- `dashboard__set_local_record_orders` turns orders on local records on or
  off, with a note, and answers the count of live orders on local records.

## For a plugin's author

- **IDs are opaque.** A plugin needs no change to keep working: a resolved
  `LCL-` ID is accepted on every write, forever.
- **Ask `provisional`, not the prefix.** A resolve answers whether the
  record is provisional (`ResolveIdentifierResult.provisional`); an `LCL-`
  record may be resolved, and stays `LCL-`.
- **No `open_meridian` identifier is written.** The record's `instrument_id`
  is the platform's ID.
- **Every role hears a replacement**, and catches up with
  `list_replacements`; the SDK keeps a current-ID map from both, for a
  plugin that keeps instrument IDs in its own storage. Every role also
  reads the templates (`list_templates`, `read_template`).
- [`meridian plugin migrate`](../api/cli.md#plugin-migrate) rewrites the
  first two for you, and `meridian plugin check` warns
  (`replaced-ids-followed`), failing nothing, on an `INS-` or `LCL-` ID kept
  as a string in the plugin's code outside its tests.

## Known limits

- **A local line is not valued.** Until its record resolves, a position on
  it has no price in the book, the lake or any reading built on them.
- **A thin statement line stays outside the book** until its source or a
  person gives an identifier, a description and a currency.
- **Some securities wait for the platform's staff.** One the platform's
  source cannot confirm stays provisional until staff review it.

## Related

- [Instruments](instruments.md): identity, dated resolution and the
  instrument store.
- [Review provisional records and the migration](../how-to/review-provisional-records.md):
  the Instruments page's Provisional tab, and the upgrade's migration.
- [The book of record](the-book-of-record.md): positions, lots and
  reconciliation.
