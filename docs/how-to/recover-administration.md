# Recover administration

Use this when nobody can open the dashboard's **Settings**, which only a deployment admin can. Find
your case below.

| What happened | Go to |
|---|---|
| The deployment holds its own account, and its administrator lost the password | [Reset a lost password](reset-a-lost-password.md) |
| You use a directory, and the person who should administer is not in the administrators' group | [Add them to the group](#add-them-to-the-group) |
| The administrators' group was misspelt in the wizard | [Match the misspelt group](#match-the-misspelt-group) |
| The home page says **Nobody administers this deployment yet** | [Claim the deployment](#claim-the-deployment) |
| None of these works | [Start over](#start-over) |

## Add them to the group

With a directory, deployment admin comes from the group you named in the wizard.

1. In your directory, add the person to that group.
2. They sign out of the dashboard and sign in again. A directory states a person's groups when they
   sign in.

Nothing changes in Open Meridian itself.

## Match the misspelt group

The wizard does not check the group's name, because a directory states groups only at sign-in. A
misspelt group still grants deployment admin: to the members of a group that does not exist.

To get back in:

1. In your directory, make a group with exactly the name that was typed in the wizard, and add
   yourself to it.
2. Sign in to the dashboard again. You now hold deployment admin.
3. In Settings, open **User groups** and **Edit** the **Deployment admins** group. Add the correct
   group on its own line under **Directory groups**, keep the misspelt one for now, and choose
   **Save**.
4. Make sure you are in the correct group in your directory, and sign in again. Check you still hold
   deployment admin.
5. Edit **Deployment admins** again to remove the misspelt line, then remove the temporary group
   from your directory.

!!! warning "A first-admin code does not help here"
    A first-admin code is redeemed only on a deployment with no deployment admin permission at all.
    A misspelt group is still such a permission, so the claim page answers **Already claimed**.

## Claim the deployment

This applies only when the deployment has no deployment admin at all. The dashboard's home page then
says **Nobody administers this deployment yet**, with a **Claim it** link.

1. On <https://open-meridian.com>, as an **Owner** or **Admin** of the project, open **Deployments**.
2. Open the deployment's menu and choose **Issue first-admin code**. Copy the code. It is offered once
   the deployment has connected.
3. Sign in to the dashboard as the person who will administer it.
4. Choose **Claim it**, or open `/claim`. The page is **Claim this deployment**.
5. Enter the **Claim code** and choose **Redeem**.

You become the deployment's first deployment admin, and land in Settings. The platform learns that
the code was used, and not by whom.

## Start over

If you cannot get back in any other way, remove the deployment and install again. See
[Remove or start over](remove-or-start-over.md). If the deployment brought its own database, its data
goes with the namespace.

## Related

- [Give people access](administer-access.md)
- [Choose how people sign in](choose-sign-in.md)
