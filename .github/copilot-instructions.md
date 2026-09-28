# Copilot instructions: Microsoft Fabric CI/CD

## Repository purpose

This repository demonstrates a lightweight Fabric development workflow for data
scientists and data engineers with limited DevOps capacity. Optimize suggestions
for the goal that developers spend 10% or less of their time managing GitHub.

Prefer a concrete command, diff, script, or checklist over a long explanation.
Explain the reason in one sentence, then give the exact action.

## Environments and source control

- `<PROJECT>_NonProd` is the authoring workspace connected to `develop`.
- Routine Fabric changes commit from NonProd to `develop`; the review boundary is
  the release pull request from `develop` to `main`.
- Use `feat/<item-type>-<description>`, `fix/<item-type>-<description>`, or
  `chore/<description>` only when an isolated branch workspace exists or for
  repository-only changes.
- Reviewed releases merge from `develop` to `main`.
- `<PROJECT>_Prod` is automation-owned and deployed from `main`.
- Never suggest direct edits in Prod or direct commits to `main`.
- Fabric-generated item folder names and `.platform` files must not be renamed by hand.

## Fabric-specific review rules

- Never hard-code environment-specific runtime values in item definitions.
  Use a Fabric Variable Library.
- Treat Variable Library definitions and the active value set as separate concerns.
  Definitions are deployed from Git; the target workspace selects its active value
  set after deployment.
- For every Copy Job change, identify added and removed source-to-destination table
  mappings. Do not assume a missing table removal was promoted correctly.
- OneLake security roles, RLS, CLS, and OLS are separate deployment controls. When
  a Lakehouse changes, state whether a security update or manual verification is
  required.
- A genuine Fabric Git conflict means the same item changed in the workspace and
  remote Git. Do not call independent changes on different items a conflict.
- Never recommend `PreferRemote`, `PreferWorkspace`, or another overwriting action
  without stating which changes will be discarded.
- Fabric Git operations can be asynchronous. Use the current `workspaceHead`, poll
  long-running operations, and serialize operations against a workspace.

## Authentication and secrets

- The implemented deployment path uses a service principal with its client secret
  stored in a protected GitHub Environment secret.
- Tenant IDs, client IDs, and workspace identifiers are configuration, not secrets,
  but they must still be represented with placeholders in committed examples.
- Managed identity may be described only as an alternative for an Azure-hosted
  runner.
- Never commit or print a client secret, token, connection string, account key, or
  workspace credential.

## Guidance versus enforcement

- Copilot instructions guide generated work.
- The pull request template collects Fabric-specific context.
- GitHub Actions, required checks, CODEOWNERS, and repository rulesets enforce policy.
- Do not claim that a prompt or checklist enforces a rule.

## Platform limitations

When behavior is not captured by Fabric Git or deployment APIs, say so plainly.
Classify it as documented, customer-observed, or requiring reproduction. Do not
invent a workaround that appears successful but cannot persist the missing state.
