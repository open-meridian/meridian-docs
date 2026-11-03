# Read curves and prints

Record government curves, inflation indexes, municipal and corporate bond
prints and bond quotes in your deployment's lake, from Terrapin and
OpenYield. You need chart 0.1.408 and CLI 0.1.58.

| Plugin | Datasets | What they hold |
|---|---|---|
| Terrapin | `government_curves`, `inflation`, `msrb_prints` | Government par yield curves (US, UK, Germany), inflation index levels, and municipal bonds' prints as MSRB disseminates them |
| OpenYield | `marketplace`, `trace_prints`, `msrb_prints` | Its ATS's firm top of book, mids and live US Treasury benchmark curve; FINRA TRACE and MSRB prints, each naming its source |

## 1. Launch it and enter its access

- **Terrapin**: approve `data` and `reference`, and enter the **Terrapin API
  key** and the **Securities** whose prints are kept current. It reads at
  once and every hour: the last five business days' curves and the listed
  bonds' prints of the last seven days, and the inflation indexes daily.
- **OpenYield**: access needs an OpenYield Data Services Agreement. Ask
  OpenYield for a token issued to your account and enter it as the
  **OpenYield token**; the plugin never holds a password. Enter the
  **Securities**, up to 500 by ISIN, CUSIP or FIGI. It reads at once and
  every five minutes.

## 2. Accept the curves' records

Each curve and index is a record of your deployment named by its source's
code, such as `TERRAPIN_US_PAR` or `OPENYIELD_UST_BENCHMARK`. The plugin
states its class, type, currency and description: **accept them on the
Instruments page** before its rates are recorded. Until then the plugin's
**Datasets** page says each waits.

## 3. License, entitle and read

On the **Data sources** page, license each dataset on the terms of your
agreement with the vendor (and FINRA's and MSRB's for the prints): the
plugins declare no default terms. Entitle the plugins that read them, and
set the priority where another dataset records the same curve or
security.

A curve's points are rates: read them with
[`list_rates`](../api/typed-operations.md#list_rates) (see
[Rates](../concepts/rates.md)). Prints are trades and the ATS's top of book
is quotes: `signal` and `ems` read them with
[`list_trades`](../api/typed-operations.md#list_trades) and
[`list_quotes`](../api/typed-operations.md#list_quotes). A bond's price is
per 100 of face, with its yield or spread beside it as quoted.

## Related

- [Bonds and fixed income](../concepts/bonds-and-fixed-income.md).
- [Bring in a bond and complete its terms](bring-in-a-bond.md).
