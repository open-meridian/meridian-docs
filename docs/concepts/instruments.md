# Instruments

Every holding, and in time every order, is about an **instrument**. Knowing
exactly which instrument, on which date, is harder than it looks: tickers are
reused, symbols differ between brokers, and the same security has several
identifiers in several schemes. This page explains how Open Meridian keeps
instrument identity, where it lives, and what a deployment does when it meets
an instrument it does not know.

## Identity is the answer; a ticker is an attribute

Each instrument has one canonical identifier, `INS-` followed by a unique
value, and a position carries that identifier and nothing else about identity.
Tickers, symbols and codes such as FIGI, ISIN, CUSIP and SEDOL are
**identifiers of** an instrument, each true over a window of time and possibly
reassigned to something else afterwards.

So resolution happens once, at the boundary where outside data arrives, and
everything past that point holds a key that cannot go stale.

**An instrument ID is never reused.** A decommissioned instrument, a
deployment's record mapped onto another, and a record merged into another
all keep their IDs, and no other instrument is ever given one, as no venue
is ever given another's [venue ID](venues.md). A position, an order or a
row in the lake stores the ID and nothing else about identity; everything
that moves (a ticker, a symbol, a venue's code) is a dated identifier,
resolved where outside data arrives. From contract v19 the contract says so where an instrument's ID is defined, for
every ID a master mints, instruments and venues alike.

**Resolution is dated.** The question is always "which instrument did this
identifier mean *on this date*", because a ticker that has since been
reassigned must still resolve to its previous holder for a date when it was
theirs. A lookup with no date is a bug waiting for a reassignment. The
date picks which record an identifier names, and, for a record's values,
which version was in force; it never changes which record an ID is.

### Each identifier's window

From contract v19 (chart 0.1.293), every identifier
on a record carries its **window**: `valid_from_ns`, when it began naming
the record, and `valid_until_ns`, when it left, 0 while it is still on it.
An identifier leaving a record (moved by a merge, removed by a completion,
or ended by the platform once a person accepts that end) has its window
closed at that date, and is **kept, never deleted**. One joining a record
opens a window from that date.

So the deployment's instrument store answers a resolve **as of any date it
holds**, without asking the platform. A ticker freed by a delisting and
given to another company answers the first record for the dates it named
it, and the second for the dates after. Contract v18 wrote a record's
identifiers whole on each change, and an identifier that left a record
stopped answering even for the dates it had named it.

The windows are shown with each identifier on the Instruments page and a
record's history, and answered by its tools. The platform fills them on a
pull, the identifiers it ended included, so the deployment can offer each
end; an end is in force only once a person accepts it. A plugin never sets a
window. In v19 an identifier pulled from the platform opens its window on
the day it entered the master, which can make a duplicate record: see
[Known limits](#known-limits).

## The security master

The **security master** is on the platform. It holds instrument identity,
symbology — which identifiers, in which schemes, have meant this instrument
and over which window — and structure. It is administered by Open Meridian
staff, and every deployment pulls from it.

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

From contract v19, an instrument's type can be a
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

## The instrument store: your deployment's copy

Each deployment has an **instrument store**, and it answers every instrument
question locally. For identity it holds a copy of what the platform
publishes, so resolving an identifier never waits on a call to the platform.

It is a *replica*, not a cache, and the difference matters in an outage. A
cache expires and stops answering; a replica keeps answering from what it
holds. When the platform cannot be reached, every instrument the deployment
already knows keeps resolving. Only an instrument it has never seen has to
wait.

Records are applied under their version. A record arriving twice, or an older
one arriving late, changes nothing, so a retried delivery is always safe.

From contract v18 the store also keeps the
[venues](venues.md) the deployment pulled from the platform's venue master, one
at a time as something names them, and answers which venue a code names; an
instrument's listing venue is a venue ID, `listing_venue_id`, in place of its
MIC. Every [amount](money-and-instruments.md) names a cash instrument in this
store, a currency's or a token's.

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
records. So from contract v19 an ambiguous resolve
takes no record and goes to no one outside the deployment: the conflict it
meets is listed on the Instruments page with its reason, `ambiguous` (a
resolve met both records), for the deployment's own person to settle. A
conflict a join or a completion met carries no reason.

**A reporting plugin resolves, read-only.** From contract v19 a
`reporting` plugin may name an instrument by an identifier, such as its
reporting currency by its ISO 4217 code, and the store answers the record
it holds for the date. Asked by `reporting`, nothing is minted, joined,
offered or listed: nothing matched is not found, and several matched is
ambiguous, with no conflict listed.

!!! warning "Known limit in v19: `reporting`'s resolve is not read-only yet"
    Core does not yet tell the instrument store that a resolve is a
    `reporting` plugin's, so it answers one as it answers any plugin's: a
    code nothing matches could record a miss, a local record minted for it.
    A currency's ISO 4217 code resolves to the currency's cash instrument
    either way. Fixed in v20.

## When an instrument is missing

The plugin reading the outside data is the one that knows the source's
symbols, so it resolves each holding before recording it. When resolution
misses:

1. **The plugin reports the miss as a fact** and moves on. It does not block,
   does not retry in a loop, and never creates an instrument; no plugin can.
2. **The holding is recorded unresolved**, carrying the identifiers the plugin
   had. It moves no position, and it is shown beside the positions, so the gap
   is visible rather than silently dropped.
3. **The conductor reacts.** It asks the security master for the instrument,
   sending only global identifiers — a brokerage's symbol means nothing
   centrally. If the master has it, the record comes back and the instrument
   store applies it. If not, the conductor may ask the platform to define it,
   and the platform may decline.

The conductor's reaction is throttled, so a burst of misses for the same
identifiers is not a burst of requests, and never a burst of new instruments.
Only the conductor calls the platform, because only it holds the deployment's
key; the instrument store itself holds no address and no key.

## Through an agent

The Instruments page's existing tools on the deployment's MCP surface take
and answer what contract v19 adds, with no new tool:
`dashboard__read_instrument`, `dashboard__read_instrument_history`,
`dashboard__list_instruments_to_complete` and
`dashboard__complete_instruments`.

- A record answers `binary_event_contract` (`payout` with its `amount` as
  text, its `currency_code` or `instrument_id`, and `closes_at_ns`), and each
  identifier its `valid_from_ns` and `valid_until_ns` where it has them.
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

## Known limits

- **Before contract v19, one version of an identifier set.** A runtime
  before chart 0.1.293 writes a record's identifiers whole on each change,
  so an identifier a later change dropped no longer resolves as of a date
  when it was still valid. That fails safe, never the wrong instrument;
  contract v19 keeps every window instead.
- **Duplicate records from an earlier-dated report (v19).** An identifier
  pulled from the platform starts its window on the day it entered the
  master, not the day it began naming the instrument. A report dated before
  that day, such as a custodian's older statement, finds no record holding
  the identifier then, and can create a duplicate local record. Until the
  fix in v20, merge each duplicate into the platform's record on the
  **Instruments** page.
- **No bulk distribution.** A deployment pulls the one instrument it just
  missed. There is no snapshot of the whole master to download.
