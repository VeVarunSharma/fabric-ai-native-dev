# Fabric workspace definitions

Connect or export Fabric items into this directory. Fabric-generated folders such as
`MyNotebook.Notebook`, `LoadData.DataPipeline`, and
`EnvironmentConfig.VariableLibrary` should remain unchanged so `fabric-cicd` can
discover and deploy them.

This README is ignored by `fabric-cicd`.

## Quick notebook PR demo

`QuickCiDemo.Notebook` is a new, repository-authored Fabric notebook definition.
It uses five synthetic sales rows, rejects one negative amount, and checks that
the four valid rows total 260.00. It runs entirely in memory using standard
Python, with no lakehouse, credentials, or Variable Library required.

Run its check locally:

```shell
python -m pytest tests/test_quick_ci_notebook.py
```

Open a PR to see the existing **Validate Fabric pull request** workflow run policy,
tests (including the notebook), lint, and type checks. Routine Fabric changes still
come from NonProd on `develop`; this repository-authored sample is a quick CI demo.

After review, merging to `main` triggers **Deploy Fabric production**. Deployment
requires the protected `production` environment to be configured as described in
the root README, with `FABRIC_REPOSITORY_DIRECTORY` set to `workspace`. Deployment
publishes the notebook definition; it does not run the notebook. After deployment,
open `QuickCiDemo` in Fabric and select **Run all** to see `QuickCiDemo passed.`
No Copy Job mappings or OneLake security settings are changed.
