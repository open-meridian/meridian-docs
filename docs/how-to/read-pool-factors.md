# Read agency pool factors and book a fill before its factor

Record the monthly factor of each agency pool and REMIC class you hold, from
the agencies' disclosure files, and see how the book prices a fill whose
settlement month's factor is not yet published. You need chart 0.1.408 and
CLI 0.1.58.

## 1. Arrange the files

The agencies publish their disclosure files to registered users, not by an
API:

- **Fannie Mae and Freddie Mac** (`gse-disclosures`): register for Fannie
  Mae's PoolTalk and its SFTP site, and Freddie Mac's secured data site,
  accepting each agency's terms for your firm.
- **Ginnie Mae** (`ginnie-mae`): sign in to Ginnie Mae's Disclosure Data
  Download.

Serve the files you download from a location over HTTPS, unchanged and
under the agencies' own names; a bearer token is supported.

## 2. Launch the plugin and point it at the files

Launch the plugin (roles `data` and `reference`) and, on its **Settings**,
enter **Files location**, the folder's HTTPS address, and **Files location
token** if it asks for one. **Payment calendar** is the platform's US dollar
calendar unless you name your own copy; a pool's record naming its own
payment calendar goes first.

On the **Data sources** page, license `gse-disclosures:fannie_mae` and
`:freddie_mac`, or `ginnie-mae:ginnie_mae`, and entitle the plugins that
read factors. The plugin's **Connection** reads Answering once the location
answers.

## 3. Read the factors

A pool's or class's factors are recorded when it is first asked for, and
checked daily after that, each exactly as published, with its factor month,
record and payment dates, and the pool's WAC, WAM and WALA where stated. A
corrected or final factor is the row's next version.

A plugin holding `operations`, `portfolio`, `reporting`, `servicing` or
`signal` reads them with [`list_factors`](../api/typed-operations.md#list_factors),
or `debt.read_factors(role, [pool_id], from_date, to_date)`, and hears each
new one with its role class's `on_factors_recorded`.

## 4. A fill before its factor

A pool's or a tranche's fill states **original face**. The book takes the
factor published for the fill's settlement month and keeps it with the fill
(`Execution.factor_taken`).

1. **Settling before its factor is published**, the fill is priced
   provisionally at the latest published factor, and the fill and its lots
   say which month they await (`Execution.factor_month_awaited`).
2. **When the factor is published**, the book writes its own
   `FACTOR_REVISION` record: the old and new factor, the cash and the cost
   change, and the fill it revises. Before the settlement date it settles
   with the fill.
3. **After the settlement date**, the revision is an **open claim**
   (`LIFECYCLE_EVENT_STATE_CLAIM_OPEN`), the money difference to collect or
   pay, until a person marks it settled. A plugin finds them with
   `debt.open_claims(events)` and marks one settled with
   `lifecycle.settle_claim(role, event, note)`.

The fill's cash, a provisional amount and each revision's differences round
to the cent, half-even.

## Related

- [Bonds and fixed income](../concepts/bonds-and-fixed-income.md#a-fill-before-its-factor).
- [Booking](../concepts/booking.md).
