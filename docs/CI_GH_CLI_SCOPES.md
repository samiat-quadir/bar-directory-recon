# CI GitHub CLI Scopes

* **Current CI token**: workflow/contents read, metadata/PR writes
* **Common issues**: 401 on private repos, 403 on admin actions
* **Fixes**: check GITHUB_TOKEN perms, use gh auth status
* **Examples**: `gh auth status`, `gh api user` (test API connectivity)
