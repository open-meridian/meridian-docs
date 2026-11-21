# Read crypto prices from Coinbase and Kraken

Put crypto pairs' closes, live prices, quotes and trades into your
deployment's lake from Coinbase or Kraken, and read them from any plugin
entitled to them.

--8<-- "requirements.md"

## Coinbase and Kraken

1. **Launch it.** Install the plugin from **Browse**, or with
   `meridian plugin install`, and approve its `data` role. It asks for
   storage for its raw responses, and no key.
2. **License and entitle its datasets**, `<instance>:daily`,
   `<instance>:live` and `<instance>:trades`, each listed with the terms the
   exchange's standard terms impose, as [License and entitle a dataset](license-and-entitle-a-dataset.md) says. Set the
   [priority](license-and-entitle-a-dataset.md#set-a-source-priority) where
   another plugin also records the same pairs' closes.

An agent you delegate to reads the plugin's pages through its tools,
`read_connection` and `read_datasets`.

## Read them

A plugin holding `reporting`, `portfolio`, `signal` or `ems` reads prices
with [`list_prices`](../api/typed-operations.md#list_prices); `signal` and
`ems` read trades and quotes with
[`list_trades`](../api/typed-operations.md#list_trades) and
[`list_quotes`](../api/typed-operations.md#list_quotes). A page showing them
live uses [live values](../tutorials/live-pages.md).

On a development deployment, each plugin's **Sample data** setting answers
from made-up data instead of the venue.

## Related

- [Using a data plugin](using-a-data-plugin.md#coinbase-and-kraken).
- [License and entitle a dataset](license-and-entitle-a-dataset.md).
- [Read Pyth Network prices](read-pyth-prices.md).
- [Crypto](../concepts/crypto.md).
