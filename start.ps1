# start.ps1 — 启动 MooFile 后端（app.py，端口 8888）
# 先停止可能存在的旧实例，再启动新实例，避免端口占用与多实例冲突
# 用法：在项目根目录执行  .\start.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$exitCode = 0

try {
    # 1) 先停止旧实例（无进程时 stop.ps1 自动跳过并返回 0）
    Write-Host "[启动] 检查并停止旧实例 ..."
    if (Test-Path "$PSScriptRoot\stop.ps1") {
        & "$PSScriptRoot\stop.ps1"
    } else {
        $targets = Get-CimInstance Win32_Process | Where-Object {
            ($_.CommandLine -match 'app\.py') -and
            ($_.ExecutablePath -match 'moofile_base' -or $_.CommandLine -match 'moofile_base')
        }
        foreach ($t in $targets) { Stop-Process -Id $t.ProcessId -Force -ErrorAction SilentlyContinue }
        $listener = Get-NetTCPConnection -LocalPort 8888 -State Listen -ErrorAction SilentlyContinue
        foreach ($l in $listener) { Stop-Process -Id $l.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2
    }

    # 2) 确认端口已释放
    if (Get-NetTCPConnection -LocalPort 8888 -State Listen -ErrorAction SilentlyContinue) {
        Write-Host "[启动] 错误: 端口 8888 仍被占用，无法启动。请先手动清理残留进程。"
        $exitCode = 1
        throw "port busy"
    }

    # 3) 校验虚拟环境
    if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
        Write-Host "[启动] 错误: 未找到虚拟环境解释器 .venv\Scripts\python.exe"
        $exitCode = 1
        throw "venv missing"
    }

    # 4) 启动后端（MCP 由 .env 中 MOOFILE_WITH_MCP=false 关闭，无需额外参数）
    Write-Host "[启动] 正在启动 MooFile 后端 (app.py) ..."
    $proc = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
        -ArgumentList "app.py" `
        -WorkingDirectory $PSScriptRoot `
        -WindowStyle Hidden `
        -PassThru

    Start-Sleep -Seconds 5
    if (Get-NetTCPConnection -LocalPort 8888 -State Listen -ErrorAction SilentlyContinue) {
        Write-Host "[启动] MooFile 后端已启动: http://127.0.0.1:8888 (PID $($proc.Id))"
        Write-Host "[启动] 停止请执行: .\stop.ps1"
    } else {
        Write-Host "[启动] 后端启动失败（进程已退出），请检查 logs\ 目录或直接运行 python app.py 查看报错。"
        $exitCode = 1
    }
} catch {
    if ($exitCode -eq 0) { $exitCode = 1 }
    Write-Host "[启动] 发生错误: $($_.Exception.Message)"
}

if ($Host.UI.SupportsPrompting) {
    Read-Host "`n按回车键退出"
}
exit $exitCode
