# Read the .gitignore file
$gitignorePath = Join-Path -Path (Get-Location) -ChildPath '.gitignore'
$ignorePatterns = @()

if (Test-Path $gitignorePath) {
    $ignorePatterns = Get-Content $gitignorePath | Where-Object {
        $_ -and -not ($_.StartsWith('#') -or $_ -match '^\s*$')
    }
}

# Add hardcoded ignore patterns for node_modules and other cache directories
$additionalPatterns = @(
    'node_modules',
    '**/.cache',
    '**/.node_modules'
)
$ignorePatterns += $additionalPatterns

# Function to check if a file should be ignored
function ShouldIgnore($filePath, $patterns) {
    foreach ($pattern in $patterns) {
        # Convert .gitignore-like pattern to regex
        $patternRegex = [regex]::Escape($pattern).Replace('\*\*', '.*').Replace('\*', '[^\\\/]*').Replace('\?', '.')
        if ($filePath -match "$patternRegex") {
            return $true
        }
    }
    return $false
}

# List files and exclude those matching the .gitignore and hardcoded patterns
Get-ChildItem -Path . -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
    if (-not (ShouldIgnore $relativePath $ignorePatterns)) {
        $_.FullName
    }
}
