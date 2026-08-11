param(
    [string]$BaseBranch = "main",
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$branches = @(
    "feature/checkpoint1",
    "feature/checkpoint2",
    "feature/checkpoint3"
)

Push-Location $repoRoot
try {
    git rev-parse --is-inside-work-tree 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Not a Git repository: $repoRoot"
    }

    git show-ref --verify --quiet "refs/heads/$BaseBranch"
    if ($LASTEXITCODE -ne 0) {
        throw "Local base branch '$BaseBranch' does not exist."
    }

    foreach ($branch in $branches) {
        git show-ref --verify --quiet "refs/heads/$branch"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SKIP] $branch already exists locally."
        }
        else {
            git branch $branch $BaseBranch
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to create '$branch' from '$BaseBranch'."
            }
            Write-Host "[CREATED] $branch from $BaseBranch."
        }

        if ($Push) {
            git push --set-upstream origin $branch
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to push '$branch' to origin."
            }
            Write-Host "[PUSHED] $branch to origin."
        }
    }

    Write-Host "Done. Current checkout and working tree were not changed."
}
finally {
    Pop-Location
}
