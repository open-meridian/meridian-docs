# Settlement calendars

A value date, or a settlement date, is worked out from which days are
business days and from a rule: a US equity bought on Friday 9 October 2026
settles one business day later on the US securities settlement calendar,
which skips Columbus Day, so on Tuesday 13 October. From contract v22 a
deployment works such dates out **one way, in core**, from **settlement
calendars** and **date rules** the platform keeps and the deployment pulls,
so every plugin, and every deployment, gets the same answer from the same
records.

!!! note "Contract v22: built, not released"
    Settlement calendars are built for contract v22: the platform's records
    and curation, the deployment's copy in its instrument store, the date
    read and the calendar read (`compute_date`, `read_calendar` in
    open-meridian 0.26.0), the **Calendars** tab on the **Instruments** page
    and its two tools. Their operations are `preview` until the first spot
    FX connectivity plugin has run on them.

!!! note "TODO: the release of contract v22"
    Name the chart that serves contract v22, and the date the platform
    serving calendars was deployed, once released.

## A calendar

A calendar is a platform record under its own ID, `CAL-` and 26 letters and
digits, minted by the platform, never changed and never reused. It is one
of three kinds:

| Kind | Its days | Its subject |
|---|---|---|
| A currency's | The currency's settlement days | The currency's cash instrument |
| A trading calendar | A venue's trading days | The venues that follow it, by their venue IDs |
| A securities settlement calendar | A securities settlement system's days | The settlement system, by its name and country |

**It says which days are not business days, as data:** its weekend, a set
of weekdays dated so that a change of weekend takes effect on its day; each
closed weekday, as a plain date with the holiday's name as its source gives
it; and each weekend day that is nevertheless a business day. **Every day
names its source**, and every source the moment the platform read it.

**It states its coverage:** the first and last dates it vouches for.
Outside them a day's status is **not known**: it is never assumed to be a
business day, and nothing is worked out from it.

**Every change makes a new version**, numbered by the platform, with the
time it came into force and the time the platform recorded it, never
back-dated, and a note. The earlier versions stay readable. An unscheduled
closure, a day of mourning, is a new version whose time in force is its
announcement.

A trading calendar is not a settlement calendar. The Federal Reserve closes
on Columbus Day and Veterans Day and the NYSE does not; on Columbus Day the
US securities settlement system settles nothing while the markets trade. So
a US equity's settlement date counts days on the US securities settlement
calendar, not on the NYSE's.

## The rules

The rules that use the calendars are platform records too, versioned and
dated the same way, each citing its sources. A rule takes no ID: it is
named by its kind, its subject and its version.

- **A settlement-date rule**, for a country and an asset class, with a
  venue's override where a venue differs: the lag in business days, the
  calendars a day must be good in to count, and the date the rule takes
  effect. A change of settlement cycle is a new dated version: the US
  equities and funds rule is T+2 from 5 September 2017 and T+1 from 28 May
  2024, so a trade date before 28 May 2024 is answered by its first version
  and one after by its second.
- **A spot-date rule**, for a currency pair named by its two cash
  instruments in either order: the lag; the calendars an intermediate day
  must be good in to count; the calendars the spot date itself must be good
  in; and the day's cut, a local time with its zone (17:00 New York for
  FX), at or after which an execution's trade date is the next day.
- **Its tenor-date rule**, carried on the same record: the convention a
  tenor date rolls by (following, modified following, preceding or none),
  and whether the end-of-month rule applies.

Whether a cross's spot date may fall on a US dollar holiday, and which
currencies count US dollar days, are parameters of each pair's rule, each
with its cited source, not constants in core.

## Working out a date

Core's instrument store answers five questions, as of the latest versions
it holds or as of a recorded time:

- **A settlement date** for an instrument from a trade date, by its
  market's rule (its asset class and its listing venue's country, a venue's
  override first);
- **A spot date** for a pair from a trade date, or from an execution's
  moment through the pair's cut;
- **A tenor date** from a trade date and a tenor: days, weeks, months or
  years from spot, or overnight, tom-next and spot-next;
- **A date rolled** by a convention on a set of calendars;
- **Whether a date is a business day** on a set of calendars.

A set of calendars combines one way: **a day is good only if it is good in
every one**. The same inputs and the same versions always give the same
date, and a read as of an earlier recorded time reproduces an answer given
before a later version. The date is worked out from the date on the
message or the deployment's clock, never the wall clock.

**Every answer names its basis**: the rule and its version, and each
calendar and its version. Anything that records the date can record its
basis with it. **A date that cannot be worked out says why**, and nothing is
guessed:

| Outcome | Means |
|---|---|
| Computed | The date, with its basis |
| Calendar not held | The deployment does not hold a calendar the question needs yet. The store reports it, the conductor asks the platform, and asking again once it is pulled answers |
| Outside coverage | A day the question needs is outside a calendar's coverage |
| Rule not held | No rule is held for the subject, reported and pulled as a calendar is |

A malformed question is refused, naming the field.

## Coverage ends where the sources end

A calendar's coverage reaches only as far as the sources it was compiled
from. **The US securities settlement calendar's coverage ends on 1 February
2027**, the last date its sources' published schedules reach; a date after
it is answered **outside coverage**. It is never extended by inference from
the trading calendar's closures: Good Friday 2027 is not known to the
settlement calendar until the next schedules are read. Likewise the
coverage of the Canadian and Australian dollars', the krona's and the
krone's calendars ends on 31 December 2026, their sources having published
nothing later yet (see
[Where calendars come from](#where-calendars-come-from)). The platform's
curation reads the next schedules when they are published, and a calendar
whose coverage ends within a year is flagged to its staff.

## Where calendars come from

**The platform keeps them**, as it keeps the
[venue master](venues.md): the same public fact for every firm, so two
deployments never break against each other's trades over a holiday. The
platform's staff, and its curator agent, record each calendar and rule from
public primary sources, each day and rule citing its source and when it was
read; every change the curator agent drafts is a proposal a person on the
staff decides. A deployment holds no licensed vendor's calendar.

**The deployment pulls what it needs**, never the whole set: a currency's
calendar with its cash instrument, a venue's with the venue, a pair's
spot-date rule and the calendars it names when a date is first asked for
that pair, and a market's settlement-date rule likewise. Only the conductor
calls the platform, outbound, and a miss carries only a calendar's subject
(a currency, a venue, a market), never anything the deployment holds. It
refreshes what it holds daily and on reconnecting, asking for the versions
after the highest it holds.

**The instrument store keeps every version pulled**, and answers from what
it holds when the platform cannot be reached. **Nothing in a deployment
edits a calendar**: a disagreement goes to the platform, and a venue's or a
counterparty's own date is kept as stated beside the computed one.

The calendars the platform holds: the ten G10 currencies' settlement
days, the NYSE markets' trading days and the US securities settlement
calendar. Every day cites the copy of its source it was read from and when;
a past year a source no longer shows is read from the Internet Archive's
copy of it as published. Each calendar's coverage runs only as far as its
source does without a gap:

| Calendar | Its sources | Coverage |
|---|---|---|
| The US dollar's settlement days | The Federal Reserve's holidays | 2016 to 2030 |
| The NYSE markets' trading days | The NYSE's holiday page, and the exchange's announcements of unscheduled closures | 2016 to 2028 |
| The US securities settlement calendar | The Federal Reserve's holidays, with each day the markets and their clearing close while the Reserve Banks open (Good Friday, and a Friday closed for a Saturday holiday), from FINRA's published settlement schedules and DTCC's notices | 2016 to 1 February 2027 |
| The euro's settlement days | The ECB's TARGET closing days | 2016 to 2028 |
| The pound's settlement days | England and Wales's bank holidays, from GOV.UK | 2016 to 2028 |
| The yen's settlement days | The Bank of Japan's holiday schedule: the days its offices close | 2016 to 2027 |
| The Swiss franc's settlement days | SIX's schedule of SIC clearing days: the bank holidays on which the Swiss National Bank's payment system makes no value day | 2020 to 2027: the schedules for 2017 to 2019 are not archived |
| The Canadian dollar's settlement days | The Bank of Canada's holiday schedule, the days it marks national; the provincial days it also lists are not listed | 2016 to 2026: the schedule shows upcoming holidays only |
| The Australian dollar's settlement days | The Reserve Bank of Australia's public and bank holidays observed in New South Wales, where the Bank and its settlement system are | 2016 to 2026: 2027's are not published yet |
| The New Zealand dollar's settlement days | The Reserve Bank of New Zealand's NZClear closure dates; Wellington's and Auckland's anniversary days are not among them | 2024 to 2027: earlier dates are not archived |
| The Swedish krona's settlement days | The Swedish Bankers' Association's bank holidays, to which the Riksbank refers for the days banks and its payment system close | 2019 to 2026: the 2018 list is not archived |
| The Norwegian krone's settlement days | Norges Bank's settlement days: the public holidays its settlement system closes | 2016 to 2026: 2027's are not published yet |

Coverage given in years runs from 1 January of the first to 31 December of
the last. A day's name is its source's, in the language the source gave it;
where the Bank of Japan's schedules give dates alone, from 2019, a day is
named "Holiday observed by the Bank of Japan". The platform also holds one
rule, the US equities and funds settlement-date rule above.

!!! note "TODO: the first spot-date rules"
    No spot-date rule is held yet, so a spot or tenor date is answered
    "rule not held" until the platform records the first pairs, with the
    spot FX connectivity plugin planned after v22. Name them when the
    platform holds them.

## The Calendars tab

From contract v22 the dashboard's **Instruments** page, at the deployment
admin's level, has a **Calendars** tab, read-only:

- **The calendars held**, one line each: its name and ID, its kind, its
  version, the last date of its coverage (**Coverage to**) and when it was
  last refreshed, searchable and paged. Empty, it says none is held yet:
  a calendar is pulled when a currency, a venue or a date read first needs
  it.
- **The date rules held**, one line each: the rule's kind, its subject
  (such as `US/equity`), its version and when it was last refreshed.
- **A calendar, one year at a time**, chosen by its name: its version, its
  weekends, its coverage ("outside it a day's status is not known"), and
  each listed day with its kind (**Closed**, or **Open (a weekend day)**),
  its name and its source, with links to the year before and after and
  **Close** back to the lists. A calendar not held says so, and is asked of
  the platform.

### Through an agent

Two of core's tools read the tab, at the deployment admin's level:
[`dashboard__list_calendars`](../api/core-tools.md#dashboard__list_calendars)
and [`dashboard__read_calendar`](../api/core-tools.md#dashboard__read_calendar).
No tool sets a calendar in a deployment.

## In a plugin

A plugin never works out a settlement or value date itself. Any role reads
a calendar's days with `read_calendar` or asks for a date with
`compute_date`, answered whatever its accounts, with the basis the date was
worked out on (see
[Settlement calendars in the Python SDK](../api/python-sdk.md#settlement-calendars)).
The SDK carries the two operations and no calendar library. From contract
v22 every role's suite holds `reads-a-calendar`, and every role's but
`connectivity`'s and `operations`' `asks-for-a-settlement-date`, which a
plugin's suite test maps; a plugin whose work never uses calendars or
settlement dates marks them not presented, with why (see
[A case not presented](../api/python-sdk.md#a-case-not-presented)).

**An execution's settlement date.** A connectivity plugin reports the date
its venue states, kept as stated. Where the venue states none, or where the
plugin also asks, it carries the computed date and its basis beside it
(`computed_settlement_date`, `settlement_date_basis`). A value a plugin
records from the date read carries the provenance **computed**, with its
basis, since a date core worked out is not the plugin's own rule. See
[The order lifecycle](the-order-lifecycle.md#what-the-venue-reports).

**A date a later version makes a holiday** is never moved by the book.
`operations` re-checks pending value dates against the calendars by its own
logic and schedule, and records a break whose cause is **a value date that
is not a business day**, linked to the check: the date, the calendars and
their versions, and why the day is closed (a weekend, a named holiday, or
outside coverage). A venue's revised date is reported as stated.

**A dataset may name its calendar.** From contract v22 a data plugin's
[dataset](the-lake.md#datasets) may name the calendar its business dates
follow, by its `CAL-` ID (`calendar_id`), beside its day's zone and end
(see [A dataset's day](dates-and-time.md#a-datasets-day)). In v22 the lake
applies nothing by it: flagging a daily value dated on a day that calendar
says is closed comes with a later revision of the lake.

## Known limits

- **Closed days only.** A trading calendar records closed days; early
  closes and special sessions are not recorded.
- **Plugins do not hear a new version yet.** A plugin asks when it uses a
  calendar, and `operations` re-checks by reading, so a stale read can miss
  an unscheduled closure for a day. Hearing reference data is a later
  revision.
- **Nothing is computed from outside coverage**, by design: such a date is
  answered so, and a counterparty's date is kept as stated.
- **No deployment-local calendar**, and no vendor's licensed calendar.
- **Nothing here claims a market's rules are met.** A computed date is what
  a named rule gives on named calendars.

## Related

- [The order lifecycle](the-order-lifecycle.md): where a fill's settlement
  date is stated or computed.
- [Dates and time](dates-and-time.md): moments, plain dates and a dataset's
  day.
- [Instruments](instruments.md): the instrument store that keeps the
  calendars.
- [Venues](venues.md): the platform's other master a deployment pulls one
  record at a time.
