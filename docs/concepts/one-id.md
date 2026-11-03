# The instrument master

A deployment keeps its own **instrument master**: the instrument store holds
a record for every instrument the deployment uses, and every holding, order,
price and position names one by its ID. Records are made, completed and
brought in inside the deployment, on the dashboard's **Instruments** page or
through its tools.

## A record { #an-ins-record-minted-by-the-platform }

When a plugin reports a security nothing in the deployment matches, the
instrument store makes a record from what the source stated: its
**template**, picked from the class and type the source gave, its
identifiers, a description and a currency. A record lists the fields its
template wants that it lacks until it is complete, and a person completes it
on the **Instruments** page.

Each record has one ID:

- **`INS-`**, the shared ID, which the same security carries in every
  deployment (see [The platform's security master](#the-platforms-security-master));
- **`LCL-`**, the deployment's own, for a record that is **provisional**:
  waiting for its shared ID, or lacking what it needs.

The prefix only says where the ID came from. Whether a record is still
waiting is its `provisional` field.

**The minimum** for any record is an identifier (a vendor's own code
counts), a description and a currency, each as the source stated it.

**Finding and bringing an instrument in.** The instrument picker searches
by what is typed, a ticker, a name, an ISIN, a CUSIP or a FIGI, and answers
with the deployment's records and candidates; a candidate chosen is brought
in, matched to a record the deployment holds or made a new one
(`dashboard__find_instruments` and `dashboard__bring_in_instrument` through
an agent). A record's values can be asked of open sources again; what comes
back arrives as offers on the record, never in force until a person accepts
them.

### Templates { #templates }

Every record names its **template** and the template's version, and a
published version never changes. Each asset class has a **base template**:
identifiers, a description and a currency. A type's template adds its
terms: cash and currency, crypto asset, equity, fund, money market fund and
binary event contract; the [listed option, future and future
option](listed-options-and-futures.md); the [bond, pool, TBA, CMO tranche and
CD](bonds-and-fixed-income.md); and a commodity future's underlying. The
templates ship with every core release, so a deployment names a record's
template and what it lacks from its own copy, and newer versions are pulled
daily.

Each field of a template states its **requirement**: `mint`, needed to make
the record; `complete`, needed before the book takes it; or `optional`; and
whether it is `repeated`. A template version's calculation package binds its
pricing model by term (`model_bindings`). A withdrawn version stays readable
and runnable; new records use its successor (`successor_version`).

## A provisional record { #an-lcl-record-a-local-record-until-the-platform-answers }

A record is provisional, under an `LCL-` ID, while:

- it carries no identifier its shared ID can be found by, such as a
  vendor's own code alone;
- it lacks fields its template wants;
- its shared ID has not been answered yet.

Each says why, in words, on the Instruments page and to its tools:
`PROVISIONAL_REASON_UNREACHABLE`, `_INCOMPLETE`, `_AWAITING_STAFF` (being
checked outside the deployment), `_CLASS_NEEDED` (no asset class, so no
template; the book refuses it until a person sets the class) and
`_HELD_BACK` (held back at an upgrade's migration; see
[Review provisional records and the migration](../how-to/review-provisional-records.md)).

### A local line is never priced { #a-local-line-is-never-priced }

In the book a position under a provisional record is a **local line**: the
quantity and the cost the statement gives, lots and all, recorded and
reconciled as any position. It has **no price, valuation or analytics**. A
reader shows it as not priced because it is a local record, never valued at
zero, and the lake is never asked a price for it. A data plugin that names a
security only by its vendor's own symbol therefore gets a record that is not
priced; for it to be priced, its record needs an identifier its shared ID
can be found by, such as a FIGI.

The home page counts the provisional records, with **See why** opening the
Instruments page's
[Provisional tab](../how-to/review-provisional-records.md#the-provisional-tab).

### Why a thinly described security stays unrecognised { #why-a-thinly-described-security-stays-unrecognised }

A source thinner than the minimum, such as a statement line with a code and
nothing else, makes **no record**: a record built from too little could match
the wrong security, or duplicate the right one. The holding is kept in the
street as a **placeholder**, outside the book, and on reconciliation the
`operations` plugin records it as a break of its own kind, an
**unrecognized security** (`BREAK_CATEGORY_UNRECOGNIZED_SECURITY`). Once the
source, or a person, gives what the minimum needs, the next resolve makes the
record, and the next statement records the position on it.

## When a record resolves

A provisional record **resolves** without anybody acting once its shared ID
is answered.

- The `INS-` record keeps every value in force, each with its source,
  person and time, and its identifiers. Differing values arrive as offers,
  never over a person's.
- The `LCL-` ID stays on it for life as an identifier under the
  deployment-only scheme `open_meridian_local`, accepted on every write and
  answered as the record it became.
- Positions, lots and pending settlements move to the `INS-` record. Two
  local records answered by one `INS-` ID are both replaced by it, and the
  book sums them.

**Nothing is rewritten.** Journal entries, holding rows, orders, executions
and rows in the lake keep the ID they were recorded with. A read naming a
replaced ID answers for the record it became, and every check of "the same
instrument" compares the record each ID became.

**Replacements.** A shared record merged into another, or decommissioned,
is followed automatically: a merge moves to the surviving ID, and a
decommission is shown on the record and never moves a position.

## Orders on local records

An order may name a local record while the deployment's setting **Allow
orders on local records** is on, as it is by default; the order is marked
"local record: not priced". A deployment admin turns it off on the
**Trading instructions** page (see
[Allow orders on local records](../how-to/set-trading-instructions.md#allow-orders-on-local-records)).
Off, from the change on:

- a new order naming a local record is refused,
  `REFUSAL_REASON_LOCAL_RECORD_NOT_ALLOWED`;
- accepting a venue-originated fill on one is refused the same way;
- orders already working on a local record continue, with their placements
  and child orders: to stop them, set a trading instruction;
- an order the `oms` records for a telephoned or outside order is recorded
  whatever the setting.

## Which identifiers leave the deployment { #the-licence-list }

To find a record's shared ID, the deployment sends only identifiers in the
schemes on its **licence list**: FIGI (and the share-class and composite
FIGI), LEI, a ticker with its venue, CAIP-19, ISO 4217, the SEC's series and
class IDs, and a rate administrator's own code (such as the New York Fed's
`SOFR`). A vendor's own code, `open_meridian_local` and the `LCL-` ID never
leave. When the list gains a scheme, each local record carrying it is asked
again: exact matches resolve, and uncertain ones become prepared changes for
a person. Which identifiers a deployment may hold, and on what terms, is the
deployment's to settle with its vendors.

**Usage reporting.** Weekly, the deployment reports how many of its records
carry each identifier scheme, counts only, never a value, a holding or an
account. A deployment admin turns it off on the Instruments page's
**Licensed identifiers** tab, with a reason, and declares there the schemes
it is licensed for.

## The platform's security master { #the-platforms-security-master }

Open Meridian's platform keeps a **security master**. It assigns the shared
`INS-` IDs a deployment's records can carry, so the same security has the
same ID wherever it is held. A deployment keeps working without it, from its
own records and its local copy of the templates: a record it cannot match
stays local until an answer comes. The shared IDs become consequential when
deployments start communicating with each other.

## Through an agent { #through-an-agent }

The Instruments tools take and answer these fields (see
[Core's tools](../api/core-tools.md)):

- `dashboard__list_instruments_to_complete` takes `provisional`, the
  provisional records alone, each with its `provisional_reason`; every record
  answers `provisional`, `template_id`, `template_version` and
  `missing_fields`.
- `dashboard__complete_instruments` and `dashboard__bring_in_instrument`
  complete a record and bring one in, with a note.
- `dashboard__apply_migration` makes an upgrade's migration lines, or holds
  lines back, with a note.
- `dashboard__set_reports_usage` turns the usage report on or off, with a
  note.
- `dashboard__set_local_record_orders` turns orders on local records on or
  off, with a note.

## For a plugin's author { #for-a-plugins-author }

- **IDs are opaque.** A resolved `LCL-` ID is accepted on every write,
  forever.
- **Ask `provisional`, not the prefix.** A resolve answers whether the
  record is provisional (`ResolveIdentifierResult.provisional`).
- **Every role hears a replacement**, and catches up with
  `list_replacements`; the SDK keeps a current-ID map from both, for a plugin
  that keeps instrument IDs in its own storage. Every role also reads the
  templates (`list_templates`, `read_template`).
- `meridian plugin check` warns (`replaced-ids-followed`), failing nothing,
  on an `INS-` or `LCL-` ID kept as a string in the plugin's code outside its
  tests.

## Related

- [Instruments](instruments.md): identity, dated resolution and the
  instrument store.
- [Review provisional records and the migration](../how-to/review-provisional-records.md).
- [The book of record](the-book-of-record.md): positions, lots and
  reconciliation.
