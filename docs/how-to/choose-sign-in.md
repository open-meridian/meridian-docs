# Choose how people sign in

A deployment signs people in one of three ways. You choose in the set-up wizard's **Signing in**
step, not at install. Nothing about sign-in is passed to `meridian up`.

Open Meridian runs no identity server of its own. There is nothing extra to size, back up or
upgrade.

| Choice | How it works | Use it when |
|---|---|---|
| **Your OpenID Connect provider** | The deployment federates to it. Your provider authenticates people. | You have Entra ID, Okta, Ping or similar. |
| **Your LDAP or Active Directory** | The deployment binds to your directory. It forwards a password once, stores none, and reads each person's groups. | You have a directory and no OIDC provider for this. |
| **No directory** | The deployment holds the account itself, with a hashed password and a lockout. | A trial, a laptop, or a firm with no directory of its own. |

!!! note
    The wizard is gone once you apply it. Decide before you choose **Apply**.

## To set up sign-in

1. Open the wizard, as in [Install a deployment](../getting-started/installation.md).
2. At **Signing in**, choose one option under **How people sign in** and fill in only that part.
3. At **Administrators**, name who runs the deployment.
4. At **Review and apply**, choose **Test**. It connects to your provider or directory from inside the
   cluster and names anything wrong. Fix it, test again, then choose **Apply**.

=== "OpenID Connect"

    Choose **Our own OpenID Connect provider** and fill in:

    | Field | What to enter |
    |---|---|
    | Issuer, exactly as the provider states it | Your provider's issuer, character for character, trailing slash and all. **Test** reads the discovery document and says if one character is off. |
    | Client id | The client you registered for the deployment. |
    | Client secret (none if public) | Its secret, or empty for a public client. |
    | Groups claim | The claim that carries a person's groups. Default `groups`. |
    | Other audiences a token may name | Usually empty. Fill it only if your provider puts something besides the client id in a token's audience; otherwise every sign-in is refused. |

    **Your provider must return `auth_time`.** It is what makes withdrawn access go away: it says
    when the person really authenticated. Open Meridian asks for it with `max_age=0` and
    `prompt=login`.

    | Provider | What to do |
    |---|---|
    | Microsoft Entra ID | Add `auth_time` as an optional claim on the app registration: Token configuration, add optional claim, ID token, `auth_time`. Entra does not send it otherwise. |
    | Okta | Nothing. It is sent when `prompt=login` or `max_age=0` is asked for. |
    | Ping | Check. Sign in once and look at the token. |
    | dex | Not usable. It does not implement `auth_time`. |

    !!! warning
        If your provider cannot return `auth_time`, do not work around it. Without it, someone
        removed from a group keeps their access until their session happens to end.

    At **Administrators**, enter the directory group, as your provider sends it in the groups
    claim.

=== "LDAP or Active Directory"

    Choose **Our LDAP or Active Directory** and fill in:

    | Field | What to enter |
    |---|---|
    | Servers, in order | For example `ldaps://ldap.firm.internal:636`. |
    | Use StartTLS | Tick it for an `ldap://` address. Without it, every password crosses your network as typed. An `ldaps://` address is already encrypted. |
    | Where people are | The base DN, for example `ou=people,dc=firm,dc=internal`. |
    | Account this deployment searches as | The bind DN, and its password. |
    | How a person is found | A filter where `{}` is the name typed. Empty means `(uid={})`. Active Directory usually wants `(sAMAccountName={})`. |

    **Test** binds with that account and reads where people are.

    At **Administrators**, enter the directory group whose members hold deployment admin.

=== "No directory"

    Choose **We have no directory: make me an account** and fill in your login name, email, given
    and family name, and a password of at least 12 characters, twice.

    That account is the deployment's administrator. The **Administrators** step asks for nothing. You
    use the same password to sign in to the dashboard and, through your browser, from the CLI.

    !!! note
        The wizard makes one account. The dashboard has no page for adding more accounts yet, so
        this choice suits one administrator trying Open Meridian. If that person loses their
        password, see [Reset a lost password](reset-a-lost-password.md).

## To name the administrators

With a directory, name one group. Its members hold deployment admin from their first sign-in.
Adding someone later is a change in your directory, not in Open Meridian.

!!! warning "Spell the group exactly"
    The group is not checked, because a directory states a person's groups only when they sign in.
    A misspelt group is a deployment nobody can administer. See
    [Recover administration](recover-administration.md).

## To answer from a file instead

`meridian up --params <file>` sends the same answers to the wizard, behind the same first-run code.
The field names are the wizard's own. The file holds no password: each one comes from a
`MERIDIAN_<FIELD>` environment variable, and a file that names one is refused.

```yaml title="first-run.yaml"
db_host: postgres.internal
db_port: 5432
db_name: meridian
db_serving_role: meridian_app
db_migrating_role: meridian_migrate
backend: ldap
ldap_servers: ldaps://ldap.firm.internal:636
ldap_base_dn: ou=people,dc=firm,dc=internal
ldap_bind_dn: cn=meridian,ou=services,dc=firm,dc=internal
admin_group: meridian-admins
dashboard_url: https://meridian.firm.example
```

```bash
export MERIDIAN_FIRST_RUN_CODE=…
export MERIDIAN_DB_SERVING_PASSWORD=…
export MERIDIAN_DB_MIGRATING_PASSWORD=…
export MERIDIAN_LDAP_BIND_PASSWORD=…
meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX --params first-run.yaml
```

`backend` is `oidc`, `ldap` or `local`. A field the wizard does not ask for is refused, with a
suggestion when one is close. See the [command line reference](../api/cli.md).

## Related

- [Access](../concepts/access.md): how sign-in feeds permissions.
- [Give people access](administer-access.md): what to do once people can sign in.
