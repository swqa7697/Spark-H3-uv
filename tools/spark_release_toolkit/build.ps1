param(
    [Parameter(Mandatory = $true)] [string] $Python,
    [ValidateSet("both", "0.2.36", "0.2.37")]
    [string] $KitchenBase = "both"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$kit = $PSScriptRoot
$identity = Get-Content (Join-Path $kit "release.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$wheelhouse = Join-Path $kit "wheelhouse"
$Python = (Resolve-Path $Python).Path
foreach ($tool in @("git", "nvcc", "cl")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "$tool is missing from PATH; use a VS x64 developer shell with CUDA Toolkit"
    }
}
& $Python (Join-Path $kit "preflight.py") --report (Join-Path $kit "build-preflight.json")
if ($LASTEXITCODE -ne 0) { throw "Triton/GPU preflight failed" }
New-Item -ItemType Directory -Force -Path $wheelhouse | Out-Null
$versions = if ($KitchenBase -eq "both") { @("0.2.36", "0.2.37") } else { @($KitchenBase) }
foreach ($version in $versions) {
    & $Python (Join-Path $kit "ComfyUI-Spark-H3\kernel_builder.py") `
        --python $Python --output-dir $wheelhouse --kitchen-base $version `
        --architecture $identity.architecture --cuda-tag $identity.cuda_tag
    if ($LASTEXITCODE -ne 0) { throw "wheel build failed for comfy-kitchen $version" }
    $pattern = "comfy_kitchen-$version+spark.h3.$($identity.architecture).$($identity.cuda_tag).1-*-win_amd64.whl"
    $matches = @(Get-ChildItem $wheelhouse -Filter $pattern)
    if ($matches.Count -ne 1) { throw "expected one Windows wheel for $version; found $($matches.Count)" }
    $hash = (Get-FileHash $matches[0].FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    Write-Host "BUILT $($matches[0].FullName) SHA256=$hash"
}
