# Prepared changes

A **prepared change** is a change checked and kept, but not made: an agent
or a person prepares it, and a person makes it. Nothing in the deployment
changes until someone makes it, as their own act. Prepared changes let a
person's agent do the work of a change (fill in a long form, read the
statements, check it against the rules) while a person decides, and let a
firm say, per act, how far its people's agents may go.

## Preparing, making

Any act that can be checked can be prepared:

- **By an agent**, through the deployment's MCP surface, with
  [`dashboard__prepare_call`](../api/core-tools.md#dashboard__prepare_call):
  the act's tool as listed, its arguments as it would call it, and why.
- **By a person**, on the page where the act is made: **Prepare**, beside
  **Save** or **Confirm**, as on a plugin's Settings form.

The dashboard checks it as the act's own check would, with the preparer's
access: core's own checks for core's acts, and for a plugin's act the read
tool the plugin names as its check. A refusal comes back as the check's,
each field by its path, and nothing is kept. A change that passes is kept
with a `PC-` ID, and the person it is for sees it:

- **In their Inbox**, under **Prepared changes**: one line each, the act,
  who prepared it and through which client, why, its state and when.
- **On the page where they would make it**, the form started from what was
  prepared, marked "prepared by" with the reason, the whole of it a click
  away: a plugin's settings, and a plugin's own act that names its page.
  Any other act is made from the prepared change's own page, reached from
  the Inbox, with **Make**.

They then **make it** (the page's own Save or Confirm, or Make), **change it
first** and make it as changed, or **discard it**. The first who makes,
changes or discards it settles it for everyone it was shown to. Its preparer
may **withdraw** it while it waits.

A change an agent prepared through a person's delegation goes to that
person, and is shared with everyone else who may make it only if they choose
**Share**. One a person prepared on the page goes to everyone who may make
it. "Everyone who may make it" is everyone whose access lets them make that
change, the plugin, role, level and accounts it touches: no new kind of
group.

**Staleness.** When a prepared change is shown and again when it is made,
the dashboard checks it again. Still passing, it stays as prepared, even
where the record it was checked against changed in a part it does not
touch. Refused now, it is shown against what stands now, with the refusal
and what differs, for the person to change or discard.

**Lapse.** A prepared change waiting 30 days lapses, as does one whose
delegation ends; it is never made by lapsing. The deployment admin sets the
period, from 1 to 365 days, on the **Agents** tab.

**Its reason is another's words.** The reason a preparer gives is
untrusted text, screened as a ticket's is: shown as text, never followed,
and held as suspect when it reads like an instruction to an agent.

## What agents may do

Whether a person's agent may make an act, only prepare it, or not reach it
at all is the firm's to say, per act, at three levels:

| Level | An agent through a person's delegation |
|---|---|
| **May make** | makes it directly, or prepares it |
| **Prepare only** | prepares it; a direct call is refused, saying it may be prepared, and a person makes it |
| **May not** | neither: it is not listed to the agent, and a call is refused by name |

Two admins set them, and the stricter wins:

- **The deployment admin**, on the **Agents** tab of the dashboard's
  Settings, sets core's own acts, and a **ceiling** for every plugin's acts.
- **A plugin's admin** (an admin of the role serving the act) sets that
  plugin's acts on the plugin's **Access** tab, under **What agents may
  do**, within the ceiling. A level above the ceiling is shown capped, such
  as "Prepare only (capped at the ceiling; chosen May make)", never lost:
  raise the ceiling again and the plugin admin's choice applies.

Either may also set a stricter level for one access group (a user group, a
plugin's role and level, account groups), so the people in it, a group of
one included, may only prepare an act others' agents may make. An act
serving several roles is set by an admin of every one.

**The person can only be stricter.** On the consent page, when a person
connects a client, beside each row they choose **Make** or **Prepare
only**. "Prepare only" narrows the admins' "may make" for that delegation;
"Make" never lifts the admins' "prepare only" or "may not".

What a person may do by hand is still their access (see
[Access](access.md)); the levels add what their agents may do with it. The
Access tab shows both side by side for each act: who may make it by hand,
and what their agents may.

An act a plugin offers with no check tool cannot be prepared, so it takes
only "may make" or "may not". An act nobody has set is "may make", with the
second pair of eyes off.

## A second pair of eyes

Either admin may turn on an act's **second pair of eyes**: then nobody makes
that change alone. It is prepared, by a person or an agent, and made by
someone other than whoever prepared it, and other than the person behind
the agent that prepared it. On the page the act offers **Prepare** alone,
and a direct make is refused to a person and an agent alike. Turned on at
the ceiling, a plugin's admin cannot turn it off; on wins. It applies only
to an act that can be prepared. Turning it on leaves pending prepared
changes pending.

The levels and the second pair of eyes say what they do: an agent may only
prepare this act; the person who makes this change is not whoever prepared
it. Neither is described here as meeting any supervisory or regulatory
rule: whether they serve one is for the firm to judge.

## Prepared by a service account

A plugin's autonomous work acts as a [service account](service-accounts.md), and the levels and the second
pair of eyes bind it as they bind a person's agent, with its own setting,
**prepare only** or **act**, the strictest of them. Held to preparing, it
prepares the act through its check tool, as an agent does; an act with no
check tool is refused to an account set to prepare only.

- **It goes to everyone who may make it, at once**, and its owner is always
  shown it: there is no person whose own it is, so there is nothing to
  share. Its preparer is shown as the account and its owner, such as *The sweep, a
  service account owned by Cat Ruiz*.
- **Its owner counts as the person behind it.** Under a second pair of eyes
  the owner never makes what it prepared; with the gate off the owner may,
  like anyone who may make the act.
- **Its owner sees its contents within their own read access.** Where it
  names an account the owner may not read, its arguments are withheld from
  them, on its page and through `dashboard__read_prepared`.
- **It lapses with the account**: disabling or removing the service account
  lapses every change it prepared that still waits, each its own record
  saying why, and its owner is told.
- **No service account makes, discards or shares a prepared change**,
  whatever its setting: those are core's acts, which it does not reach.

## Deciding through an agent

Making, discarding and sharing a prepared change are acts too, each with
its tool (`dashboard__make_prepared`, `dashboard__discard_prepared`,
`dashboard__share_prepared`), and each is at **May not** until an admin
loosens it on the Agents tab. Even then an agent makes a prepared change
only where it could make the act itself, so "prepare only" cannot be got
around; never one it prepared; and under a second pair of eyes never one
its own person prepared.

## Every step is its own record

Each step of a prepared change (prepared, shared, checked again, shown with
what differs, made, changed, discarded, withdrawn, lapsed) is its own
record, naming who and when. The change made from it names the person who
made it and the prepared change it came from (`prepared_call_id`), beside
the delegation and client, in the store that keeps it. Each change to a
level, a gate or the lapse period is its own record too (who, when, the
act, where it applies, from and to, and why), set only at the page; an agent
reads them and never sets them.

## What can be prepared

| Area | Acts | A person prepares it | A person makes it |
|---|---|---|---|
| A plugin's settings | `dashboard__set_plugin_settings` (values, a table's rows, clearing a secret; never a secret's value) | **Prepare** on the Settings form or a table's tab | on the Settings form, started from what was prepared |
| The archive and holds | `dashboard__allow_archive`, `dashboard__withdraw_archive`, `dashboard__set_hold` | **Prepare** in the archive's dialog; in the Holds tab's dialog | with **Make**, on the prepared change's page |
| Launching and stopping | `dashboard__launch_plugin`, `dashboard__stop_plugin` | through an agent only (no page draws them) | with **Make** |
| Data sources | `dashboard__set_dataset_licence`, `dashboard__set_dataset_entitlement`, `dashboard__set_source_priority` | **Prepare** in the page's dialogs | with **Make** |
| Instruments | `dashboard__complete_instruments`, `dashboard__accept_offered_values`, `dashboard__merge_instruments`, `dashboard__ask_platform_for_instrument` | through an agent | with **Make** |
| A plugin's own acts | each act whose tool names its check tool | **Prepare** beside the page's own submit | on the page the act names, started from what was prepared; with **Make** where it names none |

Not preparable: tickets' acts, the prepared changes' own tools, and a
plugin's act with no check tool. A plugin makes its acts preparable by
naming each one's check (see
[Offer your plugin's pages to agents](../how-to/offer-your-pages-to-agents.md#let-an-act-be-prepared)).

## Where you see it

- **The Inbox**, **Prepared changes**: those waiting for you.
- **A prepared change's page**, `/prepared/<PC-…>`: the act, its arguments
  as prepared, the check's answer, who prepared it and why, its state and
  its history, with Make (or **Open on its page**), Discard, Share and
  Withdraw where you may.
- **Connected clients**: what each of your clients prepared and what
  became of it.
- **The Agents tab** (deployment admin) and a plugin's **Access** tab: what
  agents may do with each act.

## Related

- [Core's tools](../api/core-tools.md#prepared-changes): the tools.
- [Let your agent manage a plugin's settings and archive](../how-to/let-your-agent-manage-a-plugin.md).
- [Set a plugin's settings](../how-to/set-a-plugins-settings.md#prepare-instead-of-saving).
- [Tickets and the inbox](tickets-and-the-inbox.md).
- [Access](access.md).
- [Service accounts](service-accounts.md): the plugin's autonomous work,
  preparing by default.
