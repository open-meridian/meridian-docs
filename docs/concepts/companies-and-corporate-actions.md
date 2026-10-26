# Companies and corporate actions

Added in contract 28. A dividend is declared by a company about its
shares; a filing is made by a company, about itself or about another's.
The lake names the company as a subject of its own, beside the security,
so a reader can ask either. This page explains the **company kind**, the
record a company is named by, and **corporate actions**, the first of
which, the declared cash dividend, the options models read.

## The company kind

A company is a platform record with an `ENT-` ID, as an instrument is an
`INS-` record: its current name, its identifiers, each with its validity
window (`cik`, the SEC's Central Index Key, and `lei`, the Legal Entity
Identifier), and its former names, each with the dates it was used. The
platform mints it from EDGAR's submissions by CIK or from GLEIF by LEI. A
filer the platform cannot type as a company, such as a natural person, is
queued for its staff and never minted.

Your deployment's instrument store keeps each company record it is
answered, every version its own row. A `data` plugin resolves one with
[`resolve_company`](../api/typed-operations.md#resolve_company): by its
`ENT-` ID, or by a `cik` or an `lei` as of a date, against each
identifier's window. Two companies named at once are refused.

**A miss asks the platform.** Resolved by identifiers and not held, the
store asks the platform, sending only the `cik` or `lei` in a scheme on the
[licence list](one-id.md#the-licence-list), never a name. A company the
platform matches or mints is kept and answers. One queued for the
platform's staff, or a platform not reached, leaves the resolve a miss,
refused naming `identifiers`, nothing kept; the next miss asks again. A
miss by `ENT-` ID alone is not asked about.

## A subject's role

From contract 28 a row's subject may carry its **role**
(`SubjectRef.role`), so one row can name a security and its issuer, or a
holder and what it holds: `subject`, `holder`, `held`, `issuer`,
`reporting_owner`, `filer`, `underlying` or `rater`. A read naming a subject
in a role is answered only rows that name it so.

In the Python SDK a subject is `meridian.SubjectRef` with `role=`, and from
SDK 0.33.0 the typed operations take only it (see
[0.32.3 to 0.33.0](../api/python-sdk.md#0323-to-0330)).

## Corporate actions

A `data` plugin records each corporate action a company declares
([`record_corporate_actions`](../api/typed-operations.md#record_corporate_actions)),
its subjects the security and, beside it, its issuer as a company in the
`issuer` role. In contract 28 the one kind is a **declared cash dividend**,
`CORPORATE_ACTION_KIND_CASH_DIVIDEND`:

| Field | What |
|---|---|
| `amount_per_share` | As declared, a `Money` resolved to its currency's cash instrument |
| `declared_date`, `ex_date`, `record_date`, `payment_date` | Each required, a plain date as the declaration states it: the plugin never infers one |
| `rule` | The rule the plugin read it by, a definition and its version |
| `filing` | The filing it was declared in, its accession and form, where given |

A correction is the next version of its row key. Every version is heard as
`corporate_actions_recorded`, never conflated, by `reporting` and `signal`. `portfolio`, `reporting` and
`signal` read them
([`list_corporate_actions`](../api/typed-operations.md#list_corporate_actions)),
by subject, by kind and by a range of the kind's date (a cash dividend's
ex-date), point in time by recorded or published time; or every version
recorded after a watermark, whatever its dates.

**The options models read them.** The analytics component reads an
underlying's declared cash dividends for a chain, and the American model
prices on the share less its escrowed dividends: a dividend going ex before
an expiry moves that series' model price, and one going ex after it changes
nothing. The dividends' dataset is named in the answer's provenance (see
[Options measures](the-analytics-component.md#options-measures)).

## What core does not serve yet { #not-served-yet }

Contract 28 also carries the rest of the filings slice, which core serves
in a later chart release on the same contract: **filings**
(`record_filings`, `list_filings`, among them an 8-K's earnings date),
**reported facts** (`record_reported_facts`, `list_reported_facts`),
**holdings reports and holdings** (`record_holdings_reports`,
`record_holdings`, `list_holdings`) and **rating actions**
(`record_rating_actions`, `list_rating_actions`). Until then a deployment
answers each `UNAVAILABLE`, nothing serving it (the Python SDK raises
`CallFailed`, `kind="no handler"`). The data suite's cases about them carry
`about: filings`, `holdings` and `ratings`, so a plugin whose source
presents none names them not presented. See
[The lake: what core does not serve yet](the-lake.md#not-served-yet).

## Related

- [The lake](the-lake.md): datasets, reads and who reads what.
- [Instruments](instruments.md) and [One ID per instrument](one-id.md).
- [Typed operations: contract 28's](../api/typed-operations.md#contract-v28s-operations).
