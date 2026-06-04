# Ops Queue Notes

## Admin-only tasks

- infra_smoke.fail.json: requires elevated shell for EnsureSshd.ps1; treat as manual/admin-only check, not a required part of --validate.

## Manual queue items

- `manual/aliyah_run_tests_on_asus.json`: investigative ASUS test pass that lacks a `target` entry and still awaits a hardened automation entrypoint. Keep it in the `manual/` subfolder until a supported runner exists, and re-add only after defining `"target"` + args in a lightweight wrapper.
