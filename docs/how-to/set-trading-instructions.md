# Set trading instructions and whether releases wait

Two settings bear on every order a deployment works:

- **Trading instructions**: **active**, **pause** or **stop**, on an
  account, every account, a plugin, a person or a service account. Each
  plugin on the order path honours them.
- **Whether an account's releases wait for compliance**: while one does, an
  order is released only once every `compliance` plugin covering the
  account has answered on it. Every account waits by default.

Both are recorded in the [book of record](../concepts/the-book-of-record.md),
each change its own entry with who made it and why. See
[The order lifecycle](../concepts/the-order-lifecycle.md) for what each does.

## What an instruction does, and does not

- **The most restrictive in force governs**: stop over pause over active.
  An active on one target lifts nothing set on another.
- **An instruction is lifted only at the level that set it.** A plugin's
  admin narrows a deployment admin's instruction and never lifts it. The
  level is stamped from your access when you set it, never chosen.
- **The book refuses and cancels nothing for it.** It records the
  instruction and tells every `oms`, `ems`, connectivity, `portfolio` and
  `compliance` plugin, whatever their accounts. Each plugin honours it as
  its development provides: on a **pause** it sends no new orders; on a
  **stop** it sends none and cancels its working orders, a connectivity
  plugin cancelling at the venue at once. An order sent anyway is recorded
  with the instruction in force.
- **Nothing stands between a person and a stop.** Set at the page, it takes
  effect at once.

Whether a plugin honours instructions is the plugin's to show, by its tests
and `meridian plugin check` (see [Command line](../api/cli.md#plugin-check)).
Setting one is not a statement that any market's or regulator's controls are
met.

## To set a trading instruction

1. Open **Trading instructions**: from **Settings**, beside **Instruments**
   and **Data sources**; or, as a plugin's admin, from the plugin's line,
   beside **Its pages**, on a plugin holding a role that honours them
   (`portfolio`, `oms`, `ems`, `compliance` or `connectivity`).
2. Choose **+ Set**. The dialog is headed **Set an instruction**.
3. Under **On**, choose the target:

    | On | Who may choose it | Names |
    |---|---|---|
    | **All accounts** | a deployment admin | nothing more |
    | **A plugin** | a deployment admin; a plugin's admin, their own | the **Plugin** |
    | **An account** | a deployment admin; a plugin's admin, within their plugin | its ID, and the **Plugin** where it is within one |
    | **A person** | likewise | their login |
    | **A service account** | likewise | its `SA-` ID |

    A plugin's admin always names their plugin, and is refused **All
    accounts** and any plugin they do not administer.
4. Choose the **Instruction**: **Active**, **Pause** or **Stop**.
5. Say **Why**, kept with the instruction, and choose **Set**; or
   **Prepare**, for someone to make it later (see
   [Prepared changes](../concepts/prepared-changes.md)).

The page lists the instructions in force you may see -- every one for a
deployment admin, those naming a plugin you administer for a plugin's
admin -- one line each: **On**, **Instruction**, **Level** (**Deployment
admin** or **Plugin admin**), **Why** and **Set by**, searchable. With none
it says no instruction is set, and every plugin trades as usual.

**To lift one**, choose **Change** on its line, shown where you set at its
level, and set it to **Active**, with a reason.

**A user group is not a target yet.** An instruction naming one is
refused, naming `target.user_group_id`: aim a stop at an account, **All
accounts** or a plugin instead.

## Whether an account's releases wait for compliance

The Accounts tab's **Compliance** column says, for each account, **Waits**
or **Does not wait**. A new account waits.

- **Waits**: an order in the account is released only once every
  `compliance` plugin covering the account has recorded a verdict on the
  version released. Until then a release leaves it proposed, **awaiting
  check**, and refuses nothing.
- **Does not wait**: a release passes the gate with no verdict, the gate's
  other checks still applying.

A deployment with no `compliance` plugin releases nothing in an account that
waits. To change it:

1. On the **Accounts** tab, choose **Edit** on the account's row.
2. Under **In the book**, set **Releases** to **Wait for compliance** or
   **Do not wait**.
3. Enter a **Reason**, and choose **Save**.

Each attribute you change is its own entry in the account's journal (see
[To set an account's attributes in the book](administer-access.md#to-set-an-accounts-attributes-in-the-book)).

## Allow orders on local records

The **Trading instructions** page also holds a
deployment-wide setting, **Allow orders on local records**: whether an
order may name an instrument whose record is still a local record, one the
platform has not answered for yet (see
[One ID per instrument](../concepts/one-id.md)). It is a deployment
admin's.

It is **On** by default, in every deployment and after the upgrade that
brings it.
While on, such an order is marked "local record: not priced". Beside the
setting the page says how many live orders name a local record, such as "3
live orders on local records, not priced."; the home page shows the same
count, linking here.

To turn it off, or back on:

1. Open **Trading instructions** from **Settings**.
2. Under **Allow orders on local records**, say **Why**.
3. Choose **Turn off** (or **Turn on**), or **Prepare**, for someone to
   make it later.

Off, from the change on, a new order naming a local record, and an accept
of a venue-originated fill on one, are refused
(`REFUSAL_REASON_LOCAL_RECORD_NOT_ALLOWED`). Orders already working on a
local record continue: to stop them, set a trading instruction. A
telephoned or outside order the `oms` records is recorded whatever the
setting.

!!! note "TODO: contract v24, built, not released"
    The setting and its tool are in core for contract v24, to be released
    in chart `0.1.CHART24` (TODO: the date).

## Through an agent

Four of core's tools mirror these. The two that set take a `note`, kept as
the book entry's reason, and the two that list answer `outcome:
"unchanged"`. Each act is at the setter's level, can be prepared, and is at
**May not** for agents until the deployment admin loosens it (see [What agents may do](../concepts/prepared-changes.md#what-agents-may-do)):

- [`dashboard__list_trading_instructions`](../api/core-tools.md#dashboard__list_trading_instructions)
  and [`dashboard__set_trading_instruction`](../api/core-tools.md#dashboard__set_trading_instruction);
- [`dashboard__list_account_attributes`](../api/core-tools.md#dashboard__list_account_attributes)
  and [`dashboard__set_account_attribute`](../api/core-tools.md#dashboard__set_account_attribute),
  which sets one attribute at a time: the base currency, the lot-relief
  default, `waits_for_compliance`, `error_account` or
  `allocation_account`.

A fifth,
[`dashboard__set_local_record_orders`](../api/core-tools.md#dashboard__set_local_record_orders),
turns orders on local records on or off, at the deployment admin's level,
and at **May not** for agents until the deployment admin loosens it.

## Related

- [The order lifecycle](../concepts/the-order-lifecycle.md#trading-instructions):
  instructions, the release gate and waiting for compliance.
- [Route orders through a connectivity plugin](route-orders-through-a-connectivity-plugin.md).
- [Give people access](administer-access.md).
