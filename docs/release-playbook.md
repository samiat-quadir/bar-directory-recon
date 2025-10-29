# Release Playbook (v0.1.x)

## Preconditions
- All **six required checks** green on `main`: audit, fast-tests (ubuntu-latest), fast-tests (windows-latest), workflow-guard, ps-lint (ubuntu-latest), ps-lint (windows-latest).
- Draft notes exist (e.g., `RELEASE_NOTES_v0.1.0.md`), artifacts build locally.

## Steps
1. **Pack sanity**: `gh workflow run cli-pack --ref <tag>` → wait → compare SHA256 to release assets.
2. **Publish** the draft Release (if not already).
3. **Attach artifacts** (if not attached) or confirm parity; use cli-pack on `release: published`.
4. **Bump dev**: `__version__ = X.Y.Z.dev0`, add CHANGELOG `[Unreleased]`.
5. **Sanity**: run `scripts/release_sanity.ps1`; post the SUMMARY line in the PR.
6. **Announce**: link Release + wheel/sdist; include install snippet.

## Rollback
- Required checks live in branch protection; ps-lint rollback: `scripts/pslint_promotion_rollback.ps1`.