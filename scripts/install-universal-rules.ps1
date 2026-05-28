[CmdletBinding()]
param(
    [string]$ProjectRoot = (Get-Location).Path,

    [string]$UniversalRepo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,

    [switch]$InstallUserRulesClipboard,

    [switch]$FixGitignore = $true,

    [switch]$WhatIf
)

# install-universal-rules.ps1 — copy universal Cursor rules into a project .cursor/
#
#   .\install-universal-rules.ps1 -ProjectRoot "C:\path\to\your-repo"
#   .\install-universal-rules.ps1 -ProjectRoot . -InstallUserRulesClipboard

$ErrorActionPreference = 'Stop'

$ProjectRoot = (Resolve-Path $ProjectRoot).Path
$rulesSrc = Join-Path $UniversalRepo 'rules'
$skillsSrc = Join-Path $UniversalRepo 'skills'
$destRules = Join-Path $ProjectRoot '.cursor\rules'
$destSkills = Join-Path $ProjectRoot '.cursor\skills'

if (-not (Test-Path $rulesSrc)) {
    throw "Rules source not found: $rulesSrc"
}

function Write-Step([string]$Msg, [ConsoleColor]$Color = 'Cyan') {
    Write-Host $Msg -ForegroundColor $Color
}

Write-Step "Installing universal rules → $destRules"
if (-not $WhatIf) {
    New-Item -ItemType Directory -Path $destRules -Force | Out-Null
    Copy-Item -Path (Join-Path $rulesSrc '*.mdc') -Destination $destRules -Force
}

Get-ChildItem $rulesSrc -Filter '*.mdc' | ForEach-Object {
    if ($WhatIf) { Write-Host "[WhatIf] $($_.Name)" -ForegroundColor Yellow }
    else { Write-Host "  ✔ rules\$($_.Name)" -ForegroundColor Green }
}

if (Test-Path $skillsSrc) {
    Write-Step "Installing skills → $destSkills"
    if (-not $WhatIf) {
        New-Item -ItemType Directory -Path $destSkills -Force | Out-Null
        Copy-Item -Path (Join-Path $skillsSrc '*') -Destination $destSkills -Recurse -Force
    }
    Write-Host '  ✔ skills/github-actions-ci/' -ForegroundColor Green
}

$cursorReadme = @'
# `.cursor/` — shared rules (universal pack)

Installed from [cursor-universal-rule](https://github.com/wangyuanzhong/cursor-universal-rule).

| Path | Role |
|------|------|
| `rules/` | Cursor rules (`alwaysApply`) — **same files on cloud and local** |
| `skills/` | Agent playbooks (e.g. GitHub Actions) |

**Local opt-out** of post-push CI monitoring: create empty file `.cursor/.local-skip-post-push-ci`.

Do not commit secrets in `.cursor/`.
'@

$readmePath = Join-Path $ProjectRoot '.cursor\README.md'
if (-not $WhatIf) {
    New-Item -ItemType Directory -Path (Split-Path $readmePath) -Force | Out-Null
    Set-Content -Path $readmePath -Value $cursorReadme.TrimEnd() -Encoding UTF8
}
Write-Host '  ✔ .cursor/README.md' -ForegroundColor Green

if ($FixGitignore) {
    $gi = Join-Path $ProjectRoot '.gitignore'
    if (Test-Path $gi) {
        $raw = Get-Content $gi -Raw -Encoding UTF8
        $patched = $raw
        $patterns = @(
            '(?m)^\.cursor/\s*$',
            '(?m)^\.cursor/\*\s*$',
            '(?m)^\.cursor/\*\s*/\s*$'
        )
        $changed = $false
        foreach ($p in $patterns) {
            if ($patched -match $p) {
                $patched = $patched -replace $p, '# .cursor/ removed by install-universal-rules (track in git)'
                $changed = $true
            }
        }
        if ($changed -and -not $WhatIf) {
            Set-Content -Path $gi -Value $patched -NoNewline -Encoding UTF8
            Write-Host '  ✔ .gitignore — removed blanket .cursor/ ignore' -ForegroundColor Green
        }
        elseif ($changed) {
            Write-Host '  [WhatIf] would patch .gitignore' -ForegroundColor Yellow
        }
        else {
            Write-Host '  ○ .gitignore — no blanket .cursor/ ignore found' -ForegroundColor Gray
        }
    }
}

if ($InstallUserRulesClipboard) {
    $summary = Join-Path $UniversalRepo 'user-rules\SUMMARY-for-cursor-settings.md'
    if (-not (Test-Path $summary)) { throw "Missing $summary" }
    $text = Get-Content $summary -Raw -Encoding UTF8
    if ($WhatIf) {
        Write-Host '[WhatIf] Would copy User Rules summary to clipboard.' -ForegroundColor Yellow
    }
    else {
        Set-Clipboard -Value $text
        Write-Host ''
        Write-Host '✔ User Rules summary copied to clipboard.' -ForegroundColor Green
        Write-Host '  Paste: Cursor → Settings → Rules → User Rules → Save' -ForegroundColor Cyan
    }
}

Write-Host ''
Write-Host "Done. Project: $ProjectRoot" -ForegroundColor Cyan
Write-Host 'Next: git add .cursor/ && commit. Optional: -InstallUserRulesClipboard' -ForegroundColor Gray
