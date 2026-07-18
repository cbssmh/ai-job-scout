# Phase 1 Task 4: Azure deployment

## Deployment flow

A push to `main`, or a manual `workflow_dispatch`, starts
`.github/workflows/deploy.yml`. The workflow runs the Python tests and validates
the Compose configuration before it authenticates to Azure, builds a
`linux/amd64` image, pushes the image to Azure Container Registry (ACR), updates
Azure Container Apps, waits for the deployed revision, and checks the public
HTTPS health endpoint.

Deployments share the `deploy-production` concurrency group. A deployment that
is already running is allowed to finish; subsequent runs wait rather than
overlap it.

## OIDC trust model

GitHub Actions requests a short-lived OIDC token for the exact subject:

```text
repo:cbssmh/ai-job-scout:ref:refs/heads/main
```

An Entra application federated credential trusts that subject and the GitHub
token issuer. `azure/login@v2` exchanges the GitHub token for a short-lived Azure
token. There is no client secret, ACR admin credential, publish profile, or other
long-lived Azure credential.

The manual trigger is safe because a workflow run from the repository's `main`
branch has the same ref subject. Runs from another ref are not trusted by this
federated credential.

## Required GitHub settings

Add these repository Actions variables or secrets under **Settings > Secrets
and variables > Actions**:

- `AZURE_CLIENT_ID`: application (client) ID printed by the bootstrap script
- `AZURE_TENANT_ID`: `26080271-1d99-47dd-a23f-502db6ef9f34`
- `AZURE_SUBSCRIPTION_ID`: `d05a26b7-4017-48f1-a956-d9f919361d10`

The workflow accepts either variables or secrets and gives secrets precedence.
These values are identifiers, not credentials. No GitHub-stored password or
client secret is required. Repository Actions must be permitted to request an
OIDC token; the workflow declares `id-token: write` and `contents: read`.

## Azure bootstrap

From the repository root, authenticate interactively, select the expected
subscription, and run:

```bash
az login --tenant 26080271-1d99-47dd-a23f-502db6ef9f34
az account set --subscription d05a26b7-4017-48f1-a956-d9f919361d10
./scripts/bootstrap_github_oidc.sh
```

The idempotent script creates or reuses:

- the `ai-job-scout-gha` Entra application;
- its service principal;
- the `github-main` federated credential; and
- the required role assignments.

It prints the three GitHub configuration values at the end but does not save
them or create a client secret.

## Azure roles and scopes

The service principal receives the minimum practical data-plane/deployment
access:

| Role | Scope | Purpose |
| --- | --- | --- |
| `AcrPush` | `/subscriptions/d05a26b7-4017-48f1-a956-d9f919361d10/resourceGroups/rg-ai-jobscout-dev/providers/Microsoft.ContainerRegistry/registries/aijobscoutms2026` | Authenticate Docker and push images to this ACR only |
| `Container Apps Contributor` | `/subscriptions/d05a26b7-4017-48f1-a956-d9f919361d10/resourceGroups/rg-ai-jobscout-dev` | Update and inspect the Container App and its revisions within this resource group |

The deployment identity is not assigned subscription-wide `Contributor` or
`Owner`. The Container App's existing registry-pull configuration remains
responsible for pulling the deployed image.

## Workflow and image tags

The immutable deployment image is:

```text
aijobscoutms2026.azurecr.io/ai-job-scout:<full-git-commit-sha>
```

The same build is also published as the mutable convenience tag `main`, but the
Container App is always updated to the full SHA tag. Buildx explicitly targets
`linux/amd64`. The update clears command and args overrides so the image's
exec-form Docker `CMD` remains authoritative; it does not add Azure-specific
startup behavior.

The workflow polls the selected revision for both `Healthy` and `Running`, with
a five-minute limit. It then retries the HTTPS health request 12 times using
connection and request timeouts. Any test, build, push, deployment, revision, or
health-check failure fails the run. The Actions step summary records the commit,
image, revision, endpoint, and health result.

## Verification

After a successful run:

1. Open the run summary and confirm the image uses the expected commit SHA.
2. Confirm the named revision is `Healthy` and `Running`:

   ```bash
   az containerapp revision show \
     --name ca-ai-jobscout-dev \
     --resource-group rg-ai-jobscout-dev \
     --revision <revision-name> \
     --query '{health:properties.healthState,running:properties.runningState}'
   ```

3. Confirm the public endpoint returns a successful response:

   ```bash
   curl --fail --show-error \
     https://ca-ai-jobscout-dev.kindbay-14c42b35.eastasia.azurecontainerapps.io/health
   ```

## Rollback

Choose a previously successful full SHA from ACR or a prior workflow summary,
then update the app to that immutable image while keeping startup overrides
cleared:

```bash
az containerapp update \
  --name ca-ai-jobscout-dev \
  --resource-group rg-ai-jobscout-dev \
  --container-name ca-ai-jobscout-dev \
  --image aijobscoutms2026.azurecr.io/ai-job-scout:<known-good-sha> \
  --command "" \
  --args ""
```

Wait for the resulting revision to become `Healthy` and `Running`, then repeat
the HTTPS health check. Do not roll back by moving the `main` tag because it is
mutable.

## Conditional Access and MFA

The interactive Azure CLI session may be blocked from Entra or Azure write
operations by the tenant's Conditional Access MFA policy. If that happens,
complete the required MFA challenge and rerun the script, or ask an authorized
administrator to perform the same application, federated-credential, and role
assignment operations in the Azure Portal. Do not bypass the policy or fall back
to a client secret. The bootstrap script stops on the failed command and reports
it; partial creation is safe because reruns reuse existing resources.

## Application scope

This deployment work changes no business logic, API behavior, UI, AI behavior,
or database design. Docker Compose remains supported, and the workflow does not
modify application source code.
