# stop.ps1 — 停止 MooFile 后端（app.py，端口 8888）
# 用法：在项目根目录执行  .\stop.ps1
$ErrorActionPreference = 'SilentlyContinue'
Set-Location $PSScriptRoot

# 递归终止指定进程的所有子进程（深度优先）
function Stop-ChildTree([int]$ParentId) {
    $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ParentId }
    foreach ($c in $children) {
        Stop-ChildTree $c.ProcessId
        Write-Host "[停止] 终止子进程 PID $($c.ProcessId)"
        Stop-Process -Id $c.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

$stopped = $false

# 1) 按命令行锚定本项目进程（解释器/工作目录位于 moofile_base 的 app.py），
#    先杀其子进程树再杀本体，避免误杀其他项目的 app.py
$targets = Get-CimInstance Win32_Process | Where-Object {
    ($_.CommandLine -match 'app\.py') -and
    ($_.ExecutablePath -match 'moofile_base' -or $_.CommandLine -match 'moofile_base')
}
foreach ($t in $targets) {
    Stop-ChildTree $t.ProcessId
    $cmd = $t.CommandLine
    if ($cmd -and $cmd.Length -gt 80) { $cmd = $cmd.Substring(0, 80) + '...' }
    Write-Host "[停止] 终止 MooFile 后端进程 PID $($t.ProcessId): $cmd"
    Stop-Process -Id $t.ProcessId -Force -ErrorAction SilentlyContinue
    $stopped = $true
}

# 2) 兜底：终止仍占用 8888 端口的监听进程
$listener = Get-NetTCPConnection -LocalPort 8888 -State Listen -ErrorAction SilentlyContinue
foreach ($l in $listener) {
    Write-Host "[停止] 终止 8888 端口监听进程 PID $($l.OwningProcess)"
    Stop-Process -Id $l.OwningProcess -Force -ErrorAction SilentlyContinue
    $stopped = $true
}

Start-Sleep -Seconds 2
if (Get-NetTCPConnection -LocalPort 8888 -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "[停止] 警告: 端口 8888 仍被占用，请手动检查残留进程。"
} elseif ($stopped) {
    Write-Host "[停止] MooFile 后端已停止，端口 8888 已释放。"
} else {
    Write-Host "[停止] 未发现运行中的 MooFile 后端进程。"
}

if ($Host.UI.SupportsPrompting) {
    Read-Host "`n按回车键退出"
}
exit 0
