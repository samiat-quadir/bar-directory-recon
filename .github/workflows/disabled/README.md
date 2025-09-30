# Disabled workflows

This directory preserves original workflow files that were quieted to prevent automatic runs on pull request events.

Files were moved here and replaced by minimal manual-only stubs in the repository root (.github/workflows) so that:

- The original workflow contents are preserved for auditing and possible restoration.
- The active workflow files only run when triggered manually (workflow_dispatch) to quiet CI noise during large refactors.

If you want to restore any workflow, move it back to .github/workflows/ and ensure it is valid YAML.
