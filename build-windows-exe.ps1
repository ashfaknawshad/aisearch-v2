param(
    [string]$OutputPath = "release\AI Search Algorithm Visualizer.exe"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
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

$webView2Root = Join-Path $root "tools\webview2"
$webView2WinForms = Join-Path $webView2Root "Microsoft.Web.WebView2.WinForms.dll"
$webView2Core = Join-Path $webView2Root "Microsoft.Web.WebView2.Core.dll"
$webView2LoaderX64 = Join-Path $webView2Root "x64\WebView2Loader.dll"
$webView2LoaderX86 = Join-Path $webView2Root "x86\WebView2Loader.dll"

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

$referenceArgs = @(
    "/reference:$webView2WinForms",
    "/reference:$webView2Core"
)
$sourceFile = Join-Path $root "tools\windows-launcher\NativeWindowLauncher.cs"

foreach ($file in @($webView2WinForms, $webView2Core, $webView2LoaderX64, $webView2LoaderX86)) {
    if (-not (Test-Path $file)) {
        throw "Missing WebView2 build file: $file"
    }
}

$resourceArgs += "/resource:$webView2WinForms,deps.Microsoft.Web.WebView2.WinForms.dll"
$resourceArgs += "/resource:$webView2Core,deps.Microsoft.Web.WebView2.Core.dll"
$resourceArgs += "/resource:$webView2LoaderX64,deps.x64.WebView2Loader.dll"
$resourceArgs += "/resource:$webView2LoaderX86,deps.x86.WebView2Loader.dll"

& $csc `
    /nologo `
    /target:winexe `
    /optimize+ `
    /platform:anycpu `
    /out:$output `
    /reference:System.dll `
    /reference:System.Drawing.dll `
    /reference:System.Windows.Forms.dll `
    $referenceArgs `
    $resourceArgs `
    $sourceFile

Write-Host "Created $output"
