# SolarForge HTML setup UI (FastAPI)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PANEL_CALCULATOR_SKIP_RELOAD = "1"

function Find-FreePort {
    param([int[]]$Candidates = @(9090, 9333, 5173, 7643, 8888, 3000))
    foreach ($port in $Candidates) {
        $listener = $null
        try {
            $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
            $listener.Start()
            $listener.Stop()
            return $port
        } catch {
            if ($null -ne $listener) { $listener.Stop() }
        }
    }
    throw "No free port found. Close other dev servers and retry."
}

$port = Find-FreePort
$url = "http://127.0.0.1:$port"
Write-Host "Starting SolarForge setup UI at $url"
Write-Host "Press Ctrl+C to stop."
Start-Process $url
& .\venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port $port --reload
