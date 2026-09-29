---
hide:
  - navigation
---

# Open Meridian documentation

Open Meridian is the open-source OEMS: the order and execution management
system you run yourself, in your own environment, and build on. Traders have
their AI agents build the tools their workflow is missing; developers write
their bots and analytics in Python. Each plugin talks only to its own sidecar,
which carries its credentials and enforces what it may touch, and every change
is live in about a second on a development deployment.

This site is how it works. For what it is and why, see
[open-meridian.com](https://open-meridian.com).

!!! note "What is live, and what is next"
    Live now: the deployment you run yourself, one identity for every
    instrument, your own sign-in and permissions, and plugins you write in
    Python, live as you save them. Next: broker connections, order routing and
    execution, built in the open.

## Where to start

<div class="grid cards" markdown>

-   **Getting started**

    ---

    Install the command line, bring a deployment up on your laptop, and run
    your first plugin.

    [Install a deployment](getting-started/installation.md)

-   **Build with an AI agent**

    ---

    Every new plugin carries `AGENTS.md`, the instructions any coding agent
    follows to build it and change it live.

    [Build with an AI agent](getting-started/build-with-an-ai-agent.md)

-   **Concepts**

    ---

    The platform and your deployment, plugins and their grants, access,
    accounts and instruments.

    [Architecture](concepts/architecture.md)

-   **How-to**

    ---

    Goal-oriented recipes: sign-in, access, a lost password, releasing a
    plugin, starting over.

    [How-to guides](how-to/index.md)

-   **Tutorials**

    ---

    Runnable walkthroughs, from changing a plugin's page live to recording a
    holdings statement.

    [Tutorials](tutorials/index.md)

-   **API reference**

    ---

    Every command, the Python SDK, and the typed operations a plugin calls.

    [API reference](api/index.md)

</div>

## At a glance

```sh
curl -fsSL https://raw.githubusercontent.com/open-meridian/meridian-cli/main/install.sh | sh
meridian doctor
meridian up --id DEP-… --development
meridian connect
meridian plugin new my-plugin && cd my-plugin
meridian plugin dev --instance my-plugin
```
