# Review provisional records and the migration

Every instrument a deployment holds is named by the
platform's `INS-` ID, and a record the platform has not answered for yet is
a **provisional** local record (see [One ID per instrument](../concepts/one-id.md)).
This page is for a deployment admin: where to see those records and why
each is waiting, how the upgrade to contract 24 migrates the records you
already hold, and the usage report's setting.

## Before you start

- You are a deployment admin. The **Instruments** page is theirs.
- Back up the deployment before upgrading to contract 24 (see
  [Back up and restore a deployment](back-up-and-restore.md)). The
  migration rewrites nothing, but the records the platform mints and the
  replacements it makes are recorded for good.

## The Provisional tab

Open **Settings**, then **Instruments**, then the **Provisional** tab. Its
label carries the count, such as **Provisional (4)**. The home page links
here too, from the line counting the provisional records ("See why").

Under **Provisional records** the tab lists each provisional record, one
line each, searchable with **Search provisional records**:

- **Record**: its `LCL-` ID, which opens the record and its history.
- **Description**: as the source stated it.
- **Why**: the reason it is provisional, in words.
- **Template**: the template it names and its version, such as
  `TPL-equity v1`, or "none yet" where its class is not known.
- **Missing**: the template's fields it lacks, or a dash.
- **Age**: how long since it was first recorded, such as "9 days".

With none it says "None: every record is the platform's."

The **Why** column reads one of:

- **the platform not reached; asked again on reconnecting**. Nothing to
  do: the conductor asks again once the platform can be reached.
- **incomplete or offline: its template's fields, or nothing to look for
  yet**. Where the **Missing** column names fields, the source has not
  given them; where it shows a dash, the record carries no identifier on
  the platform's licence list, such as a vendor's own code alone, so there
  is nothing to send. It resolves once the platform can match it, for
  instance when the licence list gains a scheme it carries.
- **with the platform's staff; asked again daily**. The platform's source
  could not confirm the security, and its staff review it.
- **class needed: no asset class stated**. Set the record's asset class
  on the **To complete** tab: the book refuses a position on it until
  then.
- **held back at the migration**. You held its line back at the upgrade;
  see [Hold a line back](#hold-a-line-back).

A provisional record is a **local line** in the book: recorded and
reconciled, never priced. Each resolves on its own when the platform
answers, its history reading across the link; nobody needs to act.

## The upgrade's migration

At the upgrade to contract 24 the instrument store sends every `LCL-`
record it holds to the platform as a matching request, in batches of at
most 100, at the pace the platform's licence list names. The run is a view
of the store, so it resumes where it stopped if the deployment restarts.
Records already keyed by an `INS-` ID stay as they are.

The answers are sorted into sections. The Provisional tab counts each,
under **The upgrade's migration**:

- **Already held**: the record already carried the platform's ID, such as
  a currency pulled from the platform's master.
- **Matched**: the platform holds the security.
- **Minted**: the platform's source confirmed it, and the platform minted
  it.
- **Near match**: minted, and flagged for the platform's staff to review.
- **With the platform's staff**: the request waits for their review.
- **Kept local**: nothing on the licence list to look for.
- **Not reached**: the platform could not be reached.
- **Held back**: lines you held back.
- **Still to send**: records not yet sent.

Below them, **Backfills** counts each scheme the licence list added after
the upgrade: how many records were linked, how many wait for a person, and
how many are still to send.

### Make the lines

A line is a record the platform answered: **Already held**, **Matched**,
**Minted** or **Near match**. Nothing is applied without you. Records with
the platform's staff, kept local or not reached are no lines: each stays
provisional, and resolves on its own once the platform answers.

Beside the counts, two buttons open the lines, each with its count:

- **Exact lines** opens **The exact lines**: each line's record, the
  `INS-` record it **Becomes**, and a **Hold back** box. They are made
  together, as one change, at most 500 at a time; with more, the dialog
  shows the first 500 and the rest are the next changes, in order.
- **Uncertain lines** lists each line to decide on its own, with **Why**:
  a duplicate (two `LCL-` records answered by one `INS-` ID, which become
  the one record, the book summing them), an identifier meeting another
  record, or a line you held back. Choose one line at a time.

To make them:

1. Open **Settings**, then **Instruments**, then the **Provisional** tab,
   and choose **Exact lines** or **Uncertain lines**.
2. Read the lines. In the exact lines, tick **Hold back** on any you are
   unsure of; in the uncertain lines, choose the line.
3. Say **Why**.
4. Choose **Make the lines** (or, for an uncertain line, **Make the line**
   or **Hold back**), or **Prepare** for someone to make it later (see
   [Prepared changes](../concepts/prepared-changes.md)).

On making, each line's record is replaced by its `INS-` record: its
positions move, its `LCL-` ID stays on the new record under
`open_meridian_local`, and its history reads across the link. A line
already made is unchanged. The change is made whole or refused whole,
naming each line that is not one the platform answered.

An agent may prepare the change for you with
[`dashboard__apply_migration`](../api/core-tools.md#dashboard__apply_migration),
which agents may only prepare until a deployment admin loosens it.

### Hold a line back

You may hold back any line. The record keeps its existing `LCL-` ID,
provisional, with the reason **held back at the migration**, and nothing
is minted for it; it moves to the uncertain lines, to be made later on its
own. A record minted after the lines were listed resolves on its own, as
any new one does.

Hold a line back when you are unsure the platform's record is the same
security: an uncertain line is better decided alone than applied with the
rest.

### After the migration

- The next weekly usage report carries its effect (see below).
- Every plugin hears each replacement, and reads what it missed.
- A plugin's table setting naming a replaced record is re-pointed by core
  as a recorded settings change.
- Check the book: quantities and positions are unchanged, now under the
  `INS-` records, and local lines are shown as not priced.

## The usage report

The **Licensed identifiers** tab shows how many identifiers in licensed
schemes your records carry, per scheme, kept here and never sent: only how
many are counted in the usage report.

Below it, **Report identifier usage** is on by default. While on, the
conductor sends the platform, weekly, for the last whole week, per
identifier scheme, how many records carry it, how many resolve only
through it and how many misses arrived with it alone: counts only, never a
value, a holding, a quantity or an account.

To turn it off or on:

1. Choose **On** or **Off** under **Report identifier usage**.
2. Say **Why**.
3. Choose **Set**, or **Prepare** for someone to make it later.

The tab then lists each report sent: its period, how many schemes it
counted, and whether the platform received it. With none it says "None
sent yet."

## Through an agent

- `dashboard__list_instruments_to_complete` with `provisional: true` lists
  the provisional records, each with its `provisional_reason`, and answers
  `migration_counts` and `backfill_counts`.
- `dashboard__apply_migration` makes the migration's lines, or holds them
  back, with a `note`; agents prepare it for you by default.
- `dashboard__set_reports_usage` sets the usage report, with a `note`.
- `dashboard__prepare_call` prepares a change for you to make.

See [Core's tools](../api/core-tools.md).

## Related

- [One ID per instrument](../concepts/one-id.md): `INS-` and `LCL-`
  records, the local line and the licence list.
- [Upgrade a deployment](upgrade-a-deployment.md).
- [Prepared changes](../concepts/prepared-changes.md).
