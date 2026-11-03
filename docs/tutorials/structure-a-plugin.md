# Structure a plugin

This tutorial lays out a plugin the way the SDK expects: one class per role,
the SDK's helpers for what every plugin of a role does the same way, settings
and secrets declared once, and tests that hold each class to its role's
behaviour. It builds a small `data` plugin that serves a made-up venue's daily
closes.

You need SDK 0.35.5, CLI 0.1.58 and a deployment on chart 0.1.408. Start from
`meridian plugin new my-closes --role data`, then `meridian plugin migrate`
to move it to 0.35.5.

## 1. One class per role

Each role the plugin declares in `pyproject.toml` is one class extending that
role's base. Its acts are its methods, and what it hears is its `on_<event>`
methods. A `data` class must hear `on_observations_wanted`: without it the
class is refused when it is made, naming the event.

```python title="src/my_closes/lake.py"
import meridian
from meridian.roles import data


class Lake(data.Role):
    """The plugin's data role: what the lake wants of it, answered."""

    def __init__(self, state):
        self.state = state
        self.wants = data.Wants(self, ("closes",))   # the SDK's want handling, given the role object

    async def on_start(self) -> None:
        await self.wants.read_licences()             # what it may record, before anything is heard

    async def on_observations_wanted(self, heard: meridian.Heard) -> None:
        await self.wants.hear(heard, self.answer)

    async def answer(self, want, key, subjects, kinds) -> dict[str, str]:
        """Record what the vendor has for `subjects`; answer what is declined, by subject."""
        prices, missing = await self.state.vendor.closes(subjects, want)
        if prices:
            await self.record_prices(prices=prices, want_id=want.want_id)
        return {subject: "not_covered" for subject in missing}
```

`data.Wants` hears the want, calls `answer` with the want, its dataset's
key, its subjects and its kinds, declines what it answers as declined, and
counts what was recorded.

- **State is shared by passing it.** One `State` object holds what the
  plugin's classes and pages share: its settings, its venue client
  (`state.vendor`), what it has fetched. Each class is given it.
- **Acts go through the role object.** A helper making an act is given the
  role object (`data.Wants(self, ...)`), never the connection. A page acts
  through the role object the plugin hands it.
- **Long-running work is `run()`.** A class's `run()` starts after every
  class's `on_start`, and is restarted after a backoff when it fails, the
  failure said on the plugin's health. Never start a loop of your own in
  `on_start`.

## 2. The entry point

```python title="src/my_closes/__main__.py"
import meridian

from .declaration import DECLARATION, PORT
from .lake import Lake
from .page import pages
from .state import State


def main() -> None:
    state = State()
    meridian.run(
        declaration=DECLARATION,
        roles=[Lake(state)],          # one class per role the plugin declares
        pages=pages,
        port=PORT,
        on_settings=state.configure,  # the typed settings, the first before any class starts
        figures=state.figures,        # read on every heartbeat
    )


if __name__ == "__main__":
    main()
```

`meridian plugin check` fails a role the plugin declares with no class
registered for it (`roles-registered`).

## 3. Settings and secrets

Declare settings once, as a typed class in the declaration, and read them
where `meridian.run` delivers them:

```python title="src/my_closes/declaration.py"
import meridian
from meridian.roles import data

PORT = 8000


@meridian.settings
class Config:
    api_key: str = meridian.setting("API key", required=True, secret=True)
    timeliness: str = data.timeliness("Timeliness", ("end_of_day",), "end_of_day")  # the SDK's common setting
    sample_data: bool = meridian.sample_data()


DECLARATION = meridian.Declaration(
    settings=Config,
    interface=meridian.Interface(port=PORT, title="My closes"),
    documentation="docs",
)
```

- **A secret is set by a person** on the dashboard's Settings form, never by
  the plugin, and reaches it only in the settings delivered: never log it,
  show it, or put it in a raw record.
- **Keep what a setting means in one place.** `State.configure(config)`
  rebuilds the venue client when the key changes; nothing else reads the
  settings.
- **The common settings are the SDK's:** `data.timeliness`, `data.api_key`,
  `meridian.environment()` for a vendor with a sandbox, and
  `meridian.sample_data()` for a development deployment.

## 4. Helpers, not copies

Logic every plugin of a role must do the same way lives in the SDK: take it,
never copy it from another plugin.

| What | Use |
|---|---|
| A session with a source, reopened and caught up | `meridian.helpers.sessions.Supervisor` |
| A dataset's business day and the market's open days | `meridian.helpers.calendars.DayClock`, `MarketDays` |
| A row sent again only when it changed | `data.SentRows` |
| The latest per key, once a period | `data.Conflator` |
| A polled source's standing wants at each dataset's cadence | `data.Timetable` |
| A chain, a package, a lifecycle event, a bond's money | `meridian.helpers.chains`, `.packages`, `.lifecycle`, `.debt` |

What faces the vendor stays the plugin's: its transport, its pacing, its
`Retry-After`, its allowance. See
[Each role's common logic](../api/python-sdk.md#each-roles-common-logic) and
[Helpers](../api/python-sdk.md#helpers).

## 5. Tests and behaviour cases

Hold each class to its role's suite, through the suites' recorder: it stands
in for the sidecar, records every act, and hands the class each row it hears.

```python title="tests/test_lake.py"
from meridian.plugin.v1 import operations_pb2 as ops
from meridian.suites import Recorder

from my_closes.lake import Lake
from my_closes.state import State


def a_want_for_spy() -> ops.ObservationsWantedEvent:
    want = ops.ObservationsWantedEvent(want_id="W-1", dataset="closes", data_type="prices")
    want.subjects.add(entity_id="INS-SPY")
    return want


async def test_a_want_is_answered():
    recorder = Recorder()
    recorder.answer("ObservationsWanted", lambda _: a_want_for_spy())   # what the row delivers
    lake = recorder.bind(Lake(State(sample=True)))                     # its acts are the recorder's
    await recorder.hear(lake)
    assert any(each.row == "RecordPrices" for each in recorder.sent)   # every act, recorded
```

- **Run the role's suite.** Each case the suite holds is mapped to your
  plugin, or named in `not_presented` with why where your source never
  presents it: see
  [Write a data plugin against its suite](../how-to/write-a-data-plugin.md#hold-it-to-the-suite).
- **Never give a class a stand-in connection.** `recorder.plugin` makes no
  act, so a class or page acting through the connection fails in its tests
  as it does when it runs.
- **Test the pages too**, with `meridian.testing.PageClient`, at each level.
- `meridian plugin check --run-tests` runs them, and CI runs the same.

## Next

- [Fast data retrieval](fast-data-retrieval.md): reading only what a page shows.
- [Role classes](../api/python-sdk.md#role-classes) in the Python SDK.
