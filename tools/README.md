# Claude Desktop diagnostics

## Diagnose-ClaudeDesktop.ps1

A read-only diagnostic for working out why Claude Desktop / Cowork sessions or
dispatched tasks fail to start on a Windows workstation.

### Running it

Open PowerShell, `cd` to this folder, then:

```powershell
powershell -ExecutionPolicy Bypass -File .\Diagnose-ClaudeDesktop.ps1
```

Start Claude Desktop and reproduce the failure **before** running the script,
so the log sections have something recent to report.

Options:

| Parameter      | Default                                        | Purpose |
|----------------|------------------------------------------------|---------|
| `-VaultPath`   | `D:\Knowledge Vault 2026`                      | Root of the Knowledge Vault to test for reachability |
| `-OutputPath`  | `%USERPROFILE%\Desktop\claude-desktop-diagnostic.txt` | Where the transcript is written |
| `-SkipNetwork` | off                                            | Skip outbound reachability tests on a locked-down network |

### What it checks

1. Operating system, build and PowerShell version
2. Claude Desktop install location and version; `claude`, `node`, `npm`, `npx`, `git` on PATH
3. Running Claude and `node.exe` processes (local MCP servers appear as `node.exe`)
4. Config files, whether each parses as valid JSON, and whether every declared
   MCP server's launcher command actually resolves
5. Knowledge Vault drive, folder and key files — existence *and* readability
6. Recent log files, with error lines extracted
7. Proxy settings and TCP reachability of `api.anthropic.com`, `claude.ai`, `registry.npmjs.org`
8. Defender real-time protection status
9. A summary of every FAIL / WARN / INFO finding

### Safety

The script only reads. It makes no configuration changes, installs nothing and
starts no services.

Values under JSON keys containing `key`, `token`, `secret`, `password`,
`credential` or `authorization` are masked in the transcript, as are bare
`sk-…` strings. That masking is best-effort — **read the transcript before
sharing it**.

### Status

Not yet executed against a live Windows machine; it was authored in a Linux
container with no PowerShell available, so it has been reviewed by hand rather
than run. Report anything that misfires.
