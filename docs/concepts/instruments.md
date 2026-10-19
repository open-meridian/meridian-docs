# Instruments

Every holding, and in time every order, is about an **instrument**. Knowing
exactly which instrument, on which date, is harder than it looks: tickers are
reused, symbols differ between brokers, and the same security has several
identifiers in several schemes. This page explains how Open Meridian keeps
instrument identity, where it lives, and what a deployment does when it meets
an instrument it does not know.

## Identity is the answer; a ticker is an attribute

Each instrument has one canonical identifier, `INS-` followed by a unique
value, minted by the platform's security master, and a position carries that
identifier and nothing else about identity. Two deployments holding one
security name it by the same ID. A deployment mints no permanent ID of its
own: while the platform has not answered for a security, the deployment
keeps a **local record** under an `LCL-` ID, provisional and never priced,
until the platform's record replaces it (see
[One ID per instrument](one-id.md)).
Tickers, symbols and codes such as FIGI, ISIN, CUSIP and SEDOL are
**identifiers of** an instrument, each true over a window of time and possibly
reassigned to something else afterwards.

So resolution happens once, at the boundary where outside data arrives, and
everything past that point holds a key that cannot go stale.

**An instrument ID is never reused.** A decommissioned instrument, a
record merged into another, and a local record resolved to the platform's
all keep their IDs, and no other instrument is ever given one, as no venue
is ever given another's [venue ID](venues.md). A resolved `LCL-` ID stays on
the record it became, under the deployment-only scheme
`open_meridian_local`, and is accepted on every write, forever. A position, an order or a
row in the lake stores the ID and nothing else about identity; everything
that moves (a ticker, a symbol, a venue's code) is a dated identifier,
resolved where outside data arrives. The contract says so where an instrument's ID is defined, for
every ID a master mints, instruments and venues alike.

**Resolution is dated.** The question is always "which instrument did this
identifier mean *on this date*", because a ticker that has since been
reassigned must still resolve to its previous holder for a date when it was
theirs. A lookup with no date is a bug waiting for a reassignment. The
date picks which record an identifier names, and, for a record's values,
which version was in force; it never changes which record an ID is.

### Each identifier's window

Every identifier on a record carries its **window**: `valid_from_ns`, when it began naming
the record, and `valid_until_ns`, when it left, 0 while it is still on it.
An identifier leaving a record (moved by a merge, removed by a completion,
or ended by the platform once a person accepts that end) has its window
closed at that date, and is **kept, never deleted**. One joining a record
opens a window from that date.

So the deployment's instrument store answers a resolve **as of any date it
holds**, without asking the platform. A ticker freed by a delisting and
given to another company answers the first record for the dates it named
it, and the second for the dates after.

The windows are shown with each identifier on the Instruments page and a
record's history, and answered by its tools. The platform fills them on a
pull, the identifiers it ended included, so the deployment can offer each
end; an end is in force only once a person accepts it. A plugin never sets a
window.

**A window from the platform opens from the start.** The platform records
an identifier's window from the day the master learnt it, which for many
records is a recent day, not the day the identifier began naming the
security. So the store opens such a window from the start, or from where
another window of the same identifier on another security closed, and an
earlier-dated report, such as a custodian's older statement, an H.10 rate,
or a resolve stating no date, finds the record held rather than minting a
duplicate beside it.

## The security master

The **security master** is on the platform. It holds instrument identity,
symbology — which identifiers, in which schemes, have meant this instrument
and over which window — and structure. It is administered by Open Meridian
staff, and every deployment pulls from it.

It mints a record when a deployment asks for a security it does not hold:
it verifies the security against a source of its own, such as OpenFIGI for
a security a FIGI identifies, and mints the record from that source's
values, held to the security's **template**, never from what the request
said. A request carries only identifiers in the schemes on the platform's
licence list, the template and what the source states of the security;
never a holding, an account or who is asking. A security its source cannot
confirm goes to the platform's staff. See
[One ID per instrument](one-id.md#an-ins-record-minted-by-the-platform).

Staff may also delegate its administration to an AI agent, over OAuth, for at
most 90 days at a time. The agent works through the platform's API or its MCP
server, under the same rules as a person: every change it makes names the agent
and the member of staff it acts for. A change that would alter what deployments
already resolve to — changing or ending an active instrument's identifier,
decommissioning, reactivating — is filed as a proposal for a person to decide,
and applied only if the instrument has not changed since. Define and amend can be
made in bulk, up to 500 instruments at a time, each with its own result.

It changes an instrument by four verbs, and the verb is the transition:

| Verb | What it does |
|---|---|
| **Define** | Creates an instrument and its identity |
| **Amend** | Replaces its identifier set, authoritatively. Not a delta, and it does not change the instrument's state |
| **Decommission** | Takes it out of use; its identifiers are untouched |
| **Reactivate** | Brings a decommissioned instrument back |

Every change increments the instrument's version, and the time a change was
recorded is stamped by the master itself, never supplied by whoever made it,
so what was known when cannot be back-dated. When a change takes effect in the
world is a separate thing, which an amend may state: the date, or date and
time, its identifiers are effective from.

A scheme's name is always lower case (`figi`, `isin`, `cusip`, `sedol`), and a
lookup matches it in any case. A global identifier already in force on another
active instrument is warned about before a change is made, since one
identifier should mean one instrument at a time.

!!! info "Identity, not a data store"
    The security master holds no prices, yields, ratings, volumes or sector
    data, now or later. That data is licensed by each firm from its own
    vendors and lives in the firm's own deployment. Keeping identity apart
    from data values is what keeps the central service small, and keeps a
    firm's licensed data in the firm's hands.

## Binary event contracts

An instrument's type can be a
**binary event contract**, under the class `event_contract`: a contract
that pays a fixed amount if an event happens, and nothing if not, as Kalshi
and Polymarket list them. Its record carries two attributes:

| Attribute | What it is |
|---|---|
| **Payout** | What one contract pays if the event happens, a [Money](money-and-instruments.md) naming its cash instrument: 1 USD at Kalshi, 1 in Polymarket's own USDC instrument at Polymarket. More than zero. |
| **Closes at** | When the venue says trading in it closes, in UTC; none where the venue states none. |

Which outcome a contract pays on stays in its description, in the venue's
own words, which an agent receives marked and screened as another's text.
Polymarket's YES and NO tokens are two records, each a binary event
contract of its own. A contract's price is money per contract, never a
probability: a reader computes the implied probability as the price over
the payout.

The type and its attributes go together: the attributes on a record that is
not a binary event contract, the type on a record not of class
`event_contract`, and a payout naming no asset or not more than zero are
refused, naming the field.

- **In the security master**, staff (or their agent) define and amend an
  instrument with the type and its attributes, and a deployment's pull
  offers them.
- **In a deployment**, the deployment admin completes a record on the
  **Instruments** page: the completion form shows the payout (its amount,
  and its asset by ISO 4217 code or by its cash record) and when trading
  closes once the type is chosen. A data plugin that names a contract, such
  as [Kalshi's or Polymarket's](../how-to/add-a-prediction-market-plugin.md),
  offers the class, the type and the venue's title for a record that lacks
  them.

What a contract paid once its venue resolved it is not on its record: it is an observation, recorded in
the lake as the contract's
[outcome](the-lake.md#an-event-contracts-outcome), with its own
determination and settlement value, so no field says which side a token
pays on.

Which contracts belong to one of the venue's events, and whether they are
mutually exclusive and exhaustive, is an [event group](event-groups.md),
kept beside the records it groups.

## The instrument store: your deployment's copy

Each deployment has an **instrument store**, and it answers every instrument
question locally. For identity it holds a copy of what the platform
publishes, so resolving an identifier never waits on a call to the platform.

It is a *replica*, not a cache, and the difference matters in an outage. A
cache expires and stops answering; a replica keeps answering from what it
holds. When the platform cannot be reached, every instrument the deployment
already knows keeps resolving. An instrument it has never seen gets a local
record until the platform answers.

Beside the platform's `INS-` records it keeps the deployment's own local
`LCL-` records, each marked `provisional` with the reason it is, and the
templates every record names. Whether a record is still waiting is its
`provisional` mark, never its prefix.

Records are applied under their version. A record arriving twice, or an older
one arriving late, changes nothing, so a retried delivery is always safe.

The store also keeps the
[venues](venues.md) the deployment pulled from the platform's venue master, one
at a time as something names them, and answers which venue a code names; an
instrument's listing venue is a venue ID, `listing_venue_id`, in place of its
MIC. Every [amount](money-and-instruments.md) names a cash instrument in this
store, a currency's or a token's.

It also keeps every version of the
[settlement calendars](settlement-calendars.md) and date rules the
deployment pulled from the platform, and works out a settlement, spot or
tenor date from them, one way, for any plugin that asks. The
**Instruments** page's **Calendars** tab shows what it holds, read-only;
nothing in a deployment edits a calendar.

### Resolving an identifier

Given a set of identifiers and a date, the instrument store tries them
strongest first:

1. Global schemes, in order: **FIGI**, **ISIN**, **CUSIP**, **SEDOL**.
2. Any other global scheme.
3. Identifiers scoped to one source, such as a brokerage's own symbol, which
   mean nothing outside that source.

Within a tier, more than one candidate is a **miss**, not a choice: picking
would be wrong about half the time, silently. And an ambiguous tier does not
fall through to a weaker one, which would answer using the evidence the caller
trusted least.

**An ambiguous miss is flagged, never escalated.** Only a person can say
which of two records a set of identifiers means, or whether they are one
security to merge, and the platform holds neither of the deployment's
records. So an ambiguous resolve takes no record and goes to no one outside the deployment: the conflict it
meets is listed on the Instruments page with its reason, `ambiguous` (a
resolve met both records), for the deployment's own person to settle. A
conflict a join or a completion met carries no reason.

**A reporting plugin resolves, read-only.** A `reporting` plugin may name an instrument by an identifier, such as its
reporting currency by its ISO 4217 code, and the store answers the record
it holds for the date. Asked by `reporting`, nothing is minted, joined,
offered or listed: nothing matched is not found, and several matched is
ambiguous, with no conflict listed.

Core enforces it. The store reads
which plugin instance asked from the message's envelope, which the
sidecar stamps, and the roles that instance was launched with from the
deployment's launch records, and answers read-only when none of its roles
may mint: `custody` and `data` may, `reporting` may not. A plugin holding
`reporting` beside `custody` or `data` resolves as those do. A plugin cannot
claim a role by what it sends.

### A currency is fetched from the master

When a plugin or core names a currency by its ISO 4217 code and no record the deployment holds carries
it, the instrument store asks the platform's master for it itself, through
the conductor, with no person asking or approving, keeps the master's
record as the deployment's, and answers the resolve with it, found, not
minted (`found: true`, `minted: false`). A currency is curated reference data carrying no account's
information, so fetching it needs no one's decision, and it stops plugins
leaving local copies beside the master's.

A local record is kept for the code only when the master does not hold
it. While the master is slow or cannot be reached, the resolve is a miss
and nothing is kept; the pull goes on, and a later resolve finds the
master's record. Only `iso4217` is fetched so: every other miss is asked
of the platform to match or mint, as below.

### Searching the deployment's records

Wherever a table names an instrument, such as a table setting's Instrument column, it is chosen with
a search-as-you-type picker: type part of a name, a symbol or an
identifier, and once typing pauses it lists up to eight of the deployment's
records whose identifier values, symbols or description contain it, each
with its name, identifiers and ID. It holds the record's ID, never a
symbol. Only the deployment's records are searched; the platform is not
asked, and nothing lists every record. The picker asks the dashboard's own
search route, `/admin/instruments/search`, on core's pages, which asks the
instrument store's list with the words as its `search`; a plugin's framed
page names its own route.

## When an instrument is missing

The plugin reading the outside data is the one that knows the source's
symbols, so it resolves each instrument before recording anything about it,
stating every identifier it has, a description, a currency, and the class
and type where the source says them. When nothing in the deployment
matches:

1. **The plugin never creates an instrument**; no plugin can. Its resolve
   asks the instrument store, which picks the security's template from the
   class and type the source stated.
2. **The conductor asks the platform to match or mint it**, sending only
   identifiers in the schemes on the platform's licence list. A brokerage's
   or a vendor's own symbol means nothing centrally, and never leaves the
   deployment.
3. **Answered within a short, bounded wait**, the deployment keeps the
   record under the platform's `INS-` ID from the start, and nobody acts.
4. **Otherwise the store keeps a local record**, under an `LCL-` ID,
   provisional, with the reason: the platform not reached, the request with
   the platform's staff, or nothing on the licence list to look for. The
   resolve answers it, and the plugin records against it. It resolves to
   the platform's record on its own once the platform answers.

A source too thin for any record, such as a statement line with a code and
nothing else, makes none: the holding is kept in the street, outside the
book, and the `operations` plugin's reconciliation shows it as an
**unrecognized security** (see
[One ID per instrument](one-id.md#why-a-thinly-described-security-stays-unrecognised)).

**A local record is never priced.** A data plugin that names a security
only by its own vendor symbol, such as a ticker as its vendor spells it,
gets a local record for it, and the lake never prices a local record: a
position on it shows as not priced, never as zero. For the security to be
priced, its record needs an identifier the platform can match, such as a
FIGI. Usually that is the record your custodian's positions already name,
which a data plugin's settings can point to.

The conductor's asking is throttled, so a burst of misses for the same
identifiers is not a burst of requests, and never a burst of new instruments.
Only the conductor calls the platform, because only it holds the deployment's
key; the instrument store itself holds no address and no key.

## Through an agent

The Instruments page's tools on the deployment's MCP surface take and
answer a record's type, its attributes and its identifiers' windows:
`dashboard__read_instrument`, `dashboard__read_instrument_history`,
`dashboard__list_instruments_to_complete` and
`dashboard__complete_instruments`.

- A record answers `binary_event_contract` (`payout` with its `amount` as
  text, its `currency_code` or `instrument_id`, and `closes_at_ns`), and each
  identifier its `valid_from_ns` and `valid_until_ns` where it has them; and
  its `provisional` mark, `template_id`, `template_version` and
  `missing_fields`, as [One ID per instrument](one-id.md#through-an-agent)
  describes.
- `dashboard__list_instruments_to_complete` lists a binary event contract
  lacking its payout and close among the records to complete, and each
  conflict with its `reason` (`MISS_REASON_AMBIGUOUS` where a plugin's
  resolve met several records).
- `dashboard__complete_instruments` takes the type
  `INSTRUMENT_TYPE_BINARY_EVENT_CONTRACT` and a `binary_event_contract`
  value, each with its source in words and a note, against the version
  read:

    ```json
    {"completions": [{
      "instrument_id": "LCL-01JB8Z3K6Q",
      "against_version": 1,
      "note": "a Kalshi contract, completed from the venue's market page",
      "values": [
        {"instrument_type": "INSTRUMENT_TYPE_BINARY_EVENT_CONTRACT", "source": "stated by kalshi-1"},
        {"binary_event_contract": {"payout": {"amount": "1", "currency_code": "USD"},
                                   "closes_at_ns": 1798761600000000000},
         "source": "the venue's market page"}
      ]
    }]}
    ```

  An end the platform offered is accepted as the identifier with its
  `valid_until_ns`.

Two more tools read the **Calendars** tab, at the deployment admin's level:
[`dashboard__list_calendars`](../api/core-tools.md#dashboard__list_calendars)
and [`dashboard__read_calendar`](../api/core-tools.md#dashboard__read_calendar).

## Known limits

- **No bulk distribution.** A deployment pulls the one instrument it just
  missed. There is no snapshot of the whole master to download.
- **A local record is not valued.** Until it resolves to the platform's
  record, a position on it has no price.

## Related

- [One ID per instrument](one-id.md): `INS-` records
  minted by the platform, and local `LCL-` records until it answers.
- [Review provisional records and the migration](../how-to/review-provisional-records.md).
