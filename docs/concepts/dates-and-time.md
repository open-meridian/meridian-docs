# Dates and time

Open Meridian keeps two kinds of time apart, because they answer different
questions:

- a **moment**: an instant, in nanoseconds since the Unix epoch, in UTC.
  When a trade printed, when a row was recorded, when a price was in force.
  Every field ending `_ns` is one.
- a **date**: a plain calendar day, with no time and no zone. Which business
  day a close is for, the date positions are read at. It crosses the wire as
  its ISO 8601 text, `2026-10-09`.

!!! note "Contract v18"
    This page describes contract v18: core from chart 0.1.292 and
    open-meridian 0.22.0.

## A daily price is keyed by a date

A close, a NAV, a settlement price or a daily bar is for a **business
date**, and is keyed by it: the close of 2026-10-08, not a moment that
happens to fall on it in some zone. Real-time data, a last price or a bid,
is keyed by the moments it was in force, the venue's zone known from its
[venue](venues.md).

## A dataset's day

Which candle or session counts as a business date depends on the dataset,
so each [dataset](the-lake.md#datasets) declares its day:

| Declared | What it says | For example |
|---|---|---|
| `day_time_zone` | The IANA zone a business date is in. Empty for a dataset that is not daily. | `America/New_York` for a US close and FX's 17:00 roll; `Etc/UTC` for a crypto venue's daily candle. |
| `day_end_minute` | The minutes after local midnight the day ends, 0 to 1,439; 0 ends it at midnight. | 960 for a US equity close at 16:00 New York; 1,020 for FX at 17:00 New York; 0 for a candle ending at UTC midnight. |

So the day says which session counts as the date, and when its value is
final. It carries no holiday calendar: a business date with no session has
no close. Settlement calendars are core reference data with a specification
of their own, and a dataset will name its calendar once they are built.

A day still forming is recorded and restated as it fills: its row's valid
time ends after the moment it is read, under one row key, until its close
is final. A reader sees the latest version; a read as of an earlier moment
sees the version in force then.

## A date is checked at both ends

A date is a date in the SDK and in core, and text that is no date is
refused, naming the field, before it goes anywhere:

- **In the SDK** (open-meridian 0.22.0), every field the data dictionary
  types `date` takes a Python `datetime.date`, or its ISO text as before.
  Text that is no day that exists (`2026-02-30`), text in another form
  (`20261009`) and a `datetime`, which is a moment, are refused before
  anything is sent. What comes back is the text:
  `date.fromisoformat(price.meta.business_date)`.
- **In core**, the sidecar refuses a batch or a read naming a business date
  that is no day, before anything is sent on, and the lake and the book
  read every date as a date.

On the wire a date stays its ISO text, so a plugin built before v18 sending
valid ISO dates sends what it always sent.

## Related

- [The lake](the-lake.md): reading by business date, at a moment, or as of
  a recorded time.
- [Venues](venues.md): a venue's time zone.
- [Typed operations: times and dates](../api/typed-operations.md#times-and-dates).
