# The agents' guard

Agents work a deployment as the people who delegate to them, and a plugin's
autonomous work runs as a [service account](service-accounts.md). Either
can reach the [order path](the-order-lifecycle.md). The **agents' guard**
keeps their orders to demo connections: a deployment setting, **Agents may
place orders on demo connections only**, which the book enforces on every
placement whatever a page drew.

## The setting

The setting is on by default, and the upgrade to contract 26 records it on,
as the book's own entry, in every deployment. It **cannot be turned off**
in this release: the book refuses a change to off, and a deployment admin
may only record it on again, with a reason.

The dashboard's home page shows it ("Agents may place orders on demo
connections only: **on**"), with no switch while it cannot be turned off.
Setting it is a deployment admin's act, through
`dashboard__set_agent_orders_demo_only` with a note, and a person's alone:
an agent may prepare the change and never make it, whatever level the
deployment gives agents. Each change is its own record in the book.
`dashboard__read_agent_orders_demo_only` reads it, at the deployment
admin's level.

## What it refuses

While the guard is on, the book refuses, and records:

- **a placement** an `ems` creates, a child order's included, and
- **an accept of venue-originated fills to a new order**,

when it is **an agent's act**, made through a delegation or by a service
account, on a connection that is **not demo**. The refusal is
`REFUSAL_REASON_AGENT_LIVE_ORDER`.

It never refuses:

- **a person's own act** at a page;
- **an act a person makes from an agent's prepared change**: its actor is
  the person, through no delegation. An agent prepares a live placement,
  and a person decides it (see [Prepared changes](prepared-changes.md));
- **a cancel**, or any change to a placement already working;
- **an accept to an existing order**;
- **what a connectivity plugin reports** from its venue: fills, charges,
  a placement's state.

**Refused and recorded.** As a placement at a connection the `ems` may not
use, the refusal is an entry on the order: it names the `ems`, the
connection and the actor, with the words "Refused: Agents may place orders
on demo connections only", and is heard by the `ems` and `compliance`. A
refused accept leaves the fills unmatched, for a person to answer.

## How a connection's environment is decided

A connection is **demo** only where two keys agree, each recorded by a
different party:

1. **The setting.** A connectivity plugin for a vendor with more than one
   environment declares the setting `environment`: `live`, or the vendor's
   demo environment, `sandbox` or `paper`. It is core's record of what a
   person with admin on the plugin saved on its Settings form. Demo means
   `sandbox` or `paper`; `live`, any other value, or no setting at all is
   live.
2. **What the session reached.** The connectivity plugin reports, on the
   venue catalogue it publishes for each venue account code, the
   environment its session actually reached, read from the vendor's host
   it called: a broker's paper or sandbox service runs on hosts and
   credentials of its own. No report counts as live.

**Both must say demo.** A setting of `paper` with a session reporting
`live`, or reporting nothing, is live, and an agent's placement on it is
refused. Where they disagree, the connection fails closed.

**Who checks it.** When a person opens an `ems`'s page, or an agent or a
service account calls one of its acts, the dashboard puts in the claims
the plugin receives which of the connections that user may route through
are demo by their setting (`Caller.demo_connectivity_instance_ids`). The
`ems`'s sidecar then marks each placement demo only where its connection
is among them and that connection's session reports demo for the
placement's venue account code; the book refuses an agent's placement not
so marked. An accept to a new order names no connection, so it counts as
demo only where every connection the user may route through from that
`ems` is demo by its setting.

## The badges

Every connection is drawn with a badge:

| Badge | When |
|---|---|
| **Demo** | The setting is `sandbox` or `paper`, and every session of it reports `sandbox` or `paper` |
| **Live (environment not confirmed)** | The setting says demo, and a session reports otherwise, or nothing: the guard treats it as live |
| **Live** | The setting is `live`, unset, or any value but `sandbox` and `paper` |

The dashboard's home page draws it on each connectivity plugin. A plugin's
page draws the same with `meridian.connection_badge(setting, reported)`,
for one session's report, which says **Live (environment not confirmed)**
wherever the two keys disagree.

## For a plugin's author

- **Read the guard** with
  [`read_agent_orders_demo_only`](../api/typed-operations.md#read_agent_orders_demo_only),
  granted to `oms`, `ems`, `portfolio` and `compliance`.
- **Say so before sending.** `Caller.agents_act` says whether a call is an
  agent's, and `Caller.agent_refused(connectivity_instance_id,
  guard_on=...)` whether the book would refuse its placement on that
  connection. Give the act's check tool the same answer, so an agent
  learns it before it calls the act.
- **Catch the refusal.** The SDK raises `meridian.CommandRefused`, its
  `reason_name` `REFUSAL_REASON_AGENT_LIVE_ORDER` (see
  [The book's refusals](../api/typed-operations.md#the-books-refusals)).
  Do not retry it: offer the person a prepared change instead.
- **Report the environment reached.** A connectivity plugin names it on
  its catalogue: with `meridian.roles.connectivity`, its adapter's
  `environment` attribute, read from the host it called with
  `meridian.reached_environment(address, live=..., paper=..., sandbox=...)`.
  A plugin that reports none leaves its connections live for agents.
- **Declare the setting** with `meridian.environment()`, or
  `environment(demo="paper")` for a vendor that calls its demo service
  paper, first among the settings (see
  [Typed settings](../api/python-sdk.md#typed-settings)).

## Related

- [The order lifecycle](the-order-lifecycle.md): placements, connections
  linked to an `ems`, and venue-originated fills.
- [Prepared changes](prepared-changes.md): how a person makes what an agent
  prepared.
- [Service accounts](service-accounts.md): a plugin's autonomous work.
- [Route orders through a connectivity plugin](../how-to/route-orders-through-a-connectivity-plugin.md).
