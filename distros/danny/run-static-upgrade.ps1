param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectDir,

    [Parameter(Mandatory = $true)]
    [string]$ProjectName
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..")
$recipe = Join-Path $repoRoot "workflow_recipes\danny_static_site_upgrade\recipe.yaml"

goose run --recipe $recipe --params "project_dir=$ProjectDir,project_name=$ProjectName"

