# Value the book

Valuing the book is a `reporting` plugin's: it reads the
[book of record](../concepts/the-book-of-record.md)'s positions and the
[lake](../concepts/the-lake.md)'s prices, multiplies each trade-date
quantity by its price, and shows the result. It records nothing: a
valuation is computed and shown, never kept in core or published back.

!!! note "TODO: the sample reporting plugin"
    The sample reporting plugin, meridian-sample-reporting, values the book
    at the close in a base currency through FX, consolidated across every
    account a person may read and by account, each price naming its
    dataset, kind and date, and a position with no price shown unvalued,
    never zero. It is still being built. This page will walk through it,
    and its tools `read_valuation` and `read_account_valuation`, once it is.

## What exists now

These are built, and not yet released (contract v18, open-meridian 0.22.0,
the CLI release after 0.1.36):

- **The reads.** A `reporting` plugin reads positions with
  [`list_positions`](../api/typed-operations.md#list_positions) and prices
  with [`list_prices`](../api/typed-operations.md#list_prices), by business
  date, as of a recorded time, from the deployment's default sources, named
  datasets or side by side, and hears new prices for the subjects it names
  with `receive(prices_recorded=..., subjects=...)`. See
  [The lake in the Python SDK](../api/python-sdk.md#the-lake).
- **A template.** `meridian plugin new my-report --role reporting` writes a
  `reporting` plugin that shows the positions in its account scope at the
  last close from the lake: each position, its close, the dataset it came
  from, the value it makes and the change over the week, on a **Closes**
  page under Open and View. Its tests run the `reporting` suite the SDK
  carries. See [`plugin new`](../api/cli.md#meridian-plugin-new).
- **Entitlements.** A deployment admin entitles the plugin to the datasets
  it reads: see [License and entitle a dataset](license-and-entitle-a-dataset.md).

A plugin reading a price it is not entitled to is answered without it, the
dataset and field named, never with a zero.
