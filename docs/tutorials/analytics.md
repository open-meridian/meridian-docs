# Analytics

A figure such as an account's exposure or its value at risk takes more work
than a page's request should do. This tutorial builds a `reporting` plugin's
risk page that asks the deployment's analytics engine for its figures, works
them out when the book changes or on a cadence, keeps the answer per key, and
serves every request from what it holds.

You need SDK 0.35.5, CLI 0.1.58 and a deployment on chart 0.1.408.

## 1. Use the engine's measures

The deployment's [analytics component](../concepts/the-analytics-component.md)
computes the standard measures, exposure, concentration, historical VaR and
expected shortfall, execution cost, the bond and options measures, from the
book and the lake, read within your plugin's own scope and entitlements.
Ask it rather than writing your own: its answers are the same for every
plugin, held to reference computations, and named when a term is not
supported. `meridian.analytics.STANDARD_MEASURES` lists them.

```python title="src/my_risk/risk.py"
from meridian import analytics


def risk_job(account_id: str, business_date: str, currency_id: str) -> analytics.Job:
    return analytics.job(
        analytics.measure("exposure", by=["asset_class", "currency"]),
        analytics.measure("historical_var"),
        accounts=[account_id],
        business_date=business_date,
        reporting_currency=currency_id,
    )
```

`analytics.Jobs().run(role, job)` sends it and answers it, inline when it is
quick and waited for when it is not.

## 2. Work it out on change, or on a cadence

Choose by what the figure depends on:

- **On change**, for a figure that follows the book: work it out when the
  book says the account changed (`on_position_changed`), and only for that
  account.
- **On a cadence**, for a figure that follows prices: a day's VaR moves with
  every price, so work it out on a timer in the class's `run()`, at the rate
  the page needs, not on every tick.

```python title="src/my_risk/reporting.py"
import asyncio

import meridian
from meridian import analytics
from meridian.roles import reporting

from .risk import risk_job


class Reporting(reporting.Role):
    def __init__(self, state):
        self.state = state
        self.jobs = analytics.Jobs()
        self.dirty: set[str] = set()

    async def on_position_changed(self, heard: meridian.Heard) -> None:
        self.dirty.add(heard.message.position.account_id)     # note it; the work is in run()

    async def run(self) -> None:
        while True:                                            # restarted after a backoff if it fails
            due = self.dirty or set(self.state.accounts)       # changed ones, else all on the cadence
            self.dirty = set()
            for account_id in due:
                job = risk_job(account_id, self.state.business_date(), self.state.currency_id)
                self.state.answers[account_id] = await self.jobs.run(self, job)
            await asyncio.sleep(self.state.every_seconds)
```

## 3. Keep the answer per key

`state.answers` holds the latest answer per account. Keep one answer per key
the page shows, replace it when a newer one arrives, and let one no page has
asked for lapse: a key dropped after a while without readers, as views and
live values linger 30 seconds after their last reader, keeps memory flat.
Never hold every answer ever computed.

## 4. Keep heavy work off the request path

The page reads what `run()` worked out; it never runs a job itself.

```python title="src/my_risk/page.py"
import meridian

pages = meridian.Pages("Risk", templates=TEMPLATES)


@pages.page("/", "Risk", levels="read")
async def risk(request: meridian.Request) -> str:
    accounts = [a for a in STATE.accounts if a in request.caller.read]   # the person's own
    return pages.render("risk.html", answers={a: STATE.answers.get(a) for a in accounts})
```

- A request that runs a job makes every reader wait for it, and runs it once
  per reader.
- An account with no answer yet is shown as such, with why, never as zero.
- For figures that move while the page is open, serve them as
  [live values](live-pages.md), worked out from the state the class keeps.

## Next

- [Structure a plugin](structure-a-plugin.md): classes, helpers, settings and tests.
- [The analytics component](../concepts/the-analytics-component.md) and
  [`run_job`](../api/typed-operations.md#run_job).
