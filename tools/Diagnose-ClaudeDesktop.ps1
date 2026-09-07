<#
.SYNOPSIS
    Read-only diagnostic for Claude Desktop / Cowork / dispatch problems on Windows.

.DESCRIPTION
    Collects evidence about why Cowork sessions or dispatched tasks fail to start
    on a Windows workstation. Makes NO changes: it only reads files, queries
    versions and tests network reachability.

    Secrets found in config files are masked before being written to the
    transcript, but READ THE OUTPUT BEFORE SHARING IT.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\Diagnose-ClaudeDesktop.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\Diagnose-ClaudeDesktop.ps1 -VaultPath 'E:\Knowledge Vault 2026'
#>

[CmdletBinding()]
param(
    # Root of the Knowledge Vault that the start-of-chat instruction reads from.
    [string] $VaultPath = 'D:\Knowledge Vault 2026',

    # Where to write the transcript.
    [string] $OutputPath = "$env:USERPROFILE\Desktop\claude-desktop-diagnostic.txt",

    # Skip the outbound network tests (use on a locked-down network).
    [switch] $SkipNetwork
)

$ErrorActionPreference = 'Continue'
$script:Report = [System.Collections.Generic.List[string]]::new()
$script:Findings = [System.Collections.Generic.List[string]]::new()

function Add-Line { param([string] $Text = '') $script:Report.Add($Text); Write-Host $Text }

function Add-Section {
    param([string] $Title)
    Add-Line ''
    Add-Line ('=' * 70)
    Add-Line "  $Title"
    Add-Line ('=' * 70)
}

function Add-Finding {
    param(
        [ValidateSet('FAIL', 'WARN', 'INFO')] [string] $Level,
        [string] $Message
    )
    $script:Findings.Add("[$Level] $Message")
    Add-Line "  >> $Level : $Message"
}

# Mask anything that looks like a credential before it reaches the transcript.
function Protect-Secrets {
    param([string] $Text)
    if ([string]::IsNullOrEmpty($Text)) { return $Text }
    $pattern = '(?i)("(?:[\w-]*(?:key|token|secret|password|passwd|credential|authorization)[\w-]*)"\s*:\s*")([^"]*)(")'
    $masked  = [regex]::Replace($Text, $pattern, { param($m) $m.Groups[1].Value + '***REDACTED***' + $m.Groups[3].Value })
    # Bare-looking API keys that appear outside JSON string pairs.
    $masked  = [regex]::Replace($masked, '(?i)\bsk-[A-Za-z0-9_\-]{12,}', 'sk-***REDACTED***')
    return $masked
}

function Test-Command {
    param([string] $Name, [string] $VersionArg = '--version')
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Add-Line "  $Name : NOT FOUND on PATH"
        return $null
    }
    $version = try { (& $Name $VersionArg 2>&1 | Select-Object -First 1) } catch { "(version query failed: $_)" }
    Add-Line "  $Name : $version"
    Add-Line "      path: $($cmd.Source)"
    return $cmd
}

Add-Line "Claude Desktop / Cowork diagnostic"
Add-Line "Generated : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
Add-Line "Machine   : $env:COMPUTERNAME"
Add-Line "User      : $env:USERNAME"

# ---------------------------------------------------------------- 1. Platform
Add-Section '1. Operating system and shell'
try {
    $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    Add-Line "  OS            : $($os.Caption)"
    Add-Line "  Version/build : $($os.Version)"
    Add-Line "  Architecture  : $($os.OSArchitecture)"
    Add-Line "  Last boot     : $($os.LastBootUpTime)"
} catch { Add-Line "  Could not query OS: $_" }
Add-Line "  PowerShell    : $($PSVersionTable.PSVersion)"
Add-Line "  Is elevated   : $(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))"

# ------------------------------------------------------- 2. Claude installs
Add-Section '2. Claude Desktop / Claude Code installation'

$desktopCandidates = @(
    "$env:LOCALAPPDATA\AnthropicClaude",
    "$env:LOCALAPPDATA\Programs\Claude",
    "$env:LOCALAPPDATA\Programs\claude",
    "$env:PROGRAMFILES\Claude",
    "${env:PROGRAMFILES(X86)}\Claude"
)
$foundDesktop = $false
foreach ($path in $desktopCandidates) {
    if (Test-Path -LiteralPath $path) {
        $foundDesktop = $true
        Add-Line "  FOUND install dir : $path"
        Get-ChildItem -LiteralPath $path -Filter 'app-*' -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name | ForEach-Object { Add-Line "      version dir  : $($_.Name)" }
        Get-ChildItem -LiteralPath $path -Filter '*.exe' -File -ErrorAction SilentlyContinue |
            ForEach-Object {
                $fv = $_.VersionInfo.FileVersion
                Add-Line "      exe          : $($_.Name)  (file version $fv)"
            }
    }
}
if (-not $foundDesktop) {
    Add-Finding 'WARN' 'Claude Desktop install directory not found in any of the usual locations. If you run Claude only in a browser, Cowork/dispatch desktop features will not be present.'
}

Add-Line ''
Add-Line '  CLI / runtime tooling:'
$claudeCmd = Test-Command -Name 'claude'
$nodeCmd   = Test-Command -Name 'node'
$npmCmd    = Test-Command -Name 'npm'
$npxCmd    = Test-Command -Name 'npx'
$gitCmd    = Test-Command -Name 'git'

if (-not $nodeCmd) {
    Add-Finding 'FAIL' 'Node.js is not on PATH. Most local MCP servers (including Desktop Commander) are launched via node/npx, so every MCP server will fail to start without it.'
}
if ($nodeCmd) {
    $nodeMajor = 0
    try { $nodeMajor = [int](((& node --version) -replace '^v', '') -split '\.')[0] } catch { }
    if ($nodeMajor -gt 0 -and $nodeMajor -lt 18) {
        Add-Finding 'WARN' "Node.js major version is $nodeMajor. Current MCP servers generally expect Node 18 or newer."
    }
}

# ---------------------------------------------------------- 3. Running procs
Add-Section '3. Running Claude processes'
$procs = Get-Process -ErrorAction SilentlyContinue |
         Where-Object { $_.ProcessName -match '(?i)claude|anthropic' }
if ($procs) {
    $procs | Sort-Object ProcessName | ForEach-Object {
        $mb      = [math]::Round($_.WorkingSet64 / 1MB, 1)
        $started = try { $_.StartTime } catch { '(access denied)' }
        Add-Line ("  PID {0,-8} {1,-28} {2,8} MB   started {3}" -f $_.Id, $_.ProcessName, $mb, $started)
    }
} else {
    Add-Line '  No Claude/Anthropic processes currently running.'
    Add-Finding 'INFO' 'Claude is not running right now. Start the app before reading the log sections below, or the logs will be stale.'
}

# Node processes are how MCP servers show up.
$nodeProcs = Get-Process -Name 'node' -ErrorAction SilentlyContinue
if ($nodeProcs) {
    Add-Line "  node.exe processes running: $($nodeProcs.Count)  (MCP servers appear here)"
} else {
    Add-Line '  node.exe processes running: 0'
    if ($procs) {
        Add-Finding 'WARN' 'Claude is running but there are no node.exe processes. That strongly suggests no local MCP server (e.g. Desktop Commander) has started successfully.'
    }
}

# -------------------------------------------------------------- 4. Config
Add-Section '4. Configuration files'

$configCandidates = @(
    "$env:APPDATA\Claude\claude_desktop_config.json",
    "$env:USERPROFILE\.claude.json",
    "$env:USERPROFILE\.claude\settings.json",
    "$env:USERPROFILE\.claude\settings.local.json",
    "$env:APPDATA\Claude\config.json"
)

$mcpServerNames = @()
foreach ($cfg in $configCandidates) {
    if (-not (Test-Path -LiteralPath $cfg)) {
        Add-Line "  MISSING : $cfg"
        continue
    }
    $info = Get-Item -LiteralPath $cfg
    Add-Line ''
    Add-Line "  FOUND   : $cfg"
    Add-Line "      size $($info.Length) bytes, modified $($info.LastWriteTime)"

    $raw = $null
    try { $raw = Get-Content -LiteralPath $cfg -Raw -ErrorAction Stop } catch {
        Add-Finding 'FAIL' "Cannot read $cfg : $_"
        continue
    }

    # Validity matters: a malformed config silently disables every MCP server.
    try {
        $json = $raw | ConvertFrom-Json -ErrorAction Stop
        Add-Line '      JSON parse: OK'
    } catch {
        Add-Finding 'FAIL' "$cfg is NOT valid JSON: $($_.Exception.Message). Claude will ignore this file, which disables every MCP server defined in it."
        continue
    }

    if ($json.PSObject.Properties.Name -contains 'mcpServers' -and $json.mcpServers) {
        $names = $json.mcpServers.PSObject.Properties.Name
        $mcpServerNames += $names
        Add-Line "      MCP servers declared: $($names -join ', ')"
        foreach ($n in $names) {
            $srv = $json.mcpServers.$n
            $launcher = $srv.command
            Add-Line "        - $n"
            Add-Line "            command : $launcher"
            if ($srv.args) { Add-Line "            args    : $((Protect-Secrets ($srv.args -join ' ')))" }
            if ($launcher) {
                $resolved = Get-Command $launcher -ErrorAction SilentlyContinue
                if ($resolved) {
                    Add-Line "            resolves: $($resolved.Source)"
                } elseif (Test-Path -LiteralPath $launcher) {
                    Add-Line "            resolves: $launcher (literal path exists)"
                } else {
                    Add-Finding 'FAIL' "MCP server '$n' has command '$launcher' which cannot be resolved on PATH or as a file. This server will fail to start."
                }
            }
        }
    } else {
        Add-Line '      No mcpServers block in this file.'
    }
}

if ($mcpServerNames -match '(?i)desktop.?commander') {
    Add-Line ''
    Add-Line '  Desktop Commander IS declared in configuration.'
} else {
    Add-Finding 'FAIL' 'Desktop Commander is NOT declared in any configuration file found. Any instruction that depends on it (such as reading the Knowledge Vault at start of chat) cannot run.'
}

# ------------------------------------------------------------- 5. The vault
Add-Section '5. Knowledge Vault accessibility'

Add-Line "  Vault path under test: $VaultPath"
$vaultDrive = $null
try { $vaultDrive = (Split-Path -Qualifier $VaultPath) } catch { }

if ($vaultDrive) {
    $psDrive = Get-PSDrive -Name ($vaultDrive.TrimEnd(':')) -ErrorAction SilentlyContinue
    if ($psDrive) {
        $freeBytes = $psDrive.Free
        $usedText  = if ($null -ne $psDrive.Used)  { "$([math]::Round($psDrive.Used / 1GB, 2)) GB" } else { 'n/a' }
        $freeText  = if ($null -ne $freeBytes)     { "$([math]::Round($freeBytes / 1GB, 2)) GB" } else { 'n/a' }
        Add-Line "  Drive $vaultDrive present. Used $usedText, free $freeText."
        if ($null -ne $freeBytes -and $freeBytes -lt 1GB) {
            Add-Finding 'WARN' "Drive $vaultDrive has under 1 GB free. Writes will fail."
        }
    } else {
        Add-Finding 'FAIL' "Drive $vaultDrive is not present on this machine. If it is a removable or network drive it may simply not be mounted right now."
    }
}

if (Test-Path -LiteralPath $VaultPath) {
    Add-Line "  Vault root EXISTS."
    $keyFiles = @(
        (Join-Path $VaultPath 'START_NEW_CHAT_HERE.txt'),
        (Join-Path $VaultPath 'Claude_Personal\DESKTOP_COMMANDER_POLICY.txt')
    )
    foreach ($f in $keyFiles) {
        if (Test-Path -LiteralPath $f) {
            $fi = Get-Item -LiteralPath $f
            Add-Line "    OK      : $f  ($($fi.Length) bytes, modified $($fi.LastWriteTime))"
            # Prove it is actually readable, not just present.
            try {
                $null = Get-Content -LiteralPath $f -TotalCount 1 -ErrorAction Stop
                Add-Line "              readable: yes"
            } catch {
                Add-Finding 'FAIL' "File exists but cannot be read (permissions or lock): $f"
            }
        } else {
            Add-Finding 'FAIL' "Expected file is MISSING: $f"
        }
    }
} else {
    Add-Finding 'FAIL' "Vault root does not exist or is not reachable: $VaultPath"
}

# ----------------------------------------------------------------- 6. Logs
Add-Section '6. Recent log entries'

$logDirs = @(
    "$env:APPDATA\Claude\logs",
    "$env:LOCALAPPDATA\AnthropicClaude\logs",
    "$env:USERPROFILE\.claude\logs"
)
$anyLogs = $false
foreach ($dir in $logDirs) {
    if (-not (Test-Path -LiteralPath $dir)) { continue }
    $anyLogs = $true
    Add-Line ''
    Add-Line "  Log directory: $dir"
    Get-ChildItem -LiteralPath $dir -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 8 | ForEach-Object {
            Add-Line "    $($_.Name)  ($($_.Length) bytes, modified $($_.LastWriteTime))"
        }

    # Pull error lines out of the most recently touched logs.
    Get-ChildItem -LiteralPath $dir -File -Filter '*.log' -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 4 | ForEach-Object {
            $hits = Select-String -LiteralPath $_.FullName `
                        -Pattern 'error|failed|exception|ENOENT|EACCES|refused|timeout|disconnect|spawn' `
                        -ErrorAction SilentlyContinue |
                    Select-Object -Last 15
            if ($hits) {
                Add-Line ''
                Add-Line "    --- error lines from $($_.Name) ---"
                foreach ($h in $hits) {
                    Add-Line ('      ' + (Protect-Secrets $h.Line.Trim()))
                }
            }
        }
}
if (-not $anyLogs) {
    Add-Finding 'WARN' 'No Claude log directories found. Without logs the failure cannot be pinpointed. Start the app, reproduce the failure, then re-run this script.'
}

# -------------------------------------------------------------- 7. Network
Add-Section '7. Network and proxy'

Add-Line "  HTTP_PROXY  : $(if ($env:HTTP_PROXY)  { $env:HTTP_PROXY }  else { '(not set)' })"
Add-Line "  HTTPS_PROXY : $(if ($env:HTTPS_PROXY) { $env:HTTPS_PROXY } else { '(not set)' })"
Add-Line "  NO_PROXY    : $(if ($env:NO_PROXY)    { $env:NO_PROXY }    else { '(not set)' })"

try {
    $ieProxy = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction Stop
    Add-Line "  System proxy enabled : $($ieProxy.ProxyEnable)"
    if ($ieProxy.ProxyServer) { Add-Line "  System proxy server  : $($ieProxy.ProxyServer)" }
} catch { Add-Line '  Could not read system proxy settings.' }

if ($SkipNetwork) {
    Add-Line '  Network reachability tests skipped (-SkipNetwork).'
} else {
    foreach ($endpoint in @('api.anthropic.com', 'claude.ai', 'registry.npmjs.org')) {
        try {
            $r = Test-NetConnection -ComputerName $endpoint -Port 443 -WarningAction SilentlyContinue -ErrorAction Stop
            if ($r.TcpTestSucceeded) {
                Add-Line "  ${endpoint}:443  reachable"
            } else {
                Add-Finding 'FAIL' "Cannot open a TCP connection to ${endpoint}:443. A firewall, proxy or DNS problem will stop Claude working."
            }
        } catch {
            Add-Finding 'WARN' "Reachability test for $endpoint could not run: $($_.Exception.Message)"
        }
    }
}

# ------------------------------------------------------------ 8. Defender
Add-Section '8. Security software (informational)'
try {
    $mp = Get-MpComputerStatus -ErrorAction Stop
    Add-Line "  Defender real-time protection : $($mp.RealTimeProtectionEnabled)"
    Add-Line "  Defender tamper protection    : $($mp.IsTamperProtected)"
    Add-Line '  Note: real-time scanning can block a local MCP server from spawning.'
} catch {
    Add-Line '  Defender status unavailable (third-party AV, or insufficient rights).'
}

# ------------------------------------------------------------- 9. Summary
Add-Section '9. Summary of findings'
if ($script:Findings.Count -eq 0) {
    Add-Line '  No problems detected by this script.'
    Add-Line '  If dispatch/Cowork still fails, the cause is server-side or account-side'
    Add-Line '  (plan entitlement, feature availability, or sign-in state) rather than local.'
} else {
    foreach ($level in @('FAIL', 'WARN', 'INFO')) {
        $prefix   = "[$level]"
        $matching = $script:Findings | Where-Object { $_.StartsWith($prefix) }
        if ($matching) {
            Add-Line ''
            foreach ($m in $matching) { Add-Line "  $m" }
        }
    }
}

Add-Line ''
Add-Line ('=' * 70)
Add-Line "Transcript written to: $OutputPath"
Add-Line 'Review it for anything sensitive before sharing.'

try {
    $script:Report | Set-Content -LiteralPath $OutputPath -Encoding UTF8 -ErrorAction Stop
} catch {
    Write-Warning "Could not write transcript to ${OutputPath}: $_"
}
