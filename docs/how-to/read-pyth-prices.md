# Read Pyth Network prices

Put Pyth Network's composite prices, each a mid with its confidence
interval, and its US Treasury par yields into your deployment's lake. You
need chart 0.1.408 and CLI 0.1.58.

Pyth's Hermes API asks for an API key on every price. A key on Pyth's
Starter plan serves crypto; its Pro plan serves every family: equities,
currencies, metals, commodities, US Treasuries and rates.

1. **Launch it** and approve its `data` role.
2. **Enter the Pyth API key** on Settings: a secret setting, sent to Hermes
   alone. A feed your plan does not serve is refused by Hermes, and
   **Connection** says so.
3. **License** its datasets on the **Data sources** page: `crypto`, `fx`,
   `equity`, `metal` and `commodities`, Pyth's composite prices, each a mid
   with its confidence interval; and `rates`, US Treasury constant-maturity
   par yields. Each starts from Pyth's subscription terms. **Entitle** the
   plugins that read them.

Read the prices with [`list_prices`](../api/typed-operations.md#list_prices)
and the yields, a par yield curve's points, with
[`list_rates`](../api/typed-operations.md#list_rates). On a development
deployment, **Sample data** answers from Pyth's feed catalogue and made-up
prices, with no key.

## Related

- [Read crypto prices from Coinbase and Kraken](read-crypto-prices.md).
- [Rates](../concepts/rates.md).
