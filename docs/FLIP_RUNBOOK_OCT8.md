## Oct-8 Flip Day Checklist (quick)
- Run: pwsh -NoProfile -File scripts\flip-morning-sanity.ps1 (artifacts under rtifacts/flip/morning/).
- Confirm the guard name in rtifacts/flip/morning/check_names.txt (expect 'workflow-guard').
- Run: pwsh -NoProfile -File scripts\flip-finalize-kit.ps1 (prints PUT + rollback).
- At EOD ET, execute the printed PUT command (or scripts\flip-guard-required.ps1 -Execute).
- Post-flip, run the two smoke scripts under scripts\afterflip-*.ps1; expect 4 required checks green on the code-touch PR.