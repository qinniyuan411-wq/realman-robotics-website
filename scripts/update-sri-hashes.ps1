# SRI 哈希重算脚本（NEW-H01 + L-01 + C-7 维护工具）
# 用途：每次修改 prop/ 下的自托管脚本后，运行此脚本自动更新所有 HTML 中的 integrity 属性
# 用法：在仓库根目录运行 `powershell -NoProfile -File scripts\update-sri-hashes.ps1`

$ErrorActionPreference = 'Stop'
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

$scriptList = @(
    @{ Path = 'prop\supabase-cta.js';    Base = 'supabase-cta\.js' }
    @{ Path = 'prop\supabase-cta-cn.js'; Base = 'supabase-cta-cn\.js' }
    @{ Path = 'prop\tailwind.js';        Base = 'tailwind\.js' }
    @{ Path = 'prop\three.min.js';       Base = 'three\.min\.js' }
    @{ Path = 'prop\vanta.halo.min.js';  Base = 'vanta\.halo\.min\.js' }
)

foreach ($s in $scriptList) {
    if (-not (Test-Path $s.Path)) { Write-Warning "Missing: $($s.Path) (skipped)"; $s.Hash = $null; continue }
    $bytes = [IO.File]::ReadAllBytes($s.Path)
    $sha   = [Security.Cryptography.SHA384]::Create()
    $b64   = [Convert]::ToBase64String($sha.ComputeHash($bytes))
    $s.Hash = "sha384-$b64"
    Write-Host ("{0,-32} {1}" -f $s.Path, $s.Hash)
}

$htmlFiles = Get-ChildItem -Path cn,en -Recurse -Filter *.html
$totalChanged = 0
$utf8NoBom = New-Object Text.UTF8Encoding $false

foreach ($html in $htmlFiles) {
    $content = [IO.File]::ReadAllText($html.FullName, [Text.Encoding]::UTF8)
    $orig = $content
    foreach ($s in $scriptList) {
        if (-not $s.Hash) { continue }
        $pattern     = '(<script\s+src="[^"]*\b' + $s.Base + '")(\s+integrity="sha384-[^"]*")?(\s+crossorigin="anonymous")?'
        $replacement = '$1 integrity="' + $s.Hash + '" crossorigin="anonymous"'
        $content = [regex]::Replace($content, $pattern, $replacement)
    }
    if ($content -ne $orig) {
        [IO.File]::WriteAllText($html.FullName, $content, $utf8NoBom)
        $totalChanged++
    }
}

Write-Host ""
Write-Host "Updated $totalChanged HTML files." -ForegroundColor Green
