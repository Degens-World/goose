param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectDir,

    [Parameter(Mandatory = $true)]
    [string]$ProjectName,

    [string]$Description = "",

    [string]$Model = "qwen3-coder:30b",

    [string]$OllamaUrl = "http://localhost:11434",

    [int]$CallTimeoutSecs = 240,

    [int]$AgentTimeoutSecs = 1800,

    [int]$MaxAttempts = 2,

    [string]$AgentScript = "D:\Agent Heartbeat\ollama_agent.py"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "run_static_upgrade.py"

python $runner $ProjectDir `
  --project-name $ProjectName `
  --description $Description `
  --model $Model `
  --ollama-url $OllamaUrl `
  --call-timeout-secs $CallTimeoutSecs `
  --agent-timeout-secs $AgentTimeoutSecs `
  --max-attempts $MaxAttempts `
  --agent-script $AgentScript
