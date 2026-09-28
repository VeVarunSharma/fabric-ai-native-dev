# Customer demo guide

## Message to land

The developer should spend time on Fabric items, not Git mechanics. Copilot supplies
Fabric-aware guidance, while repository automation performs repeatable checks and
deployment work.

## Before the call

1. Keep the repository prebuilt; do not scaffold seven files live.
2. Confirm the fixture commands in the README run locally.
3. Configure no customer identifiers in the demo repository.
4. If showing a real deployment, configure the protected `production` GitHub
   Environment separately and confirm the service principal secret is current.
5. Recheck the preview and known-issue links in `docs/known-issues.md`.

## Walkthrough

### 1. Show the five-minute path

Open the README and explain the developer's normal loop: change a Fabric item, ask
Copilot to prepare the review, open a PR, and let required checks handle the rest.

### 2. Demonstrate Fabric-aware review

Use `tests/fixtures/copy_job_before.json` and `copy_job_after.json`, then ask Copilot:

```text
Review this Copy Job change using the repository instructions. Tell me what the PR
must say and what risk the reviewer should check.
```

Run:

```shell
python scripts/validate_copy_job_diff.py \
  tests/fixtures/copy_job_before.json \
  tests/fixtures/copy_job_after.json
```

The important result is that the removed mapping is visible rather than hidden in a
large JSON diff.

### 3. Demonstrate safe sync diagnosis

Run:

```shell
python scripts/diagnose_git_sync.py \
  --status-file tests/fixtures/git_status_mixed.json
```

Then run the conflict fixture. Emphasize that independent changes are not called a
conflict, while a same-item conflict stops for a human decision.

### 4. Explain deployment rather than creating credentials

Open `.github/workflows/deploy-prod.yml`. Point out:

- `main` is the only production source.
- the protected environment holds the client secret;
- the workflow calls tested scripts rather than embedding deployment logic;
- the Variable Library active value set is verified after deployment;
- deployment concurrency prevents overlapping production writes.

Do not create an Entra application or secret during the customer call.

### 5. Show enforcement

Open the PR template and `validate-pr.yml`. Explain the boundary:

- Copilot drafts and reviews;
- the template gathers Fabric context;
- Actions and repository rules block incomplete changes.

### 6. Close on the customer goal

The developer's recurring actions should be limited to the Fabric change, one
Copilot request, and responding to review feedback. Authentication, table-diff
checks, policy checks, deployment, and value-set activation are platform-owned.

## Copilot surface note

Use `/skills list` only when demonstrating Copilot CLI. In other Copilot surfaces,
show the repository instructions through the interface supported by that product
instead of promising the same slash command.
