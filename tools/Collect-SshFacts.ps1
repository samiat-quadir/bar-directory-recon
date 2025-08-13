[CmdletBinding()]
param(
  [ValidateSet('server','client')] [string]$Role='server',
  [string]$TargetHost='',
  [string]$KeyPath=''
)
$report=@{}
$report.host=[Environment]::MachineName
$report.user=$env:USERNAME

if ($Role -eq 'server') {
  $cfg='C:\ProgramData\ssh\sshd_config'
  $ak='C:\ProgramData\ssh\administrators_authorized_keys'
  $report.sshd=@{
    exists=Test-Path $cfg
    AuthorizedKeysFile=(Select-String -Path $cfg -Pattern 'AuthorizedKeysFile' -SimpleMatch -ErrorAction SilentlyContinue).Line
    PubkeyAuthentication=(Select-String -Path $cfg -Pattern 'PubkeyAuthentication' -SimpleMatch -ErrorAction SilentlyContinue).Line
    LogLevel=(Select-String -Path $cfg -Pattern 'LogLevel' -SimpleMatch -ErrorAction SilentlyContinue).Line
    service=(Get-Service sshd -ErrorAction SilentlyContinue | Select-Object Status,StartType)
  }
  $report.admin_keys=@{
    path=$ak; exists=Test-Path $ak
    size=(Get-Item $ak -ErrorAction SilentlyContinue).Length
    icacls=(icacls $ak 2>$null)
    fingerprints= if (Test-Path $ak){ & ssh-keygen -lf $ak } else { @() }
  }
  $report.net=@{
    port22=(Test-NetConnection -ComputerName localhost -Port 22 | Select-Object -Property TcpTestSucceeded,RemoteAddress,RemotePort)
  }
  $log='C:\ProgramData\ssh\logs\sshd.log'
  if (Test-Path $log){ $report.logTail = Get-Content $log -Tail 40 }
}

if ($Role -eq 'client') {
  $report.key=@{}
  if ($KeyPath) {
    $pub="${KeyPath}.pub"
    $report.key.path=$KeyPath
    $report.key.pubExists=Test-Path $pub
    if (Test-Path $pub){ $report.key.fingerprint= & ssh-keygen -lf $pub }
  }
  if ($TargetHost) {
    $debug = & ssh -vvv -o IdentitiesOnly=yes -o PreferredAuthentications=publickey -o ConnectTimeout=10 -i $KeyPath $TargetHost "whoami" 2>&1
    $report.sshDebug = $debug | Where-Object { $_ -match 'Offering public key|key fingerprint|Authentications that can continue|Accepted publickey' }
  }
}

$ts=(Get-Date).ToString('yyyyMMdd_HHmmss')
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }
$out="logs\ssh_facts_$($report.host)_$ts.json"
$report | ConvertTo-Json -Depth 6 | Tee-Object -FilePath $out | Out-Null
Write-Host "WROTE $out"
