# Build a live page

A live page shows figures worked out from what the lake records, a mid, a
cross, a move since the open, and keeps them current without the reader
refreshing. This tutorial builds an FX rates page on `Pages.live_values`:
every value carries its source and its age, says when it is stale, counts
staleness only while its market is open, and is never blank.

You need SDK 0.35.5, CLI 0.1.58 and a deployment on chart 0.1.408. The base
template links kit 0.16.0, whose `<om-live cells>` draws the values.

## 1. The values, worked out from views

`pages.live_values(key, compute, views=...)` opens the views once, works the
values out with `compute`, and works them out again on each change of the
views, and once a second so an age, a session closing or a ceiling passed is
said. One set of values is kept per `key`, shared by every reader, and dropped
30 seconds after the last one leaves.

```python title="src/my_rates/page.py"
import meridian
from meridian import LiveValue
from meridian.helpers import sessions

PAIRS = {"EUR/USD": "INS-...", "USD/JPY": "INS-..."}   # name to instrument ID
pages = meridian.Pages("Rates", templates=TEMPLATES)


async def opened(plugin):
    return [await plugin.subscribe("QuotesRecorded", subjects=list(PAIRS.values()))]


def mid(quote) -> str:
    return str((meridian.as_decimal(quote.bid.amount) + meridian.as_decimal(quote.ask.amount)) / 2)


def compute(views):
    by_id = {q.meta.subjects[0].entity_id: q for q in views[0].rows().values()}   # each a Quote
    values = []
    for name, instrument_id in PAIRS.items():
        quote = by_id.get(instrument_id)
        if quote is None:
            values.append(LiveValue.of(f"pair:{name}", {}, [], why="no quote yet"))
            continue
        values.append(LiveValue.of(
            f"pair:{name}", {"mid": mid(quote)}, [quote],
            datasets=STATE.datasets,          # the lake's listing: each dataset's ceiling and delay
            sessions=sessions.FX_WEEK,        # Sunday 17:00 to Friday 17:00 New York
        ))
    return values


@pages.live("/rates/live", levels="read")
async def rates_live(request: meridian.Request):
    return await pages.live_values("rates", compute, views=lambda: opened(request.plugin))
```

`STATE.datasets` is what the plugin read from
[`list_datasets`](../api/typed-operations.md#list_datasets) at start, so each
value knows its dataset's declared delay and stale ceiling.

## 2. The cells

```html title="src/my_rates/templates/rates.html"
<om-live cells src="rates/live/events" snapshot="rates/live"></om-live>
<table>
  {% for name in pairs %}
  <tr data-live="pair:{{ name }}">
    <th>{{ name }}</th>
    <td data-f="mid"></td>
    <td data-f="age"></td>
    <td data-f="source"></td>
    <td data-f="limit"></td>
    <td data-f="why"></td>
  </tr>
  {% endfor %}
</table>
```

The kit fills `mid` from the value, and `age`, `source`, `state`, `limit` and
`why` itself, counting each age on once a second. It marks a row
`data-stale`, `data-closed`, `data-missing` or `data-no-limit`, for your CSS.

## 3. What each value says

- **Its source**: the dataset it was worked out from.
- **Its age**: from the oldest input's confirmed time, its source's own time,
  or for a quote stating none its `valid_from_ns`.
- **Stale**, past the tighter of its dataset's ceiling and an admin's, after
  the dataset's declared delay. **Staleness counts only in session:** given
  `sessions.FX_WEEK`, a value on Saturday is **closed**, shown with its age,
  never stale. Give the sessions of the value's own market; `FX_WEEK` is the
  one to use where an FX dataset names no calendar of its own.
- **No stale limit declared**: with no ceiling from the dataset or an admin,
  a value is never flagged stale, and the page says so beside its age.
- **Never blank**: a value with nothing to show says why (`why`, or "nothing
  heard yet"). A cell left empty is a cell the reader cannot trust.

## 4. The update rate is bounded

Values leave for the page at most once every 250 ms, the latest per key, so a
fast market redraws four times a second at most and a slow one only when it
changes. Do not push faster from the page, and do not add a timer that reads
again: the kit counts ages on by itself.

## 5. Check it

Open the page at 375, 582 and 1280 pixels wide, in light and dark. Every row
shows a value or why it has none; on a weekend each FX row shows closed with
its age.

## Next

- [Analytics](analytics.md): heavier figures, worked out off the request path.
- [Data age and liveness](../concepts/data-age-and-liveness.md).
