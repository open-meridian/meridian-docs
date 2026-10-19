# Write a pricing plugin

A pricing plugin, one holding the role `pricing`, answers the
[analytics component](../concepts/the-analytics-component.md)'s price
batches for the pricing models a deployment admin routes to it: a firm's
own implementation of a model, run as its own plugin behind the same API.
It is never called by a client, holds no accounts and keeps no records:
for each unit of a batch, one instrument under one scenario with exactly
the market objects its model declares, it answers a value per unit, and
nothing else. The role has a conformance suite, carried by the SDK. This
page starts one from the template and holds it to the suite.

You need CLI 0.1.50 and SDK 0.31.1 or later (contract 26): `meridian plugin
new --role pricing` writes this template on the role's common part, for a
runtime serving contract 26.

## Make the plugin

```sh
meridian plugin new my-pricing --role pricing
cd my-pricing
```

It writes a whole plugin holding `pricing`, pinned to
`open-meridian==0.31.1`, that answers `quoted_price` batches with the
built-in model's own computation:

| File | What it is |
|---|---|
| `src/my_pricing/model.py` | Its **models**, by model id. Replace them with your own. |
| `src/my_pricing/__main__.py` | Connects to its sidecar and runs the SDK's `Pricer` over the models: the batches still waiting, then each batch as it is routed, until it is stopped. |
| `src/my_pricing/declaration.py` | Its declaration: its page and its documentation. It declares **no storage**: `pricing` is not a role at the edge. |
| `src/my_pricing/page.py`, `templates/` | Its one page under Manage, **Batches**: the model ids it implements, the batches answered since it started, the last sequence answered, and each batch left unanswered with why. Counts and codes, never a price. Also a read tool for an agent, `read_batches`. |
| `tests/test_suite.py` | The pricing suite, each case run through the `Pricer` over the plugin's own models. |
| `tests/test_page.py` | Its page's tests. |
| `docs/` | The documentation a deployment admin reads before launching it: see [Write a plugin's documentation](write-a-plugins-documentation.md). |

`AGENTS.md` teaches a coding agent the role's rules beside the template's
own.

## What a batch carries

A batch (`PriceBatchRequest`) names its `model_id` and `model_version`, a
`deadline_ns`, a `batch_hash` naming it, its place in the plugin's
`sequence`, and its `units`. Each unit (`PricingUnit`) is one instrument
under one scenario:

| Field | What |
|---|---|
| `instrument_id`, `template_version` | The instrument, and the version of the template its record names |
| `scenario_key` | The scenario it is priced under: the base, or another the batch names |
| `inputs` | Exactly the market objects its model declares, each a `MarketObjectValue`: its `subject_id`, the lake's `kind` (`close`, `nav`, `mid`, `last`, or `outcome`), its `value`, a `Money` in the asset it is quoted in, and the `dataset` it came from |

For `quoted_price`, the inputs are the instrument's price, of the kind its
template names, then each conversion leg to the account's base currency:
the price of the currency in hand in the next. For `cash`, the conversion
legs alone. For `binary_event`, once the venue's determination is final,
an `outcome` input, the settlement value per contract in the payout's
currency, takes the price's place.

## Write a model

A model is a function of one unit, `(batch, unit) -> meridian.Money`: the
unit's value per unit, in the base currency its inputs convert to. The
template's `model.py` maps model ids to models:

```python
from meridian.roles import pricing

MODELS: dict[str, pricing.Model] = {"quoted_price": pricing.reference_model}
```

`pricing.reference_model` is the built-in models' own computation for
`cash`, `quoted_price` and `binary_event`. A model of your own reads the
unit's inputs and nothing else, every number a `Decimal`, never a float.
This one is `quoted_price` written out, the price times each conversion
leg, until none leads further:

```python
import meridian
from meridian.plugin.v1 import operations_pb2 as ops


def quoted_price(batch: ops.PriceBatchRequest, unit: ops.PricingUnit) -> meridian.Money:
    prices = {}
    for each in unit.inputs:
        money = meridian.as_money(each.value)
        prices[each.subject_id] = (money.amount, money.instrument_id)
    value, held = prices[unit.instrument_id]
    while held in prices:          # each conversion leg, until none leads further
        rate, held = prices[held]
        value *= rate
    return meridian.Money(amount=value, instrument_id=held)


MODELS: dict[str, pricing.Model] = {"quoted_price": quoted_price}
```

The rules a model keeps:

- **Answer in the base currency, naming it.** The value's `instrument_id`
  is the cash instrument the unit's last conversion leg is in. A value in
  another asset is not taken, and the figure through it is not evaluated.
- **Equal the built-in model on its model id.** A v26 model id is defined
  by the built-in implementation, and the suite holds your answer to it
  exactly, digit for digit.
- **Read nothing else.** No position, no account, no other price: the batch
  carries everything the model declares.
- **Raise rather than guess.** A model raising for a unit leaves the whole
  batch unanswered, and the figures through it are not evaluated,
  `IMPLEMENTATION_UNAVAILABLE`: never half a batch. A batch for a model id
  the plugin does not implement is left unanswered too. Either is listed on
  the Batches page with why.
- **Send no sensitivities.** No model in this release declares one, so
  the `Pricer` answers each batch with none.

## The Pricer's work

`meridian.roles.pricing.Pricer` does the rest:

- **Each batch answered whole**, with
  [`answer_price_batch`](../api/typed-operations.md#answer_price_batch): a
  `PricedUnit` per unit, its instrument, its scenario and its value per
  unit.
- **After a restart**, the batches still waiting after the last sequence it
  answered, with
  [`list_price_batches`](../api/typed-operations.md#list_price_batches),
  then each batch as it arrives. It keeps that sequence in memory
  (`pricing.Sequence()`), since the plugin holds no storage, so a restart
  reads every batch still waiting. A batch answered twice is harmless:
  named by its hash, it is taken once, and an answer after its deadline is
  not taken at all.

## Hold it to the suite

`tests/test_suite.py` runs the pricing suite through the `Pricer` over your
models, against a `Recorder` that records the plugin's operations rather
than sending them. Its five cases:

| Case | Given | Expected |
|---|---|---|
| `answers-a-batch` | A `quoted_price` batch, one instrument under the base scenario with its close | An answer naming the batch, with the instrument, its scenario and a value per unit |
| `answers-every-scenario-of-a-batch` | One instrument under several historical days' closes | A value per unit for each day, under its scenario |
| `equals-the-built-in-model` | The equity template's test case: a close of 227.50 USD | 227.50 USD per unit, exactly |
| `carries-no-sensitivity` | A model declaring no sensitivity | No sensitivities |
| `reads-the-batches-waiting-after-a-restart` | A restart with batches routed and unanswered | The batches read after the last sequence answered |

As you change the models, keep every case passing. Then hold the plugin to
the framework's rules as a verified plugin, in a virtual environment of its
own:

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -e . pytest
meridian plugin check --verified --run-tests
```

`--verified` fails `role-suite` where no test runs the pricing suite, and
`--run-tests` runs it; see [`plugin check`](../api/cli.md#plugin-check).

## Put it in a deployment

```sh
meridian plugin upload
meridian plugin launch my-pricing 0.1.0 --instance my-pricing-1
```

or, on a development deployment, `meridian plugin dev --instance
my-pricing-1`. Launched, it answers nothing until a deployment admin
routes a model id to it: on the dashboard's **Settings**, **Model routing**
tab, **Change** that model id's implementation to `my-pricing-1`, saying
why, or through `dashboard__set_model_routing` with a note. The routing is
deployment-wide, per model id, and each change is its own record. Every
job's answer then names `my-pricing-1` as that model's implementation in
its provenance.

**A routed plugin must answer in time.** A batch not answered by its
deadline, five seconds by default, leaves every figure through the plugin
not evaluated, naming it; the built-in model is never put in its place.
Before stopping a routed plugin, route its model ids back to `built-in`.

## Related

- [The analytics component](../concepts/the-analytics-component.md): jobs,
  the measures, the models and the pricing seam.
- [The `pricing` role](../concepts/roles.md#pricing).
- [Contract 26's operations](../api/typed-operations.md#contract-v26s-operations).
- [Each role's common logic](../api/python-sdk.md#each-roles-common-logic)
  in the Python SDK.
- [Release a plugin version](release-a-plugin.md) and
  [Publish a plugin to a registry](publish-a-plugin.md).
