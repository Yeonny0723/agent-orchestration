param(
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$Branch = "master"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$validatorScript = Join-Path $repoRoot "scripts\validate_plugin.py"
$publicMarketplaceSource = "https://github.com/Yeonny0723/agent-orchestration.git"
$codexMarketplaceSource = "Yeonny0723/agent-orchestration"
$releaseRef = $Branch.Trim()
$marketplaceName = "agent-orchestration-marketplace"
$pluginSelector = "agent-orchestration@$marketplaceName"

function Get-CommandOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$CommandArgs,

        [Parameter(Mandatory = $true)]
        [string]$Step
    )

    $commandOutput = & $FilePath @CommandArgs 2>&1
    $exitCode = $LASTEXITCODE
    $outputText = ($commandOutput | ForEach-Object { $_.ToString() }) -join "`n"

    if ($exitCode -ne 0) {
        throw "$Step failed with exit code $exitCode.`n$outputText"
    }

    return $outputText.Trim()
}

function Invoke-RequiredCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$CommandArgs,

        [Parameter(Mandatory = $true)]
        [string]$Step
    )

    Write-Host "[$Step]"
    $commandOutput = Get-CommandOutput $FilePath $CommandArgs $Step
    if ($commandOutput) {
        Write-Host $commandOutput
    }
    return $commandOutput
}

function Normalize-GitSource {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source
    )

    $normalizedSource = $Source.Trim()
    $fragmentIndex = $normalizedSource.IndexOf("#", [System.StringComparison]::Ordinal)
    if ($fragmentIndex -ge 0) {
        $normalizedSource = $normalizedSource.Substring(0, $fragmentIndex)
    }
    while ($normalizedSource.EndsWith("/")) {
        $normalizedSource = $normalizedSource.Substring(0, $normalizedSource.Length - 1)
    }
    if ($normalizedSource.EndsWith(".git", [System.StringComparison]::OrdinalIgnoreCase)) {
        $normalizedSource = $normalizedSource.Substring(0, $normalizedSource.Length - 4)
    }
    return $normalizedSource.ToLowerInvariant()
}

function Assert-PublicOrigin {
    $configuredOrigin = Get-CommandOutput git @("-C", $repoRoot, "remote", "get-url", "origin") "Read origin URL"
    $expectedOrigin = Normalize-GitSource $publicMarketplaceSource
    $actualOrigin = Normalize-GitSource $configuredOrigin
    if ($actualOrigin -ne $expectedOrigin) {
        throw "Origin must point to '$publicMarketplaceSource'; configured origin is '$configuredOrigin'."
    }
}

function Test-MarketplaceNetworkFailure {
    param(
        [Parameter(Mandatory = $true)]
        [string]$OutputText
    )

    return $OutputText -match "(?i)(network|timeout|timed out|connection|resolve host|could not resolve|authentication|unauthorized|forbidden|permission denied|remote.*(failed|error)|fetch.*failed|unable to access|repository.*not found|rate limit|proxy|ssl|certificate)"
}

function Remove-KnownCliWarningsFromJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RawOutput,

        [Parameter(Mandatory = $true)]
        [string]$Step
    )

    $outputLines = $RawOutput -split "`r?`n"
    $jsonStartIndex = -1
    for ($lineIndex = 0; $lineIndex -lt $outputLines.Count; $lineIndex++) {
        if ($outputLines[$lineIndex].TrimStart().StartsWith("{") -or $outputLines[$lineIndex].TrimStart().StartsWith("[")) {
            $jsonStartIndex = $lineIndex
            break
        }

        if ($outputLines[$lineIndex].Trim() -and $outputLines[$lineIndex] -notmatch "(?i)^\s*WARNING\s*:\s+") {
            throw "$Step contained non-warning output before JSON."
        }
    }

    if ($jsonStartIndex -lt 0) {
        throw "$Step did not contain a JSON object or array."
    }

    return ($outputLines[$jsonStartIndex..($outputLines.Count - 1)] -join "`n").Trim()
}

function Get-MarketplaceListState {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HostCommand,

        [Parameter(Mandatory = $true)]
        [string]$HostName
    )

    Write-Host "[Inspect $HostName marketplace registrations]"
    $commandOutput = & $HostCommand @("plugin", "marketplace", "list", "--json") 2>&1
    $exitCode = $LASTEXITCODE
    $outputText = ($commandOutput | ForEach-Object { $_.ToString() }) -join "`n"
    if ($outputText) {
        Write-Host $outputText
    }

    if ($exitCode -ne 0) {
        if (Test-MarketplaceNetworkFailure $outputText) {
            throw "Read $HostName marketplace registrations failed with a network or authentication error. No registration was removed.`n$outputText"
        }
        throw "Read $HostName marketplace registrations failed. No registration was removed.`n$outputText"
    }

    try {
        $cleanJsonText = Remove-KnownCliWarningsFromJson $outputText "$HostName marketplace list"
        $parsedState = ConvertFrom-RequiredJson $cleanJsonText "$HostName marketplace list"
        if ($parsedState -isnot [System.Array]) {
            throw "$HostName marketplace list must be a JSON array. No registration was removed."
        }
        return ,$parsedState
    }
    catch {
        if (Test-MarketplaceNetworkFailure $outputText) {
            throw "Read $HostName marketplace registrations returned a network or authentication error. No registration was removed.`n$outputText"
        }
        throw
    }
}

function Get-CanonicalRepositoryIdentity {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source
    )

    $normalizedSource = $Source.Trim()
    $fragmentIndex = $normalizedSource.IndexOf("#", [System.StringComparison]::Ordinal)
    if ($fragmentIndex -ge 0) {
        $normalizedSource = $normalizedSource.Substring(0, $fragmentIndex)
    }
    $atRefIndex = $normalizedSource.IndexOf("@", [System.StringComparison]::Ordinal)
    if ($atRefIndex -gt 0 -and $normalizedSource -notmatch "^[a-z]+://") {
        $normalizedSource = $normalizedSource.Substring(0, $atRefIndex)
    }
    $githubUrlPattern = "^https?://github\.com/([^/]+)/([^/?#]+?)(?:\.git)?/?$"
    $githubShorthandPattern = "^([^/\s]+)/([^/\s]+?)(?:\.git)?$"
    $match = [System.Text.RegularExpressions.Regex]::Match(
        $normalizedSource,
        $githubUrlPattern,
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if (-not $match.Success) {
        $match = [System.Text.RegularExpressions.Regex]::Match(
            $normalizedSource,
            $githubShorthandPattern,
            [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
        )
    }

    if ($match.Success) {
        return ("github/{0}/{1}" -f $match.Groups[1].Value, $match.Groups[2].Value).ToLowerInvariant()
    }

    return $null
}

function Get-CanonicalSourceIdentity {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source
    )

    $repositoryIdentity = Get-CanonicalRepositoryIdentity $Source
    if ($null -ne $repositoryIdentity) {
        return "repository:$repositoryIdentity"
    }

    return "source:$(Normalize-GitSource $Source)"
}

function Get-DirectStringValues {
    param(
        [Parameter(Mandatory = $true)]
        [object]$JsonEntry,

        [Parameter(Mandatory = $true)]
        [string[]]$PropertyNames,

        [Parameter(Mandatory = $true)]
        [string]$FieldDescription
    )

    if ($null -eq $JsonEntry -or $JsonEntry -is [string] -or $JsonEntry.GetType().IsPrimitive) {
        throw "The marketplace entry is not an object. No registration was removed."
    }

    $values = [System.Collections.Generic.List[string]]::new()
    foreach ($propertyName in $PropertyNames) {
        $property = $JsonEntry.PSObject.Properties[$propertyName]
        if ($null -eq $property) {
            continue
        }

        if ($property.Value -isnot [string]) {
            throw "The marketplace $FieldDescription field '$propertyName' is not a string. No registration was removed."
        }
        $values.Add($property.Value)
    }
    return @($values)
}

function Find-DirectMarketplaceEntries {
    param(
        [Parameter(Mandatory = $true)]
        [object]$MarketplaceList,

        [Parameter(Mandatory = $true)]
        [string]$ExpectedMarketplaceName
    )

    if ($MarketplaceList -isnot [System.Array]) {
        throw "Marketplace list must be a JSON array. No registration was removed."
    }

    $matches = [System.Collections.Generic.List[object]]::new()
    foreach ($entry in @($MarketplaceList)) {
        if ($null -eq $entry -or $entry -is [string] -or $entry.GetType().IsPrimitive) {
            continue
        }

        $nameProperty = $entry.PSObject.Properties["name"]
        if ($null -ne $nameProperty -and $nameProperty.Value -is [string] -and $nameProperty.Value -ceq $ExpectedMarketplaceName) {
            $matches.Add($entry)
        }
    }

    return @($matches)
}

function Get-CanonicalRefValues {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$RefValues
    )

    $canonicalValues = [System.Collections.Generic.List[string]]::new()
    foreach ($refValue in $RefValues) {
        $canonicalRef = $refValue.Trim()
        if ($canonicalRef.StartsWith("refs/heads/", [System.StringComparison]::Ordinal)) {
            $canonicalRef = $canonicalRef.Substring("refs/heads/".Length)
        }
        $canonicalValues.Add($canonicalRef)
    }
    return @($canonicalValues)
}

function Get-SourceRefValues {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$SourceValues
    )

    $sourceRefs = [System.Collections.Generic.List[string]]::new()
    foreach ($sourceValue in $SourceValues) {
        $normalizedSource = $sourceValue.Trim()
        $fragmentIndex = $normalizedSource.IndexOf("#", [System.StringComparison]::Ordinal)
        if ($fragmentIndex -ge 0 -and $fragmentIndex -lt ($normalizedSource.Length - 1)) {
            $sourceRefs.Add($normalizedSource.Substring($fragmentIndex + 1))
            continue
        }

        if ($normalizedSource -notmatch "^[a-z]+://") {
            $atRefIndex = $normalizedSource.IndexOf("@", [System.StringComparison]::Ordinal)
            if ($atRefIndex -gt 0 -and $atRefIndex -lt ($normalizedSource.Length - 1)) {
                $sourceRefs.Add($normalizedSource.Substring($atRefIndex + 1))
            }
        }
    }
    return @($sourceRefs)
}

function Assert-NoConflictingValues {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$Values,

        [Parameter(Mandatory = $true)]
        [string]$FieldDescription
    )

    $uniqueValues = @($Values | Select-Object -Unique)
    if ($uniqueValues.Count -gt 1) {
        throw "The marketplace $FieldDescription values are ambiguous. No registration was removed."
    }
}

function Test-PublicMarketplaceSource {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$SourceValues,

        [Parameter(Mandatory = $true)]
        [string[]]$ExpectedSources
    )

    $sourceIdentities = @($SourceValues | ForEach-Object { Get-CanonicalSourceIdentity $_ })
    $expectedIdentities = @($ExpectedSources | ForEach-Object { Get-CanonicalSourceIdentity $_ })
    foreach ($sourceIdentity in $sourceIdentities) {
        if ($expectedIdentities -contains $sourceIdentity) {
            return $true
        }
    }
    return $false
}

function Get-MarketplaceRegistrationInspection {
    param(
        [Parameter(Mandatory = $true)]
        [object]$MarketplaceListState,

        [Parameter(Mandatory = $true)]
        [string]$HostName,

        [Parameter(Mandatory = $true)]
        [string[]]$ExpectedSources,

        [Parameter(Mandatory = $true)]
        [bool]$RequireReleaseRef
    )

    if ($MarketplaceListState -isnot [System.Array]) {
        throw "Could not interpret the $HostName marketplace list structure. No registration was removed."
    }

    $marketplaceEntries = @(Find-DirectMarketplaceEntries $MarketplaceListState $marketplaceName)
    if ($marketplaceEntries.Count -gt 1) {
        throw "The $HostName marketplace list contains multiple '$marketplaceName' entries. No registration was removed."
    }
    if ($marketplaceEntries.Count -eq 0) {
        return [pscustomobject]@{ State = "Missing"; Reason = "Marketplace registration was not listed." }
    }

    $marketplaceEntry = $marketplaceEntries[0]
    $sourceValues = @(
        Get-DirectStringValues $marketplaceEntry @("url", "repository", "repo", "gitUrl", "git_url", "path", "localPath", "local_path") "source"
    )
    $typeValues = @(
        Get-DirectStringValues $marketplaceEntry @("type", "sourceType", "source_type", "kind", "provider") "type"
    )
    foreach ($sourceFieldValue in @(Get-DirectStringValues $marketplaceEntry @("source") "source")) {
        if ($sourceFieldValue.Trim().ToLowerInvariant() -in @("github", "git", "url", "directory", "local", "path")) {
            $typeValues += $sourceFieldValue
        }
        else {
            $sourceValues += $sourceFieldValue
        }
    }
    $refValues = @(
        (Get-DirectStringValues $marketplaceEntry @("ref", "branch", "revision") "ref")
        (Get-SourceRefValues $sourceValues)
    )
    $hasSourceMetadata = $sourceValues.Count -gt 0
    $hasReleaseRefMetadata = $refValues.Count -gt 0
    $hasTypeMetadata = $typeValues.Count -gt 0
    $sourceIdentities = @($sourceValues | ForEach-Object { Get-CanonicalSourceIdentity $_ })
    $typeIdentities = @($typeValues | ForEach-Object { $_.Trim().ToLowerInvariant() })
    $refIdentities = @(Get-CanonicalRefValues $refValues)

    Assert-NoConflictingValues $sourceIdentities "source"
    Assert-NoConflictingValues $typeIdentities "type"
    Assert-NoConflictingValues $refIdentities "ref"
    $uniqueTypeIdentities = @($typeIdentities | Select-Object -Unique)
    $uniqueRefIdentities = @($refIdentities | Select-Object -Unique)

    if (-not $hasSourceMetadata) {
        throw "Could not verify the $HostName marketplace source from structured output. No registration was removed."
    }
    if (-not (Test-PublicMarketplaceSource $sourceValues $ExpectedSources)) {
        return [pscustomobject]@{ State = "Replace"; Reason = "The $HostName marketplace source or ref is stale or incompatible." }
    }
    if ($HostName -eq "Claude Code" -and ($uniqueTypeIdentities.Count -ne 1 -or @("github", "git", "url") -notcontains $uniqueTypeIdentities[0])) {
        return [pscustomobject]@{ State = "Replace"; Reason = "The Claude Code marketplace type is stale or incompatible." }
    }
    if ($RequireReleaseRef -and -not $hasReleaseRefMetadata) {
        throw "Could not verify the $HostName marketplace ref from structured output. No registration was removed."
    }
    if ($RequireReleaseRef -and ($uniqueRefIdentities.Count -ne 1 -or $uniqueRefIdentities[0] -ne $releaseRef)) {
        return [pscustomobject]@{ State = "Replace"; Reason = "The $HostName marketplace ref is stale or incompatible." }
    }

    return [pscustomobject]@{ State = "Reusable"; Reason = "The $HostName marketplace points to the expected public source and ref." }
}

function Refresh-MarketplaceRegistration {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HostCommand,

        [Parameter(Mandatory = $true)]
        [string]$HostName,

        [Parameter(Mandatory = $true)]
        [string[]]$RefreshArgs,

        [Parameter(Mandatory = $true)]
        [string[]]$RegisterArgs,

        [Parameter(Mandatory = $true)]
        [string[]]$RemoveArgs,

        [Parameter(Mandatory = $true)]
        [string[]]$ExpectedSources,

        [Parameter(Mandatory = $true)]
        [bool]$RequireReleaseRef
    )

    $listState = Get-MarketplaceListState $HostCommand $HostName
    $inspection = Get-MarketplaceRegistrationInspection $listState $HostName $ExpectedSources $RequireReleaseRef
    switch ($inspection.State) {
        "Missing" {
            Invoke-RequiredCommand $HostCommand $RegisterArgs "Register public $HostName marketplace"
            Invoke-RequiredCommand $HostCommand $RefreshArgs "Refresh newly registered $HostName marketplace"
        }
        "Reusable" {
            Invoke-RequiredCommand $HostCommand $RefreshArgs "Refresh existing $HostName marketplace"
        }
        "Replace" {
            Write-Host "$($inspection.Reason) Replacing it after the public ref preflight."
            Invoke-RequiredCommand $HostCommand $RemoveArgs "Remove stale $HostName marketplace"
            Invoke-RequiredCommand $HostCommand $RegisterArgs "Register public $HostName marketplace"
            Invoke-RequiredCommand $HostCommand $RefreshArgs "Refresh newly registered $HostName marketplace"
        }
        default {
            throw "Could not determine whether the $HostName marketplace registration is safe to reuse. No registration was removed."
        }
    }
}

function ConvertFrom-RequiredJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$JsonText,

        [Parameter(Mandatory = $true)]
        [string]$Step
    )

    try {
        return ,(ConvertFrom-Json -InputObject $JsonText -ErrorAction Stop)
    }
    catch {
        throw "$Step returned invalid JSON. $($_.Exception.Message)"
    }
}

function Test-ExactUserPluginInstallation {
    param(
        [Parameter(Mandatory = $true)]
        [object]$PluginState,

        [Parameter(Mandatory = $true)]
        [string]$ExpectedSelector
    )

    if ($null -eq $PluginState -or $PluginState -is [string] -or $PluginState.GetType().IsPrimitive) {
        return $false
    }

    if (($PluginState -is [System.Collections.IEnumerable]) -and ($PluginState -isnot [string])) {
        foreach ($pluginEntry in $PluginState) {
            if (Test-ExactUserPluginInstallation $pluginEntry $ExpectedSelector) {
                return $true
            }
        }
        return $false
    }

    $pluginProperties = $PluginState.PSObject.Properties
    if ($null -eq $pluginProperties) {
        return $false
    }

    $selectorPropertyNames = @("id", "selector", "plugin", "pluginId", "plugin_id", "name")
    $scopePropertyNames = @("scope", "installationScope", "installScope", "install_scope")
    $hasExpectedSelector = $false
    $hasUserScope = $false

    foreach ($property in $pluginProperties) {
        if (($selectorPropertyNames -contains $property.Name) -and ($property.Value -is [string]) -and ($property.Value -ceq $ExpectedSelector)) {
            $hasExpectedSelector = $true
        }
        if (($scopePropertyNames -contains $property.Name) -and ($property.Value -is [string]) -and ($property.Value -ieq "user")) {
            $hasUserScope = $true
        }
    }

    if ($hasExpectedSelector -and $hasUserScope) {
        return $true
    }

    foreach ($property in $pluginProperties) {
        if (Test-ExactUserPluginInstallation $property.Value $ExpectedSelector) {
            return $true
        }
    }

    return $false
}

function Update-ClaudePlugin {
    $pluginListJson = Invoke-RequiredCommand claude @("plugin", "list", "--json") "Read Claude Code plugin state"
    $pluginState = ConvertFrom-RequiredJson $pluginListJson "Claude Code plugin list"
    if (Test-ExactUserPluginInstallation $pluginState $pluginSelector) {
        Invoke-RequiredCommand claude @(
            "plugin", "update", $pluginSelector, "--scope", "user"
        ) "Update Claude Code plugin"
        return
    }

    Invoke-RequiredCommand claude @(
        "plugin", "install", $pluginSelector, "--scope", "user", "-y"
    ) "Install missing Claude Code plugin"
    Write-Host "The Claude Code plugin was not installed; it was installed now."
}

function Assert-ReleaseCheckout {
    Invoke-RequiredCommand git @("-C", $repoRoot, "check-ref-format", "--branch", $releaseRef) "Validate requested branch"
    $currentBranch = Get-CommandOutput git @("-C", $repoRoot, "branch", "--show-current") "Read current branch"
    if ($currentBranch -ne $releaseRef) {
        throw "Release must run from the requested branch '$releaseRef'; current branch is '$currentBranch'."
    }

    $dirtyFiles = Get-CommandOutput git @("-C", $repoRoot, "status", "--porcelain") "Read worktree status"
    if ($dirtyFiles) {
        throw "Release requires a clean worktree.`n$dirtyFiles"
    }

    Assert-PublicOrigin
    Invoke-RequiredCommand git @("-C", $repoRoot, "fetch", "origin", $releaseRef, "--quiet") "Refresh origin/$releaseRef"
    $localCommit = Get-CommandOutput git @("-C", $repoRoot, "rev-parse", $releaseRef) "Read local $releaseRef commit"
    $remoteCommit = Get-CommandOutput git @("-C", $repoRoot, "rev-parse", "origin/$releaseRef") "Read origin/$releaseRef commit"
    if ($localCommit -ne $remoteCommit) {
        throw "Local '$releaseRef' and 'origin/$releaseRef' are not at the same commit."
    }
}

function Assert-PublicMarketplaceRef {
    Invoke-RequiredCommand git @(
        "ls-remote", "--exit-code", $publicMarketplaceSource, "refs/heads/$releaseRef"
    ) "Validate public marketplace $releaseRef ref"
}

function Refresh-CodexMarketplace {
    Refresh-MarketplaceRegistration "codex" "Codex" @(
        "plugin", "marketplace", "upgrade", $marketplaceName
    ) @(
        "plugin", "marketplace", "add", $codexMarketplaceSource,
        "--ref", $releaseRef
    ) @(
        "plugin", "marketplace", "remove", $marketplaceName
    ) @($publicMarketplaceSource, $codexMarketplaceSource) $true
    Invoke-RequiredCommand codex @("plugin", "add", $pluginSelector) "Update Codex plugin"
}

function Refresh-ClaudeMarketplace {
    Refresh-MarketplaceRegistration "claude" "Claude Code" @(
        "plugin", "marketplace", "update", $marketplaceName
    ) @(
        "plugin", "marketplace", "add", "$publicMarketplaceSource#$releaseRef",
        "--scope", "user"
    ) @(
        "plugin", "marketplace", "remove", $marketplaceName, "--scope", "user"
    ) @($publicMarketplaceSource, "$publicMarketplaceSource#$releaseRef") $true
    Update-ClaudePlugin
}

try {
    foreach ($requiredCommand in @("git", "python", "codex", "claude")) {
        if (-not (Get-Command $requiredCommand -ErrorAction SilentlyContinue)) {
            throw "$requiredCommand command was not found."
        }
    }

    Assert-ReleaseCheckout

    if (-not (Test-Path -LiteralPath $validatorScript -PathType Leaf)) {
        throw "Plugin validator not found: $validatorScript"
    }

    Invoke-RequiredCommand python @($validatorScript, $repoRoot) "Validate plugin"
    Assert-PublicMarketplaceRef
    Refresh-CodexMarketplace
    Refresh-ClaudeMarketplace
    Write-Host "Released $pluginSelector from $publicMarketplaceSource at $releaseRef. Start a new thread or restart the host to load the update."
}
catch {
    Write-Error $_
    exit 1
}
