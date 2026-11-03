# Fast data retrieval

A page that reads the lake on every request, for every subject and every
field, is slow for its reader and costly for the deployment. This tutorial
builds a `signal` plugin's watchlist page the fast way: it subscribes once
and is kept current, reads only the latest rows and only the fields it shows,
batches what it asks, and never reads again per request.

You need SDK 0.35.5, CLI 0.1.58 and a deployment on chart 0.1.408.

## 1. Subscribe, don't poll

A **view** is a read kept open: the SDK reads its snapshot once, then applies
each change the sidecar delivers, and reads the snapshot again only after a
loss. A page reads the view with no bus call.

```python
import meridian

WATCHLIST = ["INS-...", "INS-..."]                 # instrument IDs, at most 500
SHOWN = ["meridian.v1.Quote.bid", "meridian.v1.Quote.ask"]

pages = meridian.Pages("Watchlist", templates=TEMPLATES)


@pages.live("/quotes/live", levels="read")
async def quotes_live(request: meridian.Request):
    # One subscription per selector, shared by every page showing it.
    return await request.plugin.subscribe("QuotesRecorded", subjects=WATCHLIST, fields=SHOWN)
```

```html
<om-live src="quotes/live/events" snapshot="quotes/live" for="quotes"></om-live>
<om-grid id="quotes"></om-grid>
```

- **A snapshot, then changes.** The page reads `quotes/live` once and
  follows `quotes/live/events`; a gap or a reconnect reads the snapshot again.
- **Shared and lingering.** Identical selectors are one subscription, and it
  lingers 30 seconds after its last reader, so a reload does not churn it.
- **Polling** a read on a timer asks the lake again for what has not changed,
  and still shows each change late.

## 2. Ask for what the page shows

Every read takes the subjects it is about, and the lake's reads of rows take
`fields`, the dictionary entries the page draws: a field not asked comes back
unset. A chain's reads take `paths`, its template's fields, and an expiration
window.

```python
from meridian.helpers import chains
from meridian.roles import signal


class Signal(signal.Role):
    async def front_month(self, underlying: str):
        expirations = await chains.read_expirations(self, underlying)   # one small read
        return await chains.read_chain(
            self, underlying, expirations[0].expiration_date,
            paths=["put_or_call", "strike_price"],                       # only what the page draws
        )
```

Name the subjects; never read every subject to show a few.

## 3. Latest rows and listings come from memory

The lake keeps a **hot layer**: each dataset's latest rows per subject, and a
chain's series per underlying, in its own memory, the database remaining the
record. A read of the **latest now** (no `as_of_ns`, no valid-time range) or
a **listing as of now** is answered from memory when every key it names is
held; any other read goes to the record, never partly from memory.

| Read | From memory when held |
|---|---|
| `list_quotes(subjects=...)`, the latest per asset | yes |
| `list_trades(subjects=..., latest_recorded=True)` | yes |
| `list_series(...)` as of now | yes |
| any read with `as_of_ns`, a range, or every version | no: the record |

Each read's timing line in the lake's log says `from_memory`, true when every
row came from memory, and `layer`. If a page's reads say `record`, it is
asking for history it does not show. The bounds are chart values; see
[The hot layer](../concepts/service-levels.md#the-hot-layer).

## 4. Batch

- **Writes:** a `record_*` call takes 1 to 500 rows, recorded whole or
  refused naming the row. Send a pass's rows in one call, not one call a row.
- **Reads:** name up to 500 subjects in one read, and page with `cursor` only
  when a read says there is more.
- **Wants:** a data plugin answers a want with every subject it covers at
  once, and declines the rest in one call.

## 5. Never read again per request

A page's request should read what the plugin already holds: its views, or
what its role class worked out when the data changed.

```python
from meridian.roles import signal


class Signal(signal.Role):
    def __init__(self):
        self.latest = {}                       # what the page reads

    def subjects(self):
        return WATCHLIST

    async def on_quotes_recorded(self, heard: meridian.Heard) -> None:
        quote = heard.message.quote
        self.latest[quote.meta.subjects[0].entity_id] = quote


SIGNAL = Signal()


@pages.page("/", "Watchlist", levels="read")
async def watchlist(request: meridian.Request) -> str:
    return pages.render("watchlist.html", rows=SIGNAL.latest)   # no read here
```

A request that calls `list_quotes` reads the lake once per person per
refresh; the class above reads it once, at start, and is kept current.

## Next

- [Build a live page](live-pages.md): values worked out from views, with age,
  source and staleness.
- [Views and live values](../api/python-sdk.md#live-values) in the Python SDK.
