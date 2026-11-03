# FX

Currencies are records by their ISO 4217 code; a spot FX position is two
cash legs. FX prices and quotes are recorded per pair, and the spot market's
week runs from Sunday 17:00 to Friday 17:00 New York.

- **Currencies and cash:** [Money and instruments](money-and-instruments.md),
  and the deployment's [FX pivot currencies](../how-to/set-the-fx-pivot-currencies.md).
- **Dates:** value dates and rolls in [Settlement calendars](settlement-calendars.md)
  and [Dates and time](dates-and-time.md).
- **Orders:** [FX netting](fx-netting.md) and [Net FX orders](../how-to/net-fx-orders.md).
- **Rates:** fixings and curves in [Rates](rates.md).
- **Live pages:** the FX week, `meridian.helpers.sessions.FX_WEEK`, is the
  session a page's values count their staleness in: see
  [Build a live page](../tutorials/live-pages.md).
- **Plugins:** [Integrations, filtered to FX](../how-to/integrations.md?asset=fx).
