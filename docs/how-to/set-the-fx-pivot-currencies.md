# Set the FX pivot currencies

When the [analytics component](../concepts/the-analytics-component.md)
converts a fiat amount and the lake holds no rate between the two
currencies in either direction, it crosses through a **pivot currency**:
the first of the deployment's **FX pivot currencies** that both currencies
reach. Until a deployment admin sets them they are USD, then EUR. This page
changes them. You need to be a deployment admin.

## At the dashboard

1. Open the dashboard's settings, and under **Deployment** on the sidebar
   choose **FX pivot currencies**.
2. The section shows the pivots in order, such as **USD, EUR (default)**
   where they were never set, or **USD, then EUR, then GBP** and who set
   them, when.
3. Choose **Change**. The dialog, **Change the FX pivot currencies**, takes
   up to four ISO 4217 codes: **First**, required, and **Then (2)** to
   **Then (4)**. Fiat currencies only, none twice.
4. Enter **Why**, and choose **Change**.

The change is its own record, naming you and your reason. It moves the
crosses found by the next job on; an answer already given keeps the legs it
named. A direct rate, or one inverted, is always taken before a cross, and
a crypto asset's or a stablecoin's leg is never crossed.

## Through an agent

[`dashboard__read_fx_pivot_currencies`](../api/core-tools.md#dashboard__read_fx_pivot_currencies)
reads the setting, and
[`dashboard__set_fx_pivot_currencies`](../api/core-tools.md#dashboard__set_fx_pivot_currencies)
sets it, with the pivots' cash instruments by their `INS-` IDs and a note.
Agents may not make the change until a deployment admin loosens the act;
an agent may prepare it for you to make (see
[Prepared changes](../concepts/prepared-changes.md)).

## Related

- [The analytics component](../concepts/the-analytics-component.md#the-pricing-models):
  conversions, inverted and crossed legs.
- [Core's tools](../api/core-tools.md#the-deployments-settings).
