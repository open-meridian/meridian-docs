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
everything past that point holds a key that cannot go stale. A canonical
identifier is never reused: an instrument that is retired does not free its
identifier for the next one.

**Resolution is dated.** The question is always "which instrument did this
identifier mean *on this date*", because a ticker that has since been
reassigned must still resolve to its previous holder for a date when it was
theirs. A lookup with no date is a bug waiting for a reassignment.

## The security master

The **security master** is on the platform. It holds instrument identity,
symbology — which identifiers, in which schemes, have meant this instrument
and over which window — and structure. It is administered by Open Meridian
staff, and every deployment pulls from it.

It changes an instrument by four verbs, and the verb is the transition:

| Verb | What it does |
|---|---|
| **Define** | Creates an instrument and its identity |
| **Amend** | Replaces its identifier set, authoritatively. Not a delta, and it does not change the instrument's state |
| **Decommission** | Takes it out of use; its identifiers are untouched |
| **Reactivate** | Brings a decommissioned instrument back |

Every change increments the instrument's version, and the time a change was
recorded is stamped by the master itself, never supplied by whoever made it,
so what was known when cannot be back-dated.

!!! info "Identity, not a data store"
    The security master holds no prices, yields, ratings, volumes or sector
    data, now or later. That data is licensed by each firm from its own
    vendors and lives in the firm's own deployment. Keeping identity apart
    from data values is what keeps the central service small, and keeps a
    firm's licensed data in the firm's hands.

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

## Known limits

- **One version per instrument, locally.** The instrument store holds each
  instrument's current version. An identifier that a later amend dropped is
  gone from the local copy, so resolving it as of a date when it was still
  valid returns nothing. That is a safe failure — never the wrong instrument —
  and still a gap.
- **No bulk distribution.** A deployment pulls the one instrument it just
  missed. There is no snapshot of the whole master to download.
