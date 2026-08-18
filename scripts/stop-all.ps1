$ErrorActionPreference = "SilentlyContinue"

function Stop-Port([int]$Port) {
    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        Write-Host "[stop] Port $Port : not in use"
        return
    }

    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        try {
            $proc = Get-Process -Id $pid -ErrorAction Stop
            Write-Host "[stop] Port $Port : killing $($proc.ProcessName) (PID $pid)"
            Stop-Process -Id $pid -Force -ErrorAction Stop
        } catch {
            Write-Host "[stop] Port $Port : failed to kill PID $pid"
        }
    }
}

Write-Host "========================================"
Write-Host "  VisionText-RAG - Stop Services"
Write-Host "========================================"

Stop-Port 8000   # backend
Stop-Port 5173   # frontend

# Also stop orphaned uvicorn/node from this project if still running
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match "VisionText-RAG\\backend" -or $_.CommandLine -match "uvicorn" -and $_.CommandLine -match "VisionText-RAG" } |
    ForEach-Object {
        Write-Host "[stop] Orphan python: PID $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force
    }

Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
    Where-Object { $_.CommandLine -match "VisionText-RAG\\frontend" -or $_.CommandLine -match "vite" -and $_.CommandLine -match "VisionText-RAG" } |
    ForEach-Object {
        Write-Host "[stop] Orphan node: PID $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force
    }

Write-Host ""
Write-Host "Done. All VisionText-RAG services stopped."
