# Remove or start over

There are three separate things you might want to remove: the deployment from your cluster, the
deployment's record on the platform, and the CLI from your machine. Each is its own step. Your own
account on the platform is a fourth; see [Projects and deployments](../concepts/projects-and-deployments.md#members-and-roles).

| To | Run or do |
|---|---|
| Uninstall, keeping data and key | `meridian down` |
| Uninstall and delete everything in the namespace | `meridian down --delete-namespace` |
| Take the deployment out of service | **Retire** it on the platform |
| Stop one plugin | `meridian plugin stop <instance>` |
| Revoke the CLI's delegation at a deployment | `meridian sign-out` |
| Remove the CLI | `meridian uninstall` |

## To uninstall, keeping the data

```bash
meridian down
```

This removes the deployment from the cluster. It keeps the `meridian` namespace, and with it:

- the disk of the database the deployment brought, if it brought one, and
- the deployment's own key.

Running `meridian up` again picks both back up, with the data. Nothing is asked: running the
command is the decision.

## To uninstall and delete everything

```bash
meridian down --delete-namespace
```

!!! danger
    This deletes the namespace. If the deployment brought its own database, all its data goes, and
    nothing backs it up. The deployment's private key goes too. It lived only in that cluster, and
    there is no copy anywhere. `meridian down` never touches the cluster itself.

A delegation this machine held at the deployment is forgotten either way.

## To install again after deleting the namespace

The platform still holds the public half of the old key, so the deployment is not offered a new
enrolment code. That is deliberate: a code that still worked for an enrolled deployment would be a
second way to register a key for it.

Choose one:

=== "Keep the identifier (usual)"

    1. On the platform, open the deployment. Its key is listed with its fingerprint.
    2. Choose **Revoke** beside the key and confirm with **Revoke key**.
    3. Once it holds no key, open its menu and choose **Issue enrolment code**.
    4. Install again from step 5 of [Install a deployment](../getting-started/installation.md), with the
       same `DEP-` identifier.

    Keeping the identifier matters: every assertion the deployment ever signed is about it.

=== "Register a new deployment"

    1. On the platform, choose **Register deployment** and start from step 3 of
       [Install a deployment](../getting-started/installation.md).
    2. **Retire** the old deployment, so it stops appearing in the list.

    Simplest when you are only experimenting.

## To retire a deployment

Uninstalling leaves the platform still believing the deployment exists. Retiring is what revokes its
keys and stops its codes working.

1. On the platform, open **Deployments** and the deployment's menu.
2. Choose **Retire** and confirm.

All its keys are revoked and it stops connecting. Its history is kept. Retired deployments are
hidden from the list unless you choose **Show retired**.

To bring it back, choose **Return to service** in its menu. It needs a new key before it connects
again. Codes are refused while it is retired.

## To remove the CLI

```bash
meridian uninstall
```

It revokes every delegation it holds, at each deployment it can reach, and removes itself. It asks
first; `--yes` answers for a script. Not to be confused with `meridian down`, which removes a deployment.

## What to back up

- **A database you run:** back it up as you back up any other.
- **A database the deployment brought:** nothing backs it up. That is fine for a trial and wrong for
  anything you depend on.

## Related

- [Projects and deployments](../concepts/projects-and-deployments.md)
- [Troubleshoot an install](troubleshoot-install.md)
