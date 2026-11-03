# Trade equities through Alpaca or Tradier

Place orders for US stocks and ETFs at Alpaca or Tradier, from a plugin
holding the `ems` role, through the Alpaca or Tradier plugin's
`connectivity` role. You need chart 0.1.408 and CLI 0.1.58.

## 1. Choose the environment and enter the key

Under the plugin's **Manage → Settings**, an admin of the plugin sets:

1. **Environment**, first. Alpaca: **Paper**, its paper trading API with
   simulated money, or **Live**. Tradier: **Sandbox**, its developer
   sandbox, or **Live**, your brokerage account. Each is Paper or Sandbox
   until a person chooses Live, and it must match the key.
2. **The key for that environment**: Alpaca's API key ID and secret key, or
   Tradier's access token. Secret settings, never shown again.

## 2. Link the account

A deployment admin grants the plugin the accounts it may link to, and its
admin links the broker's account to one of them on **Account links**, under
Manage. A deployment admin then grants people read or write on it.

## 3. Make it available to the desk, and map the account

A deployment admin makes the plugin available to the `ems` plugin, whose
admin links it and maps a book account to the account's **venue account
code**, shown on the plugin's **Connection**, Trading tab. See
[Route orders through a connectivity plugin](route-orders-through-a-connectivity-plugin.md).

## 4. Enable trading

A new account is read-only: every order on it is rejected `unsupported`,
nothing sent. An admin of the plugin's `connectivity` role presses
**Enable trading** on the Trading tab (the `enable_trading` tool, checked
by `check_enable_trading`). The plugin then publishes its catalogue. At
Alpaca: `market` and `limit`, each day, GTC, IOC or FOK, and `stop` and
`stop_limit`, each day or GTC; every order is placed directly.

Agents' orders go only to demo connections, Paper or Sandbox: see
[The agents' guard](../concepts/the-agents-guard.md).

## 5. Follow the order

Each fill is reported into the book and booked to its account; an order
placed in the broker's own app arrives as a
[venue-originated fill](answer-a-venue-originated-fill.md). See
[The order lifecycle](../concepts/the-order-lifecycle.md).

## Related

- [Using a custody plugin](using-a-custody-plugin.md): the same plugins'
  holdings and activity.
- [Set trading instructions](set-trading-instructions.md): pause or stop
  trading on an account.
