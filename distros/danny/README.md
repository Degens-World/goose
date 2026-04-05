# Danny Distro

This directory contains a minimal Goose-based distro profile for Danny Degen.

It is intentionally small and opinionated:

- Provider defaults to local Ollama.
- Model defaults to `qwen3-coder:30b`.
- The initial workflow focus is improving static crypto/AI/degen sites until they clear a stricter quality bar.

## Files

- `init-config.yaml`: first-run config defaults for a Danny-flavored Goose install
- `run-static-upgrade.sh`: Unix wrapper for the Danny static-site upgrade recipe
- `run-static-upgrade.ps1`: PowerShell wrapper for the same recipe

## Intended usage

1. Seed Goose with the Danny distro defaults.
2. Run the `danny_static_site_upgrade` recipe against an existing project directory.
3. Let Goose inspect, improve, and re-audit the site until it passes.

## Example

PowerShell:

```powershell
.\distros\danny\run-static-upgrade.ps1 -ProjectDir C:\agent-domains\zero-signal-oracle -ProjectName zero-signal-oracle
```

Bash:

```bash
./distros/danny/run-static-upgrade.sh /work/zero-signal-oracle zero-signal-oracle
```
