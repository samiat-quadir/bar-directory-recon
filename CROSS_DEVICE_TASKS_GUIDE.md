# Cross-Device Task Runner Guide

This guide explains the improved `run_cross_device_task.py` utility and the YAML-driven tasks in `automation/cross_device_tasks.yaml`.

## Usage

List all tasks:

```bash
python run_cross_device_task.py --list
```

Run a task:

```bash
python run_cross_device_task.py run_tests_on_alienware
```

Dry-run (show command only):

```bash
python run_cross_device_task.py run_tests_on_asus --dry-run
```

Retry an SSH task with verbose diagnostics on failure:

```bash
python run_cross_device_task.py run_tests_on_asus --retry-verbose
```

## Key Features

- Enforces `IdentitiesOnly=yes` for `ssh`/`scp` to constrain key usage.
- Verbose retry (`--retry-verbose`) for SSH diagnostics.
- Dry-run mode to preview commands.
- Additional tasks for verifying remote Python executables.
- Central YAML for easy task extension.


## Current Tasks

| Task | Purpose |
|------|---------|
| run_tests_on_asus | Run pytest in the remote ASUS venv |
| run_tests_on_alienware | Run pytest in the remote Alienware venv |
| verify_python_on_asus | Show Python paths & versions remotely (ASUS) |
| verify_python_on_alienware | Show Python paths & versions remotely (Alienware) |
| echo_local_time_asus | Quick connectivity/time sanity check (ASUS) |
| echo_local_time_alienware | Quick connectivity/time sanity check (Alienware) |

## Troubleshooting SSH Auth (Permission denied (publickey))

1. Ensure the *public* key corresponding to `~/.ssh/id_ed25519_clear` is present in the remote user's `~/.ssh/authorized_keys` **as a single line**.

1. Permissions (Linux / WSL / *nix remote):

`chmod 700 ~/.ssh`

`chmod 600 ~/.ssh/authorized_keys`

1. Manually test:

```bash
ssh -o IdentitiesOnly=yes rog-lucci "echo ok"
```

1. If failing, add `--retry-verbose` to gather negotiation logs and look for lines like `Offering public key` / `Server accepts key`.

1. Verify the Tailscale IP/hostname matches the host alias in `~/.ssh/config`.

## Adding New Tasks

Edit `automation/cross_device_tasks.yaml` and add an entry:

```yaml
tasks:
  new_task_name:
    command: "ssh rog-lucci \"cmd /c ^\"your windows command here^\"\""
```
Then list tasks to confirm it loads correctly.


## Shell Integration Prompt

The workspace settings now explicitly define the Windows `Command Prompt` profile and disable the suggestion banner (`terminal.integrated.shellIntegration.suggestEnabled: false`). If the banner still appears, open a new terminal; if necessary reload VS Code. The integration itself remains enabled.

Generated automatically as part of cross‑device enhancement improvements.
