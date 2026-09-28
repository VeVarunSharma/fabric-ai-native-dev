# Fabric development with 10% or less Git overhead

This demo shows how Microsoft Fabric developers can spend most of their time on
pipelines, notebooks, reports, lakehouses, warehouses, and other Fabric items—not
on GitHub workflow maintenance.

The default path mirrors a team with two persistent workspaces:

```text
<PROJECT>_NonProd (Fabric Git -> develop)
                 |
                 | Copilot-assisted release PR
                 v
               main
                 |
                 | GitHub Actions + fabric-cicd
                 v
<PROJECT>_Prod (automation-owned)
```

Copilot helps developers understand and prepare changes. Tested scripts and GitHub
Actions perform the repeatable validation and deployment work.

## Start here in five minutes

### 1. Make the Fabric change

Work in `<PROJECT>_NonProd`, which is connected to `develop`, and commit the
supported Fabric item changes to Git.

For routine Fabric authoring, developers do not need to create and manage another
workspace or branch. Use a feature branch when an isolated branch workspace already
exists or when changing repository-only code such as scripts and workflows.

### 2. Ask Copilot to prepare the review

```text
Review my current Fabric Git change using this repository's instructions. Identify
the Fabric item types, show any Copy Job mappings that were added or removed, call
out Variable Library or OneLake security follow-up, and draft the release PR from
develop to main.
```

Copilot reads [the repository instructions](.github/copilot-instructions.md) so the
developer does not need to paste a large context block every time.

### 3. Open the release pull request

Use [the pull request template](.github/pull_request_template.md). The required
check runs tests and verifies the Fabric-specific declarations.

The template guides the author; the
[validation workflow](.github/workflows/validate-pr.yml) enforces the policy.

### 4. Merge after review

A merge to `main` starts the
[production deployment](.github/workflows/deploy-prod.yml). The workflow:

1. authenticates with the production service principal;
2. deploys reviewed item definitions with `fabric-cicd`;
3. selects and verifies the production Variable Library value set;
4. serializes deployments so two production writes cannot overlap.

The developer does not edit the workflow, handle an access token, or manually
switch the production value set.

## Try the demo without a Fabric tenant

Install the local validation tools:

```shell
python -m pip install -e ".[dev]"
```

The deployment library supports Python 3.11 through 3.13. The fixture-only tools and
tests can run independently of Fabric credentials.

Show a Copy Job mapping removal:

```shell
python scripts/validate_copy_job_diff.py \
  tests/fixtures/copy_job_before.json \
  tests/fixtures/copy_job_after.json
```

Diagnose independent changes on both sides:

```shell
python scripts/diagnose_git_sync.py \
  --status-file tests/fixtures/git_status_mixed.json
```

Show a genuine same-item conflict:

```shell
python scripts/diagnose_git_sync.py \
  --status-file tests/fixtures/git_status_conflict.json
```

Run all local checks:

```shell
python -m pytest
python -m ruff check scripts tests
python -m mypy scripts tests
python scripts/validate_repo_policy.py --all
```

## What is automated

| Developer need | Copilot assists with | Repository automation does |
|---|---|---|
| Understand a Fabric Git diff | Summarizes changed items and drafts the PR | Detects item folders and required declarations |
| Review a Copy Job | Explains mapping impact | Reports added and removed tables explicitly |
| Resolve a sync problem | Explains the status in plain language | Classifies independent changes versus genuine conflicts |
| Promote environment values | Identifies definition versus workspace state | Selects and verifies the target active value set |
| Deploy to production | Explains failures and reviews changes | Deploys `main` through the protected production environment |
| Apply DevOps policy | Gives the smallest corrective action | Runs required tests, ownership, and policy checks |

## Production configuration

The `production` GitHub Environment supplies the following non-secret variables:

| Variable | Example purpose |
|---|---|
| `FABRIC_TENANT_ID` | Entra tenant containing the service principal |
| `FABRIC_CLIENT_ID` | Service principal application/client ID |
| `FABRIC_WORKSPACE_ID` | Target Prod workspace |
| `FABRIC_REPOSITORY_DIRECTORY` | Repository folder containing Fabric item definitions |
| `FABRIC_ENVIRONMENT` | Deployment environment, normally the exact value-set name |
| `FABRIC_VARIABLE_LIBRARY_NAME` | Optional Variable Library to verify after deployment |
| `FABRIC_ACTIVE_VALUE_SET` | Optional value set that must be active in Prod |

The environment contains one secret: `FABRIC_CLIENT_SECRET`.

The two Variable Library variables can remain unset until the repository contains a
Variable Library. When both are configured, the workflow selects and verifies the
target value set after deployment.

The client secret is never committed or printed. See
[deployment authentication](docs/authentication.md) for setup, rotation, and the
managed identity alternative.

## Repository map

- [`docs/prompt-pack.md`](docs/prompt-pack.md): copyable Fabric developer prompts.
- [`docs/known-issues.md`](docs/known-issues.md): evidence-classified limitations
  and escalation guidance.
- [`docs/demo-guide.md`](docs/demo-guide.md): a reliable customer walkthrough.
- [`scripts/diagnose_git_sync.py`](scripts/diagnose_git_sync.py): read-only sync
  diagnosis from a live workspace or fixture.
- [`scripts/validate_copy_job_diff.py`](scripts/validate_copy_job_diff.py): explicit
  mapping additions and removals.
- [`scripts/deploy_fabric.py`](scripts/deploy_fabric.py): small `fabric-cicd` wrapper.
- [`scripts/set_active_value_set.py`](scripts/set_active_value_set.py): post-deploy
  Variable Library state selection and verification.

## Success scorecard

The demo meets the customer goal when:

- a routine developer uses Fabric, one Copilot request, and one release PR;
- developers do not edit deployment YAML or handle deployment credentials;
- risky Copy Job removals and Lakehouse security follow-up are visible in review;
- sync failures produce a safe next action instead of requiring Git internals;
- production is changed only by reviewed automation;
- platform limitations are identified rather than hidden by unreliable workarounds.

## Boundaries

This repository does not provision Entra identities, GitHub repository rulesets, or
Fabric tenant settings. It does not automatically choose a winner for destructive
Git conflicts. Customer-specific observations remain labeled as such until they are
reproduced or documented.
