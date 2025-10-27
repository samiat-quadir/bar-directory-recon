# v0.1.0 (draft)

**Why this matters:** CI is now quiet and deterministic (guard required; allowed workflows strict). A packaged CLI (dr) provides a demo five-stage flow with adapters and safe fallbacks. Security noise is reduced (lockfile flow, CodeQL fixture ignores, secret-scanning allowlist).

> This is a **documentation-only** PR; no code or CI policy changes.

## What changed (highlights)
- Required checks stabilized (fast-ubuntu, fast-windows, audit, workflow-guard)
- Guard verifier + allow-list/early-exit assertions
- ps-lint burn-in + promotion kit (pending Oct 23 window)
- CLI: demo pipeline, adapters, --version, doctor
- Security: constraints/lock, audit targeting, secret-scanning allowlist, CodeQL paths-ignore
### CI & Guard
* #256 - chore(ci): insights polish (guard drift) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/256))
* #257 - chore(ci): ps-lint readiness telemetry (no policy change) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/257))
* #258 - ci(dependabot): workflow-only automerge safeguard ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/258))
* #263 - feat(cli): demo pipeline + manual CI ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/263))
* #266 - ci(ps-lint): always-run (remove paths filter) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/266))
* #267 - ci(guard): assert ps-lint is always-run ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/267))
* #268 - fix(guard): clean up merge conflict in guard script ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/268))
* #269 - ci(hygiene): schedule-only + rename ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/269))
* #270 - ci(ps-lint): early-exit + guard assertions ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/270))
* #271 - fix(guard): add ci-hygiene-weekly to allow list ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/271))
* #272 - chore: ps-lint sanity (README-only) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/272))
* #277 - ci(status-bot): PR comment from allowed jobs ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/277))
* #278 - ci(ps-lint): promotion kit (preview/decide) – no policy change ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/278))
* #279 - ci/guard: assert ps-lint early-exit + reminder + runbook ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/279))
* #282 - ci(ps-lint): add rollback script for promotion kit ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/282))
* #283 - ci(ps-lint): add scheduler for automated Oct 23 promotion decision ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/283))
* #285 - sec: quiet Security Center (allowlist + scrub) & CodeQL config; workflow permissions ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/285))

### CLI & Demo
* #259 - docs+cli: project vision/architecture/roadmap + CLI stub ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/259))
* #263 - feat(cli): demo pipeline + manual CI ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/263))
* #264 - chore(cli): package console entry + pre-commit (ruff-only) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/264))
* #273 - feat(cli): adapters wiring + Quickstart (safe fallbacks) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/273))
* #280 - chore(cli): --version + doctor (no deps) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/280))

### Security & Supply Chain
* #258 - ci(dependabot): workflow-only automerge safeguard ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/258))
* #285 - sec: quiet Security Center (allowlist + scrub) & CodeQL config; workflow permissions ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/285))

### Docs & Misc
* #259 - docs+cli: project vision/architecture/roadmap + CLI stub ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/259))
* #260 - chore: LICENSE + docs index + weekly branch-hygiene report ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/260))
* #272 - chore: ps-lint sanity (README-only) ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/272))
* #284 - docs: badges + issue templates ([link](https://github.com/samiat-quadir/bar-directory-recon/pull/284))

## Upgrade notes
- No behavioral changes for end-users in this draft.
- After the Oct 23 decision, ps-lint may become required (ubuntu & windows). Rollback instructions live in **docs/PROMOTION_RUNBOOK.md**.

## Contributors
Thanks to everyone who pushed PRs in this window.