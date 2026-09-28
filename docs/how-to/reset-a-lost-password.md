# Reset a lost password

This is for a deployment that holds its own accounts, the **No directory** choice in the wizard,
when its administrator has lost their password. Nobody else can sign in to reset it, so the reset
starts on the platform.

!!! note "Using a directory?"
    If the deployment signs people in through your OpenID Connect provider or LDAP, passwords live
    there. Reset it in your directory. The deployment's reset page says the same.

## Before you start

- Someone who is an **Owner** or **Admin** of the deployment's project on the platform. It can be the
  person who lost the password.
- The deployment shows **Connected** on the platform. Password-reset codes are offered only once it
  has connected.
- The login name of the account to reset.

## To reset the password

1. On <https://open-meridian.com>, open the project, then **Deployments**.
2. Open the deployment's menu and choose **Issue password-reset code**. Copy the code. It is shown
   once.
3. Open the deployment's sign-in page and choose **Lost your password?** It opens **Reset a
   password**, at `/sign-in/reset`.
4. Fill in:
    - **Password-reset code**: the code from step 2.
    - **Login**: the account's login name.
    - **New password** and **New password, again**: at least 12 characters, the same twice.
5. Choose **Set the password**.

The sign-in page then says **Your password is set. Sign in with it.**

## What happens

- Every session the account held ends, in browsers and in terminals. Run `meridian connect` again on
  each machine that used it.
- The account's failed attempts and any lockout are cleared.

!!! warning "The code is spent when you submit"
    If the two passwords differ or the new one is too short, the page says so and the code is not
    used. After that, the code is spent even if the login is wrong. Only a local account holding
    deployment admin can be reset this way. Anything else is refused with "The code was spent: ask
    for another."

## Related

- [Recover administration](recover-administration.md): other ways to get back in.
- [Choose how people sign in](choose-sign-in.md)
