# Venues

A **venue** is where a price or a trade comes from: an exchange, an
alternative trading system, a crypto exchange, a dealer network, or a
facility trades are reported to. From contract v18 every venue a deployment
names has an ID of the platform's, `VEN-` followed by letters and digits,
from the platform's **venue master**, kept beside the security master. A
deployment pulls the venues it needs from it, one at a time, and never mints
one.

!!! note "Contract v18"
    This page describes contract v18: core from chart 0.1.292 and
    open-meridian 0.22.0, and the platform's venue master, deployed
    2026-10-10.

## A venue ID, and its codes

A venue's ID is the answer; its codes are attributes, as an instrument's
ticker is an attribute of the instrument (see [Instruments](instruments.md)).
A venue may be known by:

- its **MIC**, the ISO 10383 market identifier code, operating or segment,
  under the scheme `iso10383`, where it has one. A crypto exchange or a
  dealer network may have none;
- **vendors' codes**, each a `symbol` with the vendor as its `source`, such
  as Alpaca's one-letter exchange codes (`V` for IEX).

Each code is dated: a MIC names the venue in force on the date it is asked
about.

| A venue's record | What it holds |
|---|---|
| `venue_id` | Its `VEN-` ID, never changed and never reused. |
| `name` | Its name. A rename is an amend, the old name kept in its dated history. |
| `country_code` | Where it operates, ISO 3166-1 alpha-2. |
| `kind` | `exchange`, `alternative_trading_system` (FX's anonymous central books among them), `crypto_exchange`, `dealer_network` (RFQ, OTC and, for now, IOI networks) or `reporting_facility` (reported to, not traded on). |
| `identifiers` | Its MIC and vendors' codes, each in force from a date. |
| `operating_venue_id` | For a segment, the venue it belongs to. |
| `time_zone` | The IANA zone its trading day is defined in: `America/New_York` for a US equity venue, `Etc/UTC` for a crypto exchange. |
| `lifecycle_state` | Active, or decommissioned: closed, or its MIC expired. A decommissioned venue still resolves for a date it was in force. |

The record is the platform's, at the platform's version; a deployment keeps
it as pulled and changes nothing in it. The whole record is in the
[data dictionary](../boundaries/instrument.md#meridian.v1.VenueRecord).

## Pulled when needed

A deployment asks the platform for a venue only when something names one it
does not hold, by the venue's public codes alone, and never pulls the whole
list. A plugin resolves a code it read to a venue ID through its sidecar
([`resolve_venue`](../api/typed-operations.md#resolve_venue)); the
deployment answers from the venues it holds.

Where none answers, the plugin reports the venue missing
([`report_missing_venue`](../api/typed-operations.md#report_missing_venue)),
and carries on. The deployment asks the platform for it, once, and again only
after ten minutes. A row naming a venue the deployment does not hold yet
names none, and keeps the code as the source reported it, so the venue is
not lost; the Data sources page counts the miss against the dataset. Once
the platform's curation has vetted the venue and the deployment holds it, it
resolves like any other.

A plugin never adds a venue, and neither does a deployment: a new venue is a
new record in the venue master, never a change to the contract.

## Where a deployment names a venue

- **A lake row's source** (`Source.venue_id`): the venue a price printed on.
  Empty is the consolidated view across venues.
- **A dataset's catalogue entry** (`DatasetDeclaration.venue_id`): the venue
  a dataset is, where it is one venue's; empty for a consolidated dataset.
- **An instrument's listing venue** (`InstrumentRecord.listing_venue_id`),
  in place of its MIC: a segment's venue where the listing is on one. The
  instrument's `exchange_mic` is deprecated from v18 and read until every
  record carries a venue ID.

## Related

- [The lake](the-lake.md): a row's venue, and a dataset's.
- [Dates and time](dates-and-time.md): a venue's time zone, and a dataset's
  day.
- [Instruments](instruments.md): identity, and resolving an identifier.
