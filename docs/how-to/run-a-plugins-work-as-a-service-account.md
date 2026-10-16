# Run a plugin's autonomous work as a service account

A plugin's autonomous work -- a scheduled sweep, a strategy, an agent inside
the plugin -- changes something in the deployment only as a
[service account](../concepts/service-accounts.md): a user of the
deployment that is not a person, with an owner who answers for it. Three
people set it up, each in their own place:

| # | Step | Whose | Where |
|---|---|---|---|
| 1 | **Create the service account**, its owner and its setting | a deployment admin | Settings, **Service accounts** |
| 2 | **Grant it** `write` on the plugin's role, over the accounts it is to act on | a deployment admin | Settings, **User groups**, **Access groups** and **Permissions** |
| 3 | **Choose what the role runs as** | an admin of the plugin's role | the plugin's **Access** tab, **Runs as** |
| 4 | **Watch it, and stop it if need be** | its owner | **Service accounts**, from their home |

Until all three are done, the plugin's work is refused, saying which is
missing, and changes nothing.

The sample operations plugin's sweep, which closes cleared breaks, is one
plugin's work that runs as a service account (see
[Using an operations plugin](using-an-operations-plugin.md#close-cleared-breaks-automatically)).

## 1. Create the service account

1. Open **Settings** (see [Give people access](administer-access.md#to-open-settings)),
   then the **Service accounts** tab, and choose **+ Add**. The dialog is
   headed **A service account**.
2. Enter its **Name**, up to 200 characters, and its **Purpose**, up to
   2,000: what it runs and why, for whoever reads its row later.
3. Choose its **Owner**: the person who answers for it, one the deployment
   knows (they have signed in, a user group names them, or the deployment
   holds their account). An owner is always a person.
4. Choose its **Setting**: **Prepare only**, the default, or **Act**.
    - **Prepare only:** every act it would make becomes a
      [prepared change](../concepts/prepared-changes.md) for the people who
      may make it. It never makes one.
    - **Act:** it makes an act where every level that applies lets agents
      make it and the act's second pair of eyes is off; otherwise it
      prepares it.
5. Say **Why**, and choose **Create**.

Its row shows its name, owner, setting, state (**Active**), the roles it
runs for (none yet), when it was last used and its last refusal. Its ID,
`SA-` and a ULID, is on the row's hover and on its page, **What it did**.

To change its name, purpose, owner or setting later, choose **Edit** on its
row. Each change is its own record, with who made it and why.

## 2. Grant it

A service account is granted as anyone is, and a new one is granted
nothing. On the plugin's role it needs `write`, over the account groups
it is to act on: an act needs `write`.

1. Make a user group for it, or use one: on **User groups**, its **People**
   list names it by its name, such as *The sweep (service account)*. Or enter its `SA-` ID under
   **Other logins**. See [To say who: make a user group](administer-access.md#to-say-who-make-a-user-group).
2. Make an access group giving the plugin's role at **Write**, such as the
   sample operations plugin's `operations`. See
   [To say what: make an access group](administer-access.md#to-say-what-make-an-access-group).
3. Grant the access group to the user group on the account groups it is to
   act on. See [To grant a permission](administer-access.md#to-grant-a-permission).

Whatever it is granted, it administers nothing: a grant at `admin` gives it
nothing, and it reaches no core act.

**To keep every service account to preparing an act** that people's agents
may make, give the service accounts a user group of their own, and on the
**Agents** tab or the plugin's **Access** tab set a stricter level for the
access group they hold (see
[What agents may do](../concepts/prepared-changes.md#what-agents-may-do)).

## 3. Choose what the role runs as

An admin of the plugin's role does this, on the plugin's admin view
(`/admin/plugins/<instance>`):

1. Open its **Access** tab and the part **Runs as**. Each of the plugin's
   roles has a line: what it runs as and at which level, or **nobody**, and
   how many service accounts are granted on it.
2. Choose **Edit** on the role's line. The dialog lists the service accounts
   a deployment admin granted on that role, each with its grant.
3. Choose one under **Runs as**, its **Level** (**Write**; an act needs
   it), say **Why**, and choose **Save**. **Nobody** clears it.

The level is never above the account's grant, and an account not granted on
the role cannot be chosen. Each choice, change and clearing is its own
record. A deployment admin reads the tab; only the role's admin sets it.

Where the account is later disabled or removed, or its grant withdrawn, the
choice stands and the line says so, **Disabled**, **Removed**, **Not
granted** or **Granted read**, and every call is refused until the grant
returns or the admin chooses again.

## 4. Watch it, and stop it

Its owner's home says "You answer for N service accounts", with a link to
**Service accounts**, `/service-accounts`: their own accounts' lines, read
only, with **Disable**.

- **What it did**, on its line, opens the account's page: **Its calls**,
  each act it called with when, the outcome (made, prepared or refused) and
  why refused; **Its prepared changes**, each with its state; and **Its
  record**, every change made to it. A prepared change opens on its own
  page, its contents within your own read access.
- **The Inbox**: each change it prepared, waiting for whoever may make it,
  you included, its preparer shown with you as its owner, such as *The
  sweep, a service account owned by Cat Ruiz*; and a notice when it is disabled or removed and by whom, and when
  each of its prepared changes lapses with it.

**To stop it**, choose **Disable** on its line and confirm. Its next call
is refused, and every change it prepared that still waits lapses, each its
own record. Only a deployment admin re-enables it (**Re-enable** on the
Service accounts tab) or removes it (**Remove**); a removed account is
never re-enabled, and every record it left is kept.

A role's admin may also stop the role's work by choosing **Nobody** under
**Runs as**, and a deployment admin by withdrawing its grant.

## When the plugin's work is refused

The plugin is told why, naming the field, and says it where it reports its
work; the account's line shows its **Last refusal**. The fix for each:

| The refusal says | Do |
|---|---|
| the role runs as no service account | step 3: its admin chooses one |
| the account is disabled or removed | a deployment admin re-enables it, or the role's admin chooses another |
| the account holds read, or nothing, on the role; or the role runs it at read | step 2: grant it `write` on the role; step 3: choose **Write** |
| the act is at may not | the deployment admin or the plugin's admin raises its level, if agents are to reach it |
| the act names no check tool, so it cannot be prepared, and the account is set to prepare only | set the account to **Act**, at may make; or the plugin's author names the act's check tool |
| a tool that is not one of the role's acts | the plugin's author: a service account reaches only its plugin's own acts on that role |

## Related

- [Service accounts](../concepts/service-accounts.md): the model, the
  levels' table and what is recorded.
- [Prepared changes](../concepts/prepared-changes.md).
- [Give people access](administer-access.md).
- [A service account runs the plugin's autonomous work](../api/python-sdk.md#runs_as):
  for a plugin's author.
