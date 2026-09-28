# Fabric developer prompt pack

These prompts are intentionally short. The repository instructions supply the
Fabric-specific context, so developers do not need to paste a large context block
into every conversation.

## Git-based Fabric workflows

```text
Review my current Git diff as a Fabric change. Identify the Fabric item types,
summarize the developer impact, and draft the pull request using this repository's
template. Explicitly list Copy Job mappings that were added or removed.
```

Good output: a concise Fabric-aware summary with the PR fields completed from the
actual diff rather than guessed.

```text
I have an isolated branch workspace for <Fabric item>. Give me the correct branch
name from develop, the smallest safe Git command sequence, and the PR target.
Explain each step in no more than one sentence.
```

Good output: a `feat/`, `fix/`, or `chore/` branch without implying that routine
two-workspace Fabric authors must create another workspace for every edit.

## Troubleshooting Fabric and Git synchronization

```text
Run the repository's Fabric Git diagnostic against this status response. Separate
workspace-only, remote-only, same-change, and genuine same-item conflicts. Do not
overwrite either side. Tell me the safest next action.
```

Good output: different-item changes are not mislabeled as conflicts, and destructive
choices are surfaced rather than executed.

```text
Fabric says my workspace is out of sync after an update. Check for an asynchronous
operation, stale workspaceHead, residual changes, and formatting-only diffs. Give me
the checks in the order I should run them.
```

Good output: bounded long-running-operation polling followed by verification that
the workspace and remote heads match and the changes list is empty.

## Updating Variable Libraries across environments

```text
Review this Variable Library change. Separate definition changes stored in Git from
the active value set stored in the target workspace. Tell me what deploys and what
must run after deployment.
```

Good output: Git-managed variables/value-set files are distinguished from the
post-deployment `activeValueSetName` operation.

```text
Prepare the command to select the prod value set with
scripts/set_active_value_set.py. Use GitHub Environment variables for deployment
metadata and do not place runtime application values in GitHub.
```

Good output: a command using placeholders or environment variables, followed by a
read-back verification.

## Deployment authentication: service principal and managed identity

```text
Review the production workflow's service-principal authentication. Confirm that the
client secret comes only from the protected GitHub Environment, no token is printed,
and non-secret identifiers are stored as environment variables.
```

Good output: a least-surprise review of the implemented client-secret path, including
the rotation burden.

```text
Explain how this deployment would change if the GitHub runner moved to an
Azure-hosted runner with managed identity. Do not change the current implementation.
List only the authentication and permission differences.
```

Good output: managed identity is treated as an Azure-hosted runner alternative, not
as a feature of the current GitHub-hosted runner.

## Code review, security checks, and DevOps enforcement

```text
Review this pull request for Fabric deployment risk. Check for secrets, hard-coded
environment values, direct Prod changes, missing Copy Job removals, Variable Library
activation needs, and OneLake security follow-up. Report only actionable findings.
```

Good output: findings map to repository policy and distinguish guidance from checks
that are actually enforced.

```text
Explain why this pull request is blocked by validate-pr.yml and give the smallest
change that satisfies the policy without weakening the check.
```

Good output: a direct correction to the PR description or code rather than a request
to bypass required checks.
