$csName = $args[0]
if (-not $csName) { Write-Error 'Missing codespace name'; exit 2 }
 $remoteCmd = 'bash -lc "pytest -q -k \"not slow and not e2e and not integration\" 2>&1 | sed -n ""' + "$p" + '"""'
 Write-Output ('Running on {0}: {1}' -f $csName, $remoteCmd)
 & gh codespace ssh -c $csName -- $remoteCmd
