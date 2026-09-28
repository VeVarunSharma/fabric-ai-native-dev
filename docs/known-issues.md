# Fabric Git and deployment issues

The classifications below prevent tenant-specific observations from being presented
as universal Fabric behavior. Recheck preview behavior before each customer demo.

## Copy Job table removal is not visible after promotion

**Classification:** Customer-observed; reproduce on the current Fabric build.

**What happens:** Added mappings and schedule changes appear, but a removed table can
remain in the promoted Copy Job.

**What this repository does:** `validate_copy_job_diff.py` compares mappings before
and after the change and makes removals explicit in the PR. This is a safety control,
not a claim that Copilot repairs Fabric serialization.

**Escalate when:** The removed mapping is absent from the committed item definition
but remains after a successful deployment, or the workspace export does not record
the removal.

**Reference:** [CI/CD for Copy Job](https://learn.microsoft.com/fabric/data-factory/cicd-copy-job)

## OneLake security changes are absent from the Git change

**Classification:** Customer-observed; verify the serialized Lakehouse parts and the
current supported-item documentation.

**What happens:** A Lakehouse change can be committed without an accompanying role,
RLS, CLS, or OLS definition in the Git diff.

**What this repository does:** Lakehouse PRs require an explicit statement that no
OneLake security change is needed or a linked security runbook. Copilot can identify
the missing control, but it cannot source-control state Fabric did not export.

**Escalate when:** The security configuration must be promoted repeatably but no
supported definition or API surface represents it.

**Reference:** [Create and manage OneLake security roles](https://learn.microsoft.com/fabric/onelake/security/create-manage-roles)

## Workspace and Git both contain changes

**Classification:** Documented Fabric Git behavior.

**What happens:** Independent changes on different items can exist on both sides.
A genuine conflict occurs when the same item changed in the workspace and remote Git.

**What this repository does:** `diagnose_git_sync.py` classifies each item and refuses
to perform an overwrite. Fabric Git operations must use the current `workspaceHead`,
handle HTTP 202 long-running operations, and run one at a time per workspace.

**Escalate when:** Status remains inconsistent after the operation succeeds and
`workspaceHead`, `remoteCommitHash`, and the residual changes have been re-read.

**Reference:** [Git Get Status REST API](https://learn.microsoft.com/rest/api/fabric/core/git/get-status)

## Service principal setup and secret rotation

**Classification:** Expected operational overhead.

**What happens:** The Entra application needs Fabric permissions, a workspace role,
tenant settings, and a client secret that must be rotated.

**What this repository does:** The client secret exists only as a protected GitHub
Environment secret. The workflow never prints it. Non-secret identifiers use GitHub
Environment variables. Managed identity is documented as an alternative only when
the runner is hosted on an Azure resource.

**Escalate when:** Tenant settings block service principals, the principal lacks the
workspace role required by the API, or organizational policy disallows stored client
secrets.

**Reference:** [Fabric REST API identity support](https://learn.microsoft.com/rest/api/fabric/articles/identity-support)

## Values are maintained in both GitHub and Fabric

**Classification:** Configuration-design issue.

**What happens:** Teams duplicate the same endpoint, connection, or feature value in
GitHub and the Fabric Variable Library.

**What this repository does:** GitHub stores only deployment metadata such as the
workspace, tenant, client, library name, and selected stage. Runtime application
values remain in the Fabric Variable Library. The workflow selects the target
workspace's active value set after deploying the definition.

**Escalate when:** An item type cannot consume a Variable Library value and still
requires environment-specific configuration.

**Reference:** [Variable Library lifecycle management](https://learn.microsoft.com/fabric/cicd/variable-library/variable-library-cicd)

## GitHub Actions need ongoing maintenance

**Classification:** Repository maintenance concern.

**What happens:** Large YAML workflows accumulate embedded shell code, stale action
versions, and duplicated deployment logic.

**What this repository does:** Workflows remain orchestration-only; tested Python
scripts own the logic. Dependabot tracks Python and GitHub Actions updates, while
CODEOWNERS requires platform review for workflow changes.

**Escalate when:** A workflow requires provider-specific or organization-wide logic
that belongs in a reusable workflow maintained by the platform team.

## Verification record

Last reviewed for the demo: 2026-09-28. Preview and supported-item behavior should be
checked against Microsoft Learn before an external presentation.
