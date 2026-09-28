# Deployment authentication

The implemented path uses a Microsoft Entra service principal and a client secret.
It is deliberately simple for a GitHub-hosted runner.

## Implemented service-principal path

### Fabric and Entra prerequisites

1. Create or reuse an Entra application and its service principal.
2. Allow service principals to use the required Fabric APIs in tenant settings.
3. Add the service principal to the production workspace with the least role that
   supports the deployed item operations. Use a higher role only when an API
   explicitly requires it.
4. Create a time-bounded client secret and record its expiry in the team's normal
   credential-management process.

This repository does not provision these resources because identity and tenant
policy are organization-owned.

### GitHub Environment

Create a protected environment named `production`. Add approval rules appropriate
for the organization, then configure:

**Environment secret**

- `FABRIC_CLIENT_SECRET`

**Environment variables**

- `FABRIC_TENANT_ID`
- `FABRIC_CLIENT_ID`
- `FABRIC_WORKSPACE_ID`
- `FABRIC_REPOSITORY_DIRECTORY`
- `FABRIC_ENVIRONMENT`
- `FABRIC_VARIABLE_LIBRARY_NAME`
- `FABRIC_ACTIVE_VALUE_SET`

Tenant, client, and workspace IDs are identifiers rather than credentials. Keeping
them as variables makes configuration visible without exposing the client secret.

### Runtime behavior

`scripts/deploy_fabric.py` constructs `ClientSecretCredential` and passes it to the
required `token_credential` argument of `fabric_cicd.FabricWorkspace`. A subscription
ID and Azure CLI login are not required for this direct authentication path.

The workflow passes the secret only to the deployment and Variable Library steps.
It must never be echoed, written to a file, or included in a job summary.

## Secret rotation

1. Create a new client secret before the existing secret expires.
2. Replace `FABRIC_CLIENT_SECRET` in the protected GitHub Environment.
3. Run the production workflow manually against a reviewed commit.
4. Confirm deployment and Variable Library verification succeed.
5. Remove the previous secret from Entra.

This sequence avoids an outage and gives the platform team one verifiable rotation
point. Dependabot does not rotate identity secrets.

## Managed identity alternative

Managed identity is appropriate when the runner is hosted on an Azure resource that
owns or can access that identity. In that model:

- assign the managed identity the required Fabric workspace role;
- enable the applicable Fabric tenant settings;
- replace `ClientSecretCredential` with `ManagedIdentityCredential`;
- remove `FABRIC_CLIENT_SECRET`, `FABRIC_CLIENT_ID`, and secret rotation work;
- keep the same deployment and Variable Library operations.

Managed identity is documented but not implemented here because the demo uses a
GitHub-hosted runner. Moving to managed identity is a platform-runner decision, not a
change a Fabric developer should make per pull request.

## References

- [Fabric REST API identity support](https://learn.microsoft.com/rest/api/fabric/articles/identity-support)
- [`fabric-cicd` authentication](https://microsoft.github.io/fabric-cicd/1.3.0/example/authentication/)
- [`ClientSecretCredential`](https://learn.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential)
- [Managed identities for Azure resources](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
