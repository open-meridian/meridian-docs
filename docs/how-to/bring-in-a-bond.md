# Bring in a bond and complete its terms

Make a record for a bond or a CD in your deployment's instrument master, and
complete its terms from a reference data plugin, Terrapin or 9fin, which
offers them. You need chart 0.1.408 and CLI 0.1.58.

## 1. Bring it in

On the dashboard's **Instruments** page, the instrument picker searches by
what you type, a ticker, a name, an ISIN, a CUSIP or a FIGI, and answers
with the deployment's records and candidates. Choose one to bring it in,
matched to a record you hold or made a new one under the `bond` or
`certificate_of_deposit` template (`dashboard__find_instruments` and
`dashboard__bring_in_instrument` through an agent). A record lists the terms
its template wants that it lacks. See [The instrument master](../concepts/one-id.md).

## 2. Have its terms offered

Launch Terrapin's plugin (roles `data` and `reference`) or 9fin's (`ninefin`,
roles `reference` and `data`), and on its **Settings** enter:

- its key: Terrapin's API key, or 9fin's client ID and client secret,
  secrets never shown again;
- **Securities**: the bonds and CDs whose terms it offers, one ISIN or
  CUSIP a row, up to 500. Terrapin asks each of its monthly quota once a
  month, so list what you hold or watch.

Each listed security is resolved to its record, and the terms the source
states are **offered** to it, field by field, with their source and time.

## 3. Accept the terms

On the **Instruments** page, each offered term waits for a person to accept
it (`dashboard__accept_offered_values` through an agent, with a note). An
offer never overwrites a value a person set. Once the record carries every
term its template marks `complete`, the book takes it.

## Related

- [Bonds and fixed income](../concepts/bonds-and-fixed-income.md).
- [Read curves and prints](read-curves-and-prints.md).
