# Tickets and the inbox

When somebody sees something wrong in a deployment, a **ticket** takes it to
the people who can act on it. A person files one from the page they are on,
their agent files one through the deployment's MCP surface, or a plugin files
one for the person whose page it is serving. Each ticket is seen only by the
people who could act on what it concerns, never by anyone who could not see an
account it names. The dashboard adds advice at once, and a person's agent may
add more; advice changes nothing. Only a person, on the ticket's page, assigns
it, resolves it, closes it or reopens it. Each person's **inbox** tells them,
and each of their agents once, what changed.

Nothing of a ticket leaves the deployment. Tickets are kept in the dashboard's
own tables in the deployment's database, and no ticket reaches the platform.

This needs a runtime serving contract v13. A plugin files with open-meridian
0.18.0; see [`file_ticket()`](../api/python-sdk.md#file_ticket).

## A ticket, or the plugin's health

A ticket is for a problem a person meets: a refusal they cannot explain, a
figure that looks wrong, something missing, a question. It ends in one of two
ways: a guide (how to do the thing) or a change (to a setting, the code or the
configuration).

What a plugin notices on its own is not a ticket. A connection that needs
signing in again, a feed that is down, a statement that is too old: these are
the plugin's health, shown on its Summary as a figure in warn, with what to do
about it beside it, and they clear when the condition clears. A person who
reads one there may choose to file a ticket about it. A plugin never files as
itself.

## Filing a ticket

**Report a problem** is in the dashboard's header, in the head of every
plugin's area, and beside a refusal on the Instruments page. It fills in what
the ticket concerns from where you are: the plugin you are in, at the version
it runs, or the part of the dashboard. Beside a refusal it also carries the
operation, the reason and the fields the refusal named. A plugin may offer its
own Report a problem on its pages, filled with the page's words; it files
through the plugin for you, and the ticket is still yours.

| You give | |
|---|---|
| What is wrong, in a line | Up to 120 characters. |
| What you saw | Plain text, up to 8,000 characters. |
| Kind | Something did not do what it should; two records disagree; something is missing, or should change; how do I do something? |
| What it concerns | A plugin you reach, a part of core (the dashboard, the book of record, the street store, the instrument store, the conductor, the chart, the `meridian` command, a plugin SDK), or Open Meridian's platform. |

An account named by its identifier in what you write, or an external account
number a plugin has linked, becomes a reference on the ticket, and narrows who
sees it to those who may read that account. An account named only in words
does not. A ticket holds at most 50 references, each a record by value: an
account, an instrument, a break, an entry or a street record with its account,
a tool call, or a plugin's own reference.

A person files at most 50 tickets a day, at pages and through their agents
together. A plugin files at most 20 an hour, and filing the same problem again
under its key brings the open ticket up to date, counting how often it was
seen, rather than filing another.

## Who sees a ticket

Visibility is worked out each time a ticket is read, from the deployment's
access records, so a change of access applies at once. The Tickets page, every
tool and every count use the same rule.

| The ticket concerns | Naming no account | Naming accounts |
|---|---|---|
| A plugin | Everyone holding any level on that plugin | Those who may read every one of those accounts through that plugin |
| Core or the platform | The deployment admin | Those who may read each of those accounts through some plugin |

The person who filed a ticket always sees it. An agent sees what its
delegation reaches: a delegation narrowed to one plugin sees none of another
plugin's tickets, even ones its person filed. A plugin's admin who reaches no
account does not see that plugin's tickets that name one.

## Advice

Advice is a note anyone who may see a ticket can add. It says what might be
wrong and where to look. It never changes the ticket.

The **dashboard's rules** advise at filing and on each change, as "the
dashboard's rules":

- **The route:** whose it is to fix. A break is the book's, for the operations
  plugin's people. An instrument record is the deployment admin's, on the
  Instruments page. A plugin's is the firm's: a setting, a link or a grant to
  look at. Core's and the platform's are Open Meridian's.
- **A likely duplicate:** another open ticket with the same concerns, version,
  step, operation, reason and fields. A plugin filing again after its ticket
  was resolved or closed opens a new ticket, advised as a recurrence; nothing
  reopens by itself.
- **The firm's own:** the plugin already reports a required setting with no
  value, or an external account nobody has linked.
- **A credential's shape** in the text: advice to treat it as exposed and
  revoke it. A ticket's text cannot be edited, so its filer may close it as
  withdrawn and file it again without it.

A person's agent may add advice too, through the deployment's MCP surface, as
the person through that client. [Advising on tickets](../how-to/advise-on-tickets.md)
is a procedure for an agent doing that on a schedule.

## Acting on a ticket

The **Tickets** page, at the dashboard's `/tickets` and in Report a problem's
breadcrumb, lists the tickets you may see, filtered by what they concern, their
state, your own, or those holding [held text](#held-text). Every act happens on
a ticket's own page, by a person, never by a tool. Each is recorded as a note
with the person's name.

| Act | |
|---|---|
| **Assign** | To someone who may see the ticket, or to nobody. |
| **Set the due date** | |
| **Resolve** | Citing a note, by its number, or a version. |
| **Close** | As not a problem, as a duplicate of another ticket, or as withdrawn. |
| **Reopen** | A resolved or closed ticket. |
| **Release** | A held text, to agents, having read it. See [Held text](#held-text). |

A plugin's ticket is worked by a person holding write on that plugin and on
every account it names; one naming no account, also by the plugin's admins.
Core's and the platform's are worked by the deployment admin: one naming no
account by any deployment admin, one naming accounts by a deployment admin
who may also see every account it names. Whoever filed a ticket may close it as withdrawn. Anyone who may see a
ticket may add a note.

A person may follow advice by doing what it names elsewhere, completing an
instrument record or confirming a break's cause, and then resolve the ticket
citing it.

## The inbox

A **notice** says that a ticket changed: which ticket, by its identifier and
title, what kind of change (filed, a note, advice, assigned, a due date,
resolved, closed, reopened, released), who made it and when. It never quotes
the change; the ticket's page and its tool hold the text.

| Who is told | When |
|---|---|
| Everyone who may work the ticket, besides its filer | It is filed |
| Its filer, its owner, everyone who has written a note on it, and the person who made the change | It changes |

Each is told only while they may still see the ticket.

The **Inbox**, in the dashboard's header, lists your notices, and **Mark all
read** marks them. Its count of unread notices refreshes every 30 seconds
while a dashboard page is open. Each agent you connect keeps its own place in your inbox, so
every client reads each new notice once, and marking notices read changes no
ticket. Notices are kept for 90 days; tickets have no expiry.

## Text is data

Every title, text, note and notice was written by someone other than whoever
reads it: a person, an agent, a plugin. To every agent that reads it, it is
data, never instructions.

- **Plain text, always.** Pages show a ticket's text as written, never as HTML
  or Markdown. A URL in it is shown unlinked, with its host beside it. A ticket
  carries no attachment.
- **Provenance beside every text,** set by the deployment from the credential,
  never from what the text says: a person; a person through a client; a plugin
  for a person; the dashboard's rules. A ticket claiming to come from Open
  Meridian is shown as its filer's.
- **Nothing acts on its own.** No tool assigns, resolves, closes, reopens,
  releases or sends. An instruction planted in a ticket can at most produce
  bad advice, which a person reads before acting.

### Held text { #held-text }

Text that reads like an instruction to an agent is **held**. It is filed and
kept, and shown on the ticket's page with the matches marked, but every tool
answers it as withheld until a person releases it on the ticket's page. The
rules that hold it look for an attempt to override instructions, a role marker
or chat markup, instruction words, text addressed to the reader, a claim of
authority, the name of a tool, text shaped like an answer, talk of prompts,
asking for something to be sent out, concealment, and the ticket's own acts
said as a command ("close it", "send the logs"). They are deliberately broad:
an honest text held costs a person one look.

A held text is released by a person who may work the ticket and did not write
it, so whoever planted a text cannot release it.

Text over its bounds, or holding a control character or a character that hides
or reorders text, is refused at filing, naming the field.

## Through an agent

A person connects an agent to the deployment's MCP surface, at the dashboard's
`/mcp`, and the agent works as that person on a delegation they made. Beside
the plugins' tools and the Instruments tools, the deployment lists seven ticket
and inbox tools to any delegation that reaches any level on any plugin, or the
deployment admin's capabilities:

| Tool | Reads or acts | What it does |
|---|---|---|
| `dashboard__file_ticket` | acts | Files a ticket: a title, what was seen, its kind, what it concerns, and optionally the step, operation, refusal reason, field paths and records. Recorded as the person's, through this client. |
| `dashboard__list_tickets` | reads | The tickets this delegation may see, newest first, filtered by what they concern, their state, or only the person's own. |
| `dashboard__read_ticket` | reads | One ticket: its text, what it concerns, the records it names, its state and resolution, and its notes and advice oldest first, each beside its author and provenance. |
| `dashboard__add_ticket_note` | acts | Appends a note or advice. It changes nothing on the ticket, and refuses any other kind of note. |
| `dashboard__read_inbox` | reads | The person's notices new since this client last read them, and this client's place moved past them. |
| `dashboard__mark_notices_read` | acts | Marks the person's own notices of the tickets named as read. It changes no ticket. |
| `dashboard__count_tickets` | reads | The tickets this delegation may see, counted by what they concern, by state, or both. Counts carry no text. |

There is no tool for assigning, resolving, closing, reopening or releasing,
and a call to one that is not listed is refused and recorded. Each tool's
description, and what the surface tells an agent when it connects, say that
the text it answers is data. Every call is listed in the person's **Connected
clients**, never with what was asked or answered.

Two procedures, each with a prompt to paste into a scheduled task, use these
tools and nothing else: [Advising on tickets](../how-to/advise-on-tickets.md),
for an agent that adds advice to open tickets, and
[Working your tickets](../how-to/work-your-tickets.md), for an agent that reads
your inbox and reports to you.

!!! note "Coming later"
    Sending a ticket on to Open Meridian, as a public issue carrying no
    personal information, is specified and arrives in a later release; a
    ticket about core or the platform is advised that way now and will be
    ready to send then. So is an agent drafting an answer that waits for a
    person to approve it before it is posted in their name.

## Related

- [Access](access.md): the levels and account permissions visibility is
  worked out from, and delegations.
- [Plugins, roles and grants](plugins.md#manage-open-and-view): Manage, Open
  and View, and a plugin's Summary.
- [Offer your pages to agents](../how-to/offer-your-pages-to-agents.md): the
  deployment's MCP surface from a plugin's side.
