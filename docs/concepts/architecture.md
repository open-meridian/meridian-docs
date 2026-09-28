# Architecture

Open Meridian is in two halves, run by different people in different places.

- **The platform**, at [open-meridian.com](https://open-meridian.com), is
  operated centrally by Open Meridian. It is where you manage your projects
  and deployments, and where instrument identity is kept.
- **Your deployment** is the runtime, installed into your own Kubernetes
  cluster beside your own database. It is where your people sign in, where
  plugins run, and where everything about your accounts and holdings lives.

The line between the two is the most important design decision in the
system. The platform deals in *identity*: which deployments exist, which keys
they hold, and what an instrument is. Your deployment deals in *data*: who
your people are, what they may do, and what you hold. Data does not cross the
line.

## The shape

```text
 open-meridian.com (the platform, operated by Open Meridian)
 +--------------------------------------------------------------------+
 |  projects and members  |  deployments and public keys  |  security  |
 |                        |  one-time codes               |  master    |
 +--------------------------------------------------------------------+
                                  ^
                                  |  HTTPS, outbound only,
                                  |  signed with the deployment's key
                                  |
 your cluster, beside your database
 +--------------------------------|-----------------------------------+
 |                                |                                   |
 |  people --HTTPS--> dashboard   conductor (holds the key,           |
 |  (browser, CLI)       |        |  configuration store)             |
 |                       |        |                                   |
 |        ===============+== bus (NATS broker) ==+==============      |
 |            |                  |               |           |        |
 |       instrument           street          sidecar     sidecar     |
 |         store              store              |           |        |
 |                                            plugin      plugin      |
 |                                                                    |
 |  launcher --> starts plugins from --> registry (plugin images)     |
 +--------------------------------------------------------------------+
```

A person reaches a plugin's page through the dashboard, which hands the
request to that plugin's sidecar; nothing else in the cluster reaches a
plugin.

## The platform

The platform serves four things, and holds no deployment data at all.

| What | What it is for |
|---|---|
| **Projects** | A project gathers the people who administer a set of deployments, each with a role. (Underneath, and in the API, a project is an *organisation*.) |
| **Deployments** | Each registered deployment has an identifier, `DEP-…`, and the **public** halves of the keys it has enrolled. The platform issues the one-time codes a deployment is set up with. See [Projects and deployments](projects-and-deployments.md). |
| **The security master** | Instrument identity and symbology, administered by Open Meridian staff and pulled by every deployment. It is identity, not a data store: prices, yields, ratings and other client-licensed data are never in it. See [Instruments](instruments.md). |
| **Staff** | Capabilities for the people who operate Open Meridian itself. |

The platform never holds a private key. A full copy of its key table would let
somebody verify a deployment's signatures and forge none of them.

## Your deployment

A deployment is one Helm release, `meridian-runtime`, installed into a
namespace of your cluster (`meridian` by default). Every component is in one
published image, `ghcr.io/open-meridian/meridian-runtime`.

| Component | What it does |
|---|---|
| **dashboard** | The one address your staff use. It signs people in — through your OpenID Connect provider, your LDAP, or accounts it holds itself — runs the first-run wizard and the administration pages, and serves each plugin's page on its own name, `<instance>.plugins.<host>`. It signs what it tells a plugin about a person with a key of its own, which is not the deployment's key. |
| **conductor** | The only component that holds the deployment's private key, and so the only one that reaches the platform. It also holds the configuration store: accounts, who may reach what, and the plugin catalogue. There is one conductor; redundancy means a standby, not a second one. |
| **instrument store** | What this deployment knows about instruments, and the answer to every instrument question, locally. It holds a copy of the identity the platform publishes, so resolution keeps working when the platform cannot be reached. |
| **street store** | What custodians say is held: statements, holdings and custodial positions. The one store whose contents nothing else can rebuild. |
| **sidecar** | One per plugin, bound to loopback in the plugin's pod. It holds that plugin's broker credential and enforces its grants. A plugin reaches its sidecar and nothing else. |
| **broker** | NATS, carrying the bus. Its permissions are generated from the grants, never written by hand. |
| **registry** and **launcher** | The deployment's own catalogue of plugin images, and the one component allowed to start a plugin once the conductor has approved it. |

Setting a deployment up also runs three Jobs: **key**, which has the
conductor's keypair made inside your cluster; **first-run**, which writes the
wizard's answers; and **migrate**, which prepares the database.

### The bus

Inside a deployment, components talk over one bus, carried by NATS. Topics are
named for what they carry, `platform.<domain>.<kind>.<action>`, where the kind
is `command`, `event` or `query`. Delivery is at-most-once: a message a slow
consumer cannot take is dropped rather than queued without end, so one stuck
plugin cannot become a stuck deployment.

Who may publish and subscribe to each topic is decided by Open Meridian's
contract, not by an operator. The broker's permission list is generated from
it when the broker starts, and regenerated when a plugin is launched or
stopped. The sidecar checks a plugin's grants before anything reaches the
broker, and the broker checks them again by the credential presented, so the
boundary holds even if a sidecar were not the one Open Meridian ships.

### Nothing keeps the right to change the cluster

Two things in a deployment need rights in Kubernetes, and both are narrow.

- The **first-run** Job may touch only resources the chart names, may create
  nothing, and deletes its own RoleBinding once it has applied the wizard's
  answers. After first run, nothing holds its rights.
- The **launcher** may create, update and delete Deployments in its own
  namespace, only in the chart's plugin shape, and only from an image in the
  deployment's own registry. It holds no key, no database and serves no
  browser. The conductor decides what to launch; the launcher only acts.

No component that serves a browser holds a right to change the cluster.

## What crosses between them

Everything that crosses is started by your deployment, over HTTPS, and signed
with the deployment's key. The platform never dials in. Only the conductor
makes these calls.

| From your deployment | What comes back |
|---|---|
| **Enrolment**: the public half of the key the conductor generated, with a one-time enrolment code | The key is registered against your deployment |
| **A missing instrument**: the global identifiers (FIGI, ISIN, CUSIP, SEDOL) of something the instrument store could not resolve | The instrument's record, if the master has it; otherwise the deployment may ask for one to be defined, which the platform may decline |
| **Component reports**: each component's name, version and health | Nothing; the platform shows them on the deployment's page |
| **A code a person typed**: a first-run, first-admin or password-reset code, with the deployment's identity | Yes or no. Nothing about the person who typed it is sent |

A deployment holds three things about the platform: one address, its own
identifier, and its key. It knows nothing about the platform's shape, so the
platform can scale, move or be redirected without anything in your cluster
changing.

### What never crosses

- Positions, holdings and statements.
- Your accounts, user groups, account groups, access groups and permissions.
- Who has signed in, and your directory's people and groups.
- Plugin settings and plugins' own data.
- Passwords, of any kind.
- The deployment's private key. It is generated in your cluster and never
  leaves the conductor's volume.

## When the platform is unreachable

Your deployment keeps working. People sign in against your own directory, not
the platform. Instruments the instrument store already holds keep resolving,
from its local copy. What waits is anything that genuinely needs the platform:
a new instrument the store has never seen, and redeeming a one-time code.

## What is not built yet

- **Order routing and execution** are on the roadmap. The `oms` and `ems`
  roles exist in the vocabulary, but no workflow grants them anything yet.
- **The firm's own book of record.** The street store holds what custodians
  say is held. A book calculated from the firm's own activity does not exist
  yet, and neither does reconciling the two.
