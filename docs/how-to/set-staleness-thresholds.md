# Set staleness thresholds and the stale-reference action

How old a price may be before it is treated as stale is set in three
places: a data plugin's admin sets each dataset's threshold, a deployment
admin says whether a desk may warn rather than refuse, and an `ems`'s admin
sets the desk's own ceiling and what the desk does past it. Then, for a
plugin's author, how a data plugin records liveness and an `ems` makes its
check. What each number means is in
[Data age and liveness](../concepts/data-age-and-liveness.md).

You need a deployment on contract 28 (chart 0.1.31x or later) and plugins
on SDK 0.33.0 or later. On contract 27 the thresholds and the desk's
setting work as below, but there is no deployment's permission: the
`ems`'s admin chooses.

## A dataset's threshold

You need admin on the data plugin.

1. Open the data plugin under **Manage**, and its **Settings**.
2. Open the **Dataset thresholds** table. Each row is one of the plugin's
   datasets, the asset class its default came from, and **Stale after**,
   in seconds.
3. Change a row's **Stale after**, and save with why.

The lake answers it on the dataset at once, and every reader judges the
dataset's values by it, counted only in session. A delayed dataset is
judged against its declared delay plus this. Each change is recorded with
who made it and why, as every setting change is.

## What the deployment permits

You need to be a deployment admin.

1. Open the dashboard's settings home page, at **Stale reference actions
   permitted** (`/admin#stale-reference`).
2. **Change**, choose **Refuse only** (the default) or **Refuse or warn**,
   write why, and save; or prepare it for another person to make.

Each change is its own record, shown on the tab with who made it and when.
Through an agent, `dashboard__set_stale_reference_actions_permitted` with a
note.

## The desk's ceiling and action

You need admin on the `ems` plugin.

1. Open the `ems` under **Manage**, and its **Settings**.
2. In **Stale reference after**, set a ceiling in seconds for each asset
   class the desk trades. Only one tighter than the dataset's threshold
   changes anything.
3. Set **Stale reference action**: **Refuse**, the default, holds the order
   and places nothing; **Warn** sends the placement and marks it, where the
   deployment permits it, and is applied as **Refuse** where it does not.
4. Save with why.

A held order says why, typed, `HOLD_CAUSE_REFERENCE_PRICE_STALE`, with the
dataset, the price's age and the ceiling. Place it again once the price is
fresh.

## In a data plugin

Declare a delayed dataset's delay on its catalogue entry,
`DatasetDeclaration(declared_delay_ns=...)`, 0 for real time; one dataset
is one timeliness. Declare the thresholds' setting,
`meridian.dataset_thresholds()`, offering a default per asset class on the
plugin's page. Where the source sends only on change, or a poll finds
nothing new, record its sign of life:

```python
await wants.liveness("live", alive_at_ns=heartbeat_ns, venue_id=venue)
```

The data suite's `records-a-datasets-liveness` is `about: streams`: a
plugin that polls and streams nothing marks it not presented, with why.

## In an `ems`

Declare `meridian.stale_reference_after()` and
`meridian.stale_reference_action()`, then check the reference price
before each placement with `roles.ems.ReferenceCheck`:

```python
from meridian import roles
from meridian.roles import ems

liveness = roles.Liveness()            # kept from receive(liveness_recorded=liveness.heard)
check = ems.ReferenceCheck(
    action=config.stale_reference_action,
    after_ns=ems.after_ns(config.stale_reference_after),
    liveness=liveness,
)
await check.permitted(plugin)         # the deployment's Stale reference setting, read as the plugin
stale = check.stale(price, dataset=dataset_ref, asset_class="equity", sessions=sessions)
if stale is not None and check.refuses:
    await check.hold(plugin, order_id, stale)
else:
    await plugin.create_placement(..., **check.placement(stale))
```

`dataset_ref` is the price's dataset from
[`list_datasets`](../api/typed-operations.md#list_datasets), carrying its
threshold and delay; `sessions` its venue's trading sessions from
[`read_calendar`](../api/typed-operations.md#read_calendar). With no
ceiling set at all, nothing is stale. `check.refuses` is true for
**Refuse**, and for **Warn** where the deployment does not permit it. The
check records the price's age at its hop, which `roles.Latency` reports to
core. The ems suite's `reports-its-pre-trade-checks-data-age` and
`reads-the-stale-reference-actions-permitted` are required.

## Related

- [Data age and liveness](../concepts/data-age-and-liveness.md).
- [Set a plugin's settings](set-a-plugins-settings.md).
- [Typed settings](../api/python-sdk.md#typed-settings).
