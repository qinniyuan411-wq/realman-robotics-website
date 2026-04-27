# U-2 Edge Function 黑盒验证（纯后端，无需 Turnstile，可全自动）
# 模拟 IT 的渗透测试：直接打 Edge Function，看后端能否拒绝各类恶意/异常输入。
#
# 通过条件：所有恶意 payload 都被拒绝（HTTP 4xx + 明确 error code）；
# 不应出现任何 5xx 或意外 200。
#
# Output: evidence/u2-form/backend-blackbox.json

$ErrorActionPreference = 'Continue'
$EDGE_URL = 'https://dwtfijvpelpavdslvyry.supabase.co/functions/v1/submit-contact'
$OUT_DIR = "C:\Users\Qinni Yuan\Desktop\realman-robotics-website\evidence\u2-form"
New-Item -ItemType Directory -Force -Path $OUT_DIR | Out-Null

# Each test sends a JSON body via curl --data-binary @file.json so multibyte +
# special characters are preserved exactly (we hit the invalid_json bug last
# time when we used --data 'string').
$tests = @(
    @{ name = 'C-2-bad-origin';          expect = 'origin_not_allowed';
       body = @{ name='张三'; email='a@b.com'; company='Co'; consultType='sales'; turnstile='fake' };
       overrideOrigin = 'https://evil.example.com' },
    @{ name = 'C-4-no-turnstile-token';  expect = 'missing_turnstile';
       body = @{ name='张三'; email='a@b.com'; company='Co'; consultType='sales' } },
    @{ name = 'C-4-empty-token';         expect = 'missing_turnstile|invalid_turnstile';
       body = @{ name='张三'; email='a@b.com'; company='Co'; consultType='sales'; turnstile='' } },
    @{ name = 'C-4-fake-token';          expect = 'invalid_turnstile|turnstile_failed';
       body = @{ name='张三'; email='a@b.com'; company='Co'; consultType='sales'; turnstile='fake.token.value' } },
    @{ name = 'C-6-xss-script';          expect = 'invalid_(name|input)|missing_turnstile';
       body = @{ name='<script>alert(1)</script>'; email='a@b.com'; company='Co'; consultType='sales'; turnstile='fake' } },
    @{ name = 'C-6-sql-injection';       expect = 'invalid_(name|input)|missing_turnstile';
       body = @{ name="Robert'); DROP TABLE Students;--"; email='a@b.com'; company='Co'; consultType='sales'; turnstile='fake' } },
    @{ name = 'C-6-bad-email';           expect = 'invalid_email|missing_turnstile';
       body = @{ name='张三'; email='not-an-email'; company='Co'; consultType='sales'; turnstile='fake' } },
    @{ name = 'C-6-name-2000-chars';     expect = 'invalid_name|name_too_long|missing_turnstile';
       body = @{ name=('A'*2000); email='a@b.com'; company='Co'; consultType='sales'; turnstile='fake' } },
    @{ name = 'C-6-missing-required';    expect = 'missing_(name|email|company)|invalid_input';
       body = @{ email='a@b.com' } }
)

$results = @()
foreach ($t in $tests) {
    $tmp = [System.IO.Path]::GetTempFileName() + '.json'
    ($t.body | ConvertTo-Json -Compress -Depth 10) | Set-Content -Path $tmp -NoNewline -Encoding utf8
    $origin = if ($t.overrideOrigin) { $t.overrideOrigin } else { 'https://www.qinnitest.you' }
    $resp = curl.exe -s -w "`n__HTTP__%{http_code}__TIME__%{time_total}__" `
        -X POST `
        -H "Content-Type: application/json" `
        -H "Origin: $origin" `
        -H "Referer: $origin/cn/main/home.html" `
        --data-binary "@$tmp" $EDGE_URL 2>&1
    Remove-Item $tmp -ErrorAction SilentlyContinue
    $respStr = $resp -join "`n"
    if ($respStr -match '^(.*)\n__HTTP__(\d+)__TIME__([0-9.]+)__$') {
        $body = $matches[1].Trim()
        $http = [int]$matches[2]
        $time = [double]$matches[3]
    } else {
        $body = $respStr; $http = 0; $time = 0
    }
    $pass = ($http -ge 400 -and $http -lt 500) -or ($body -match $t.expect)
    $results += [PSCustomObject]@{
        Name = $t.name
        HTTP = $http
        ExpectPattern = $t.expect
        BodyPreview = $body.Substring(0, [Math]::Min($body.Length, 220))
        TimeSec = [math]::Round($time, 2)
        Pass = if ($pass) { 'PASS' } else { 'FAIL' }
    }
}
$results | Format-Table -AutoSize -Wrap

$report = @{
    edgeUrl = $EDGE_URL
    runAt = (Get-Date).ToString('o')
    summary = @{
        total = $results.Count
        passed = ($results | Where-Object Pass -eq 'PASS').Count
        failed = ($results | Where-Object Pass -eq 'FAIL').Count
    }
    cases = $results
}
$report | ConvertTo-Json -Depth 6 | Set-Content -Path "$OUT_DIR\backend-blackbox.json" -Encoding utf8

Write-Host ""
Write-Host "=== U-2 Backend Black-box Summary ===" -ForegroundColor Cyan
Write-Host "Total:  $($report.summary.total)"
Write-Host "Passed: $($report.summary.passed)" -ForegroundColor Green
Write-Host "Failed: $($report.summary.failed)" -ForegroundColor $(if ($report.summary.failed -eq 0) { 'Green' } else { 'Red' })
Write-Host "Report: $OUT_DIR\backend-blackbox.json"
