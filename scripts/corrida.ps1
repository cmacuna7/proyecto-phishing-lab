# Corrida completa del laboratorio (antes y después de los controles) guardada por persona.
#
#   .\scripts\corrida.ps1 -Persona zaith-manangon
#   .\scripts\corrida.ps1 -Carpeta evidence\corridas\2026-10-25_zaith-manangon -SoloAnalizar
#
# Cada corrida queda en evidence\corridas\<AAAA-MM-DD>_<persona>[_N]\ y nunca sobrescribe otra:
#   resultados\  JSON/CSV de run_scenario.py      zap\       CSV exportados de ZAP
#   logs\baseline, logs\hardened  copia de logs\    analisis\  informes y comparacion.md
param(
    [string]$Persona,
    [string]$Carpeta,
    [switch]$SoloAnalizar
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot)

function Run {   # ejecuta un comando externo y se detiene si falla
    & $args[0] $args[1..($args.Count - 1)]
    if ($LASTEXITCODE) { throw "Falló: $args" }
}

if (-not $Carpeta) {
    if (-not $Persona) { throw "Indique -Persona (p. ej. -Persona zaith-manangon)" }
    $Carpeta = "evidence/corridas/$(Get-Date -Format yyyy-MM-dd)_$Persona"
    $base = $Carpeta; $n = 2
    while (Test-Path $Carpeta) { $Carpeta = "${base}_$n"; $n++ }
}
$Carpeta = $Carpeta -replace '\\', '/'   # la misma ruta se usa dentro del contenedor (Linux)

if (-not $SoloAnalizar) {
    Write-Host "== Corrida en $Carpeta" -ForegroundColor Cyan
    foreach ($mode in "baseline", "hardened") {
        Write-Host "== Modo $mode" -ForegroundColor Cyan
        Run docker compose down
        Remove-Item -Recurse -Force logs, data -ErrorAction SilentlyContinue
        $env:CONTROLS_MODE = $mode
        Run docker compose up -d --build --wait
        foreach ($t in "apache", "nginx") {
            Run docker compose exec client1 python scripts/run_scenario.py --target $t --mode $mode --out-dir "$Carpeta/resultados"
            Run docker compose exec client1 python scripts/zap_export.py --baseurl "http://$t" --out "$Carpeta/zap/${t}_$mode.csv"
        }
        New-Item -ItemType Directory -Force "$Carpeta/logs" | Out-Null
        Copy-Item -Recurse logs "$Carpeta/logs/$mode"
        Get-ChildItem -Recurse "$Carpeta/logs/$mode" -Filter *.pid | Remove-Item
    }
    Remove-Item Env:CONTROLS_MODE
}

Write-Host "== Análisis de $Carpeta" -ForegroundColor Cyan
foreach ($mode in "baseline", "hardened") {
    foreach ($t in "apache", "nginx") {
        $l = "$Carpeta/logs/$mode"
        $audit = if (Test-Path "$l/app-$t/auth.log") { @("--audit", "$l/app-$t/auth.log") } else { @() }  # baseline no audita
        Run python scripts/analyze_logs.py @audit --access "$t=$l/$t/access.log" --zap-csv "$Carpeta/zap/${t}_$mode.csv" --out "$Carpeta/analisis/${t}_$mode.md" | Out-Null
    }
}
Run python scripts/compare_results.py --results "$Carpeta/resultados/*.json" --out "$Carpeta/analisis/comparacion.md"
Run python scripts/compare_results.py | Out-Null   # todas las corridas: evidence/corridas/comparacion.md
Write-Host "== Listo: $Carpeta (comparación general en evidence/corridas/comparacion.md)" -ForegroundColor Green
