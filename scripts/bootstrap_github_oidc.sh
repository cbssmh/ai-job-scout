#!/usr/bin/env bash
set -euo pipefail

EXPECTED_SUBSCRIPTION_ID="d05a26b7-4017-48f1-a956-d9f919361d10"
EXPECTED_TENANT_ID="26080271-1d99-47dd-a23f-502db6ef9f34"
RESOURCE_GROUP="rg-ai-jobscout-dev"
ACR_NAME="aijobscoutms2026"
APP_DISPLAY_NAME="ai-job-scout-gha"
FEDERATED_CREDENTIAL_NAME="github-main"
GITHUB_SUBJECT="repo:cbssmh/ai-job-scout:ref:refs/heads/main"

failed_command=""
on_error() {
  local exit_code="${1:-$?}"
  printf '\nBootstrap stopped. Command failed (exit %d): %s\n' \
    "$exit_code" "${failed_command:-$BASH_COMMAND}" >&2
  cat >&2 <<'MESSAGE'
If Azure reports Conditional Access or MFA, authenticate with `az login`, complete
the required MFA challenge (or have an authorized administrator perform the
operation in the Azure Portal), then rerun this script. Do not create a client
secret or weaken the tenant policy.
MESSAGE
  exit "$exit_code"
}
trap on_error ERR

run() {
  local exit_code
  failed_command="$(printf '%q ' "$@")"
  if "$@"; then
    failed_command=""
  else
    exit_code=$?
    on_error "$exit_code"
  fi
}

command -v az >/dev/null 2>&1 || {
  echo "Azure CLI (az) is required." >&2
  exit 1
}

current_subscription_id="$(run az account show --query id --output tsv)"
current_tenant_id="$(run az account show --query tenantId --output tsv)"

if [[ "$current_subscription_id" != "$EXPECTED_SUBSCRIPTION_ID" ]]; then
  printf 'Expected active subscription %s, but found %s.\n' \
    "$EXPECTED_SUBSCRIPTION_ID" "$current_subscription_id" >&2
  printf 'Run: az account set --subscription %q\n' "$EXPECTED_SUBSCRIPTION_ID" >&2
  exit 1
fi

if [[ "$current_tenant_id" != "$EXPECTED_TENANT_ID" ]]; then
  printf 'Expected tenant %s, but found %s.\n' \
    "$EXPECTED_TENANT_ID" "$current_tenant_id" >&2
  exit 1
fi

subscription_scope="/subscriptions/$EXPECTED_SUBSCRIPTION_ID"
resource_group_scope="$subscription_scope/resourceGroups/$RESOURCE_GROUP"
acr_scope="$resource_group_scope/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME"

app_id="$(run az ad app list \
  --display-name "$APP_DISPLAY_NAME" \
  --query '[0].appId' \
  --output tsv)"

if [[ -z "$app_id" ]]; then
  echo "Creating Entra application: $APP_DISPLAY_NAME"
  app_id="$(run az ad app create \
    --display-name "$APP_DISPLAY_NAME" \
    --query appId \
    --output tsv)"
else
  echo "Reusing Entra application: $APP_DISPLAY_NAME"
fi

app_object_id="$(run az ad app show --id "$app_id" --query id --output tsv)"
sp_object_id="$(az ad sp show --id "$app_id" --query id --output tsv 2>/dev/null || true)"

if [[ -z "$sp_object_id" ]]; then
  echo "Creating service principal for: $APP_DISPLAY_NAME"
  run az ad sp create --id "$app_id" --output none
  for _ in {1..12}; do
    sp_object_id="$(az ad sp show --id "$app_id" --query id --output tsv 2>/dev/null || true)"
    [[ -n "$sp_object_id" ]] && break
    sleep 5
  done
  if [[ -z "$sp_object_id" ]]; then
    echo "Service principal was created but did not become readable within 60 seconds." >&2
    exit 1
  fi
else
  echo "Reusing service principal for: $APP_DISPLAY_NAME"
fi

credential_id="$(run az ad app federated-credential list \
  --id "$app_object_id" \
  --query "[?subject=='$GITHUB_SUBJECT' && issuer=='https://token.actions.githubusercontent.com'].id | [0]" \
  --output tsv)"

if [[ -z "$credential_id" ]]; then
  echo "Creating GitHub federated credential: $FEDERATED_CREDENTIAL_NAME"
  credential_file="$(mktemp)"
  trap 'rm -f "$credential_file"' EXIT
  printf '%s\n' "{
    \"name\": \"$FEDERATED_CREDENTIAL_NAME\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"$GITHUB_SUBJECT\",
    \"description\": \"GitHub Actions main branch deployment\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }" > "$credential_file"
  run az ad app federated-credential create \
    --id "$app_object_id" \
    --parameters "$credential_file" \
    --output none
else
  echo "Reusing GitHub federated credential: $FEDERATED_CREDENTIAL_NAME"
fi

ensure_role_assignment() {
  local role="$1"
  local scope="$2"
  local assignment_count
  assignment_count="$(run az role assignment list \
    --assignee-object-id "$sp_object_id" \
    --scope "$scope" \
    --query "[?roleDefinitionName=='$role'] | length(@)" \
    --output tsv)"
  if [[ "$assignment_count" == "0" ]]; then
    echo "Assigning $role at $scope"
    run az role assignment create \
      --assignee-object-id "$sp_object_id" \
      --assignee-principal-type ServicePrincipal \
      --role "$role" \
      --scope "$scope" \
      --output none
  else
    echo "Reusing $role assignment at $scope"
  fi
}

ensure_role_assignment "AcrPush" "$acr_scope"
ensure_role_assignment "Container Apps Contributor" "$resource_group_scope"

cat <<VALUES

Bootstrap complete. Add these values as GitHub Actions secrets or variables:
AZURE_CLIENT_ID=$app_id
AZURE_TENANT_ID=$EXPECTED_TENANT_ID
AZURE_SUBSCRIPTION_ID=$EXPECTED_SUBSCRIPTION_ID

No client secret was created. These identifiers are printed only and were not
saved by this script.
VALUES
