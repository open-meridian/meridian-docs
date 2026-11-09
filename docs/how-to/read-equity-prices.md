# Read equity and option prices

Put US equities' closes, bars, quotes and trades, and listed options'
chains, into your deployment's lake from a data plugin, and read them from
any plugin entitled to them. You need chart 0.1.477 and CLI 0.1.59.

| Plugin | What it records | Its key |
|---|---|---|
| Databento | Closes and daily bars, the last sale and quotes, every trade, and OPRA option chains | A Databento API key; you say on Settings whether your plans reach real time or history only |
| Massive | Closes and bars, trades and quotes from the consolidated feeds, and OPRA option chains, real time or delayed | A Massive API key |
| Alpaca | Daily closes and bars, live prices and trades for US stocks and ETFs | An Alpaca API key and secret |
| Tradier | Daily closes, live or delayed prices, and option chains | A Tradier access token |

## 1. Launch it and enter its key

Install the plugin from **Browse** on the dashboard's **Plugins** page, or
with `meridian plugin install <listing> --note "<why>"`, and
approve its `data` role. Then, under **Manage → Settings**, enter the key: a
secret setting, never shown again, logged or sent anywhere but the vendor.
Databento also asks for a **Stocks plan** and an **Options plan**, each
**Real time** or **Historical only**; it opens no live session until you
choose Real time. **Connection** then says whether the key is set and
whether the vendor answered, never the key itself.

## 2. License and entitle its datasets

On the deployment's **Data sources** page a deployment admin:

1. **licenses** each dataset your plan reaches (Databento's `daily`, `live`,
   `trades` and `options`; Alpaca's `daily`, `live` and `trades`), each
   starting from the vendor's terms, with a note;
2. **entitles** the plugins that read prices, trades, quotes and chains;
3. sets the **priority** where two datasets record the same prices.

Nothing is read from the vendor until an entitled plugin asks.

## 3. Read them

A plugin holding `reporting`, `portfolio`, `signal` or `ems` reads closes
with [`list_prices`](../api/typed-operations.md#list_prices); `signal` and
`ems` read trades and quotes with
[`list_trades`](../api/typed-operations.md#list_trades) and
[`list_quotes`](../api/typed-operations.md#list_quotes); and a chain is read
with `chains.read_expirations` and `chains.read_chain`. See
[Read trades and quotes](read-trades-and-quotes.md),
[Record and read an option chain](record-and-read-an-option-chain.md) and
[Fast data retrieval](../tutorials/fast-data-retrieval.md).

**Datasets**, under Manage, shows each dataset with what was recorded and
declined; **Connection** the calls made and each live session.

## Related

- [Using a data plugin](using-a-data-plugin.md): the first-use path every
  data plugin shares.
- [License and entitle a dataset](license-and-entitle-a-dataset.md).
- [Equities](../concepts/equities.md).
