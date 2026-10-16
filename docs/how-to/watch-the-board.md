# Watch the market on the Board

The sample reporting plugin, from plugin-sample-reporting, shows a **Board**
beside its valuation pages: a calm view of a watchlist's latest prices, from
every data source the plugin may read, side by side, read again every few
seconds. It is a reference implementation, not a trading screen: it shows
conflated prices and bars, never the tape.

A person with `write` keeps their own Board, saved for them alone, beside
the admin's shared one (see [Your own Board](#your-own-board) and
[Each person's own views](using-a-reporting-plugin.md#each-persons-own-views)).

## What it shows

The Board is under **Open** and **View**, beside Consolidated and By
account, and fits one screen:

- **Three panels: Stocks, Crypto and Prediction markets.** Each instrument
  in the watchlist is shown in its panel by its asset class, one row per
  data source and venue, side by side: Coinbase's bitcoin beside Kraken's,
  a broker's consolidated price beside another's single-exchange one. Each
  row shows the last price, the bid and the ask, the change from the close
  before today, when the price stood (in UTC on the page), and whether it
  is **live** or the **close**, dated, where no live source answers.
- **A prediction market's implied probability.** A
  [binary event contract](../concepts/instruments.md#binary-event-contracts)'s
  price over its payout, worked out by the plugin. The price itself stays
  money per contract.
- **A chart** of one instrument: its daily closes over sixty days and its
  minute bars over the last eight hours. Click a row to chart it.
- **The stream's state**, beside the plugin's name: live, waiting for its
  sources (closes shown), a source silent, closes only, or failed, with when
  it last read.
- **Every watched instrument**, one no source prices saying so
  ("no source prices it"); a fund at its NAV, marked NAV, daily; and a
  stable money market fund at 1.00, marked stable.

Prices and bars only: no trades, no sizes, no tape. `reporting` is for
slower consumers, and the Board reads what the lake conflates: the latest
`last`, `bid`, `ask` and `mid` per dataset, venue and asset. A desk that
needs every trade writes a `signal` or `ems` plugin: see
[Read trades and quotes](read-trades-and-quotes.md).

It is read again every five seconds while someone is looking, and every
minute with nobody looking. Reading on that timetable keeps a **standing
want** at the lake for the watchlist's live prices, so the data sources keep
them current, and stream them where they can. On a phone, tabs show one
panel at a time, and a tap on a row opens its whole.

## Set it up

1. **Data sources** with live datasets, launched and entitled to this
   plugin on the Data sources page: a crypto exchange's `live`, a broker's
   `live`, and Kalshi's or Polymarket's for the Prediction markets panel. A
   panel with no live source shows the close; one with no source at all
   says so. See [Using a data plugin](using-a-data-plugin.md#the-data-plugins)
   and [Add a prediction-market plugin](add-a-prediction-market-plugin.md).
2. **The plugin**, uploaded and launched as for
   [valuing the book](value-the-book.md#set-it-up), holding `reporting`.
3. **The watchlist** (`watchlist`), on **Manage**, **Settings**, by an admin
   of the plugin: the instruments the Board shows, one a row, each found
   among the deployment's instrument records, at most 40. The admin also
   chooses each row's **Panel**. The Board itself never changes
   it: this is the shared Board.
4. **Read on the plugin**, for the people who will look at it.

## Your own Board

A person with `write` on the plugin builds and saves their own
Board, a watchlist and charts of their own (`own_watchlist` and
`own_charts`, declared `per_person`), on the Board under **Open**, choosing
**Shared** or **Mine**. **Save** keeps it for them alone, with **Prepare**
beside it, alone where its second pair of eyes is on (see
[Prepared changes](../concepts/prepared-changes.md)). A person with `read`
sees the shared Board. See
[Each person's own views](using-a-reporting-plugin.md#each-persons-own-views).

## Through an agent

The Board is also a read tool on the deployment's MCP surface, `read_board`,
answering what the page shows the same person: each panel's rows (the
instrument, its price, dataset, venue and time, in its dataset's own zone,
live or the close, and an event contract's implied probability) and the
stream's state, with the view it shows (shared or the person's own). An agent saves a person's own Board with `save_own_board`,
checked by `check_own_board`. An agent sets the shared watchlist through the
deployment's settings tools, `dashboard__set_plugin_settings`, as an admin of the plugin
would on the form: see [Core's tools](../api/core-tools.md#dashboard__set_plugin_settings).

A tool's answer includes the prices the page shows. An agent client may
pass what it reads to its model's host; what each source's terms allow, for
display inside the organisation, for a demonstration, or for an agent, is
for the deployment's admin and its users to settle with each source. This
is not legal advice, and neither the plugin nor these docs say a deployment
meets any source's terms.

## Related

- [Value the book](value-the-book.md): the plugin's other two pages.
- [The lake](../concepts/the-lake.md): conflated prices, and who reads
  trades and quotes.
- [Set a plugin's settings](set-a-plugins-settings.md).
