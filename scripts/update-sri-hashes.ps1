# SRI 哈希重算脚本（NEW-H01 + L-01 维护工具）
# 用途：每次修改 prop/ 下的自托管脚本后，运行此脚本自动更新所有 HTML 中的 integrity 属性
# 用法：在仓库根目录运行 `pwsh -File scripts/update-sri-hashes.ps1`

$ErrorActionPreference = 'Stop'
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

$scripts = @{
    'prop\supabase-cta.js'      = 'supabase-cta\.js'
    'prop\supabase-cta-cn.js'   = 'supabase-cta-cn\.js'
    'prop\tailwind.js'          = 'tailwind\.js'
    'prop\three.min.js'         = 'three\.min\.js'
    'prop\vanta.halo.min.js'    = 'vanta\.halo\.min\.js'
}

# 1. 先算所有目标脚本的 SHA384
$hashes = @{}
foreach ($file in $scripts.Keys) {
    if (-not (Test-Path $file)) {
        Write-Warning "Missing: $file (skipped)"
        continue
    }
    $bytes = [IO.File]::ReadAllBytes($file)
    $sha   = [Security.Cryptography.SHA384]::Create()
    $b64   = [Convert]::ToBase64String($sha.ComputeHash($bytes))
    $hashes[$file] = "sha384-$b64"
    Write-Host ("{0,-32} {1}" -f $file, $hashes[$file])
}

# 2. 遍历所有 HTML，更新匹配 <script src="...basename"> 的 integrity 属性
$htmlFiles = Get-ChildItem -Path cn,en -Recurse -Filter *.html
$totalChanged = 0

foreach ($html in $htmlFiles) {
    $content = [IO.File]::ReadAllText($html.FullName, [Text.Encoding]::UTF8)
    $orig = $content

    foreach ($file in $scripts.Keys) {
        $basenamePattern = $scripts[$file]
        $hash = $hashes[$file]
        # 匹配 <script src="...basename"  ...> ；如果已有 integrity，先移除再加
        # 处理两种情况：(a) 无 integrity；(b) 有旧的 integrity 值需要更新
        $pattern = "(<script\s+src=`"[^`"]*\b$basenamePattern`")(\s+integrity=`"sha384-[^`"]*`")?(\s+crossorigin=`"anonymous`")?"
        $replacement = "`$1 integrity=`"$hash`" crossorigin=`"anonymous`""
        $content = [regex]::Replace($content, $pattern, $replacement)
    }

    if ($content -ne $orig) {
        [IO.File]::WriteAllText($html.FullName, $content, (New-Object Text.UTF8Encoding $false))
        $totalChanged++
    }
}

Write-Host ""
Write-Host "Updated $totalChanged HTML files." -ForegroundColor Green
