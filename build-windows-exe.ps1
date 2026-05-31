param(
    [string]$OutputPath = "release\AI Search Algorithm Visualizer.exe"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $root "tools\windows-launcher\Launcher.cs"
$output = Join-Path $root $OutputPath
$outputDir = Split-Path -Parent $output

$cscCandidates = @(
    "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe"
)

$csc = $cscCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $csc) {
    throw "Could not find the Windows C# compiler. Install .NET Framework developer tools or Visual Studio Build Tools."
}

$files = @(
    "index.html",
    "styles.css",
    "favicon.png",
    "gif.worker.js",
    "Node.py",
    "PriorityQueue.py",
    "SearchAgent.py",
    "main.py",
    "docs\algorithm-guide.md",
    "docs\api-reference.md",
    "docs\deployment-guide.md",
    "vendor\brython.min.js",
    "vendor\brython_stdlib.js",
    "vendor\gif.js",
    "vendor\jspdf.umd.min.js",
    "vendor\jszip.min.js",
    "vendor\lucide.min.js"
)

foreach ($file in $files) {
    $fullPath = Join-Path $root $file
    if (-not (Test-Path $fullPath)) {
        throw "Missing file required for EXE build: $file"
    }
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$resourceArgs = foreach ($file in $files) {
    $fullPath = Join-Path $root $file
    $resourceName = "app." + ($file -replace "\\", "." -replace "/", ".")
    "/resource:$fullPath,$resourceName"
}

& $csc `
    /nologo `
    /target:winexe `
    /optimize+ `
    /platform:anycpu `
    /out:$output `
    /reference:System.dll `
    /reference:System.Drawing.dll `
    /reference:System.Windows.Forms.dll `
    $resourceArgs `
    $launcher

Write-Host "Created $output"
