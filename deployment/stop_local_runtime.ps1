$ErrorActionPreference = "SilentlyContinue"

$ports = @(8000, 18101, 18102)
$connections = Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in $ports }
$processes = $connections | Select-Object -ExpandProperty OwningProcess -Unique

foreach ($pid in $processes) {
  Stop-Process -Id $pid -Force
}

Write-Host ("Stopped processes on ports: " + ($ports -join ", "))
