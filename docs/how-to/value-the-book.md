# Value the book

Valuing the book is a `reporting` plugin's: it reads the
[book of record](../concepts/the-book-of-record.md)'s positions and the
[lake](../concepts/the-lake.md)'s prices, multiplies each trade-date
quantity by its price, and shows the result. It records nothing: a
valuation is computed and shown, never kept in core or published back.

The sample reporting plugin, meridian-sample-reporting, does this: a
reference implementation of valuing a book at a business date's prices, not
a firm's valuation policy. You can run it as it is, or read it and build
your own from the template below.

!!! note "Contract v18"
    meridian-sample-reporting 0.1.0 is built on open-meridian 0.22.0
    (contract v18), and runs on chart 0.1.292 or later.

!!! note "Contract v19: built, not released"
    meridian-sample-reporting 0.2.0, on open-meridian 0.23.0 (contract v19,
    chart 0.1.293 or later), adds the [Board](watch-the-board.md) and any
    reporting currency. It is not yet released.

## What the sample reporting plugin shows

Two pages, under **Open** and **View**, each fitting one screen, its rows
paged, and from 0.2.0 a third, the [Board](watch-the-board.md):

- **Consolidated**: every account you may read, valued at the prices of the
  date you choose (the weekday before today unless you choose another), in
  the reporting currency. The total, how many positions it values and how
  many it leaves out; one row per instrument, with its total quantity, how
  many accounts hold it, its price and the dataset and kind it came from,
  and its value. A row opened shows each account's part.
- **By account**: one account at a time, chosen from those you may read, in
  its own base currency (the reporting currency where the account has none):
  each position's quantity, price and value, the total, and what it leaves
  out.

Each price names its dataset, kind and date and, where the page's prices
stood at different times of day in different places (a crypto close at
midnight UTC beside a New York close at 16:00), its time. A converted value
names its rate. The page keeps itself current: when a source records a price
it was waiting for, or restates one, the rows move, and a restated price
says its version.

## How it values a position

Each position is its trade-date quantity at the end of the date, times the
date's price from the deployment's default sources, in the order the
deployment admin sets:

| What it is | Priced at |
|---|---|
| Cash | 1, in its own currency |
| A money market fund whose record says its NAV is stable | 1.00, by the plugin's named rule, labelled so, never as a source's price |
| A fund | its NAV for the date, else its close (an ETF) |
| Anything else | its close for the date, else its daily bar's close |
| A stablecoin, or a price quoted in one | through a source's price of that stablecoin, never assumed to be 1 |

A price the lake does not hold yet is asked of the source that serves it,
and the page fills in when the source answers. A value in another currency
is converted through the lake's rates, such as the Federal Reserve's H.10:
multiplied, divided where the rate is quoted the other way, or crossed
through dollars, each rate up to a week older than the date, its date shown.

A position with no price or no rate is shown **unvalued, with its reason,
never as zero**, and counted in what the total leaves out:

| It says | What to do |
|---|---|
| asked of its source, not answered yet | Nothing: the page fills in when the source answers |
| no dataset covers it | Entitle a source that does (a fund's NAV needs a source carrying NAVs), or accept that it is valued elsewhere |
| its source is silent | Its admin looks at the source's Connection page |
| this plugin is not entitled to the dataset that covers it | A deployment admin entitles the plugin on the Data sources page |
| no rate into the currency it is shown in | Entitle a source of exchange rates, or choose a later date |
| its currency's cash instrument is not known here | The deployment holds no record of that currency: complete one on the Instruments page, or show it in another. Before 0.2.0, only a currency the book held was known |
| the deployment holds no record of it | The deployment admin looks at the Instruments page |

## Set it up

1. **Data sources.** Launch at least one data plugin and entitle this plugin
   to its datasets, setting the source priority where two datasets price
   the same thing: see [Add a data plugin's key](add-a-data-plugins-key.md),
   [Add a public data plugin](add-a-public-data-plugin.md) and
   [License and entitle a dataset](license-and-entitle-a-dataset.md).
   Nothing is priced without one.
2. **A book.** Accounts with opening balances, recorded through an
   operations plugin, each account's base currency set on the dashboard's
   Accounts page.
3. **Upload and launch it**, from its repository, and approve its role,
   `reporting`:

    ```sh
    meridian plugin upload --dir meridian-sample-reporting
    meridian plugin launch sample-reporting <version> --instance sample-reporting-1
    ```

4. **Its setting**, on **Manage**, **Settings**, by an admin of the plugin:
   **Reporting currency** (`reporting_currency`), the ISO 4217 code
   Consolidated shows every account in, USD unless set. By account always
   shows an account in its own base currency. From 0.2.0 (contract v19)
   the plugin resolves the code to the deployment's cash instrument itself,
   as it does each account's base currency and a stable-NAV fund's
   currency, so **any currency works**, held in the book or not. In 0.1.0
   (contract v18) the code resolved only to a currency the book held; any
   other left converted values unvalued, its cash instrument not known
   here. A value that is not an ISO 4217 code is not used: Consolidated
   shows USD, and the plugin is unhealthy on Manage until the setting is
   corrected.
   From 0.2.0, **Watchlist** (`watchlist`) too: the instruments the Board
   shows.
5. **Read on the plugin**, granted by a deployment admin to the people who
   will look at valuations. Each person sees only the accounts they may
   read.

## Through an agent

Each page is also a read tool on the deployment's MCP surface, answering
exactly what the page shows the same person: `read_valuation` for
Consolidated and `read_account_valuation` for By account, and from 0.2.0
`read_board` for the Board. An agent you have
delegated to reads valuations as you would, and only the accounts you may
read. A tool's answer includes the prices the page shows; an agent client
may pass what it reads to its model's host, and whether a source's terms
allow that is for the deployment's admin and its users to settle with each
source.

It records nothing: a valuation is worked out each time it is looked at,
and nothing it reads leaves the deployment.

## Build your own

A reporting plugin of your own uses what the sample does (contract v18,
open-meridian 0.22.0, CLI 0.1.37):

- **The reads.** A `reporting` plugin reads positions with
  [`list_positions`](../api/typed-operations.md#list_positions) and prices
  with [`list_prices`](../api/typed-operations.md#list_prices), by business
  date, as of a recorded time, from the deployment's default sources, named
  datasets or side by side, and hears new prices for the subjects it names
  with `receive(prices_recorded=..., subjects=...)`. See
  [The lake in the Python SDK](../api/python-sdk.md#the-lake). A
  `reporting` plugin reads prices and bars, never trades or quotes.
- **Its currency, by its code.** From contract v19 a `reporting` plugin
  names its reporting currency by its ISO 4217 code and has core resolve
  it, read-only, with
  [`resolve_identifier`](../api/typed-operations.md#resolve_identifier):

    ```python
    found = await plugin.resolve_identifier(
        identifiers=[meridian.Identifier(scheme="iso4217", value="EUR")], as_of_ns=day_ns)
    euro = found.instrument_id if found.found else ""
    ```

  The `reporting` suite's `resolves-its-reporting-currency` case holds a
  plugin to it from open-meridian 0.23.0.
- **A template.** `meridian plugin new my-report --role reporting` writes a
  `reporting` plugin that shows the positions in its account scope at the
  last close from the lake: each position, its close, the dataset it came
  from, the value it makes and the change over the week, on a **Closes**
  page under Open and View, which is also a read tool, `read_report`, for
  an agent the person delegated to. Its tests run the `reporting` suite the
  SDK carries. See [`plugin new`](../api/cli.md#meridian-plugin-new).
- **Entitlements.** A deployment admin entitles the plugin to the datasets
  it reads: see [License and entitle a dataset](license-and-entitle-a-dataset.md).

A plugin reading a price it is not entitled to is answered without it, the
dataset and field named, never with a zero.
