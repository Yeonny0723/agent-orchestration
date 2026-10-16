param([Parameter(Mandatory = $true)][string]$Case)

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot "../scripts/redeploy-plugin.ps1"
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw $parseErrors[0] }
# Load functions without running the release entrypoint.
foreach ($definition in $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)) {
    . ([scriptblock]::Create($definition.Extent.Text))
}

$marketplaceName = "agent-orchestration-marketplace"
$publicMarketplaceSource = "https://github.com/Yeonny0723/agent-orchestration.git"
$codexMarketplaceSource = "Yeonny0723/agent-orchestration"
$releaseRef = "master"
$pluginSelector = "agent-orchestration@$marketplaceName"
$script:commands = [System.Collections.Generic.List[string]]::new()
$script:cliExitCode = 0
function Test-Cli {
    $global:LASTEXITCODE = $script:cliExitCode
    $script:cliJson
}
function Invoke-RequiredCommand {
    param($FilePath, $CommandArgs, $Step)
    $script:commands.Add(($CommandArgs -join " "))
}
function Assert-Equal($Expected, $Actual) {
    if ($Expected -cne $Actual) { throw "Expected '$Expected', got '$Actual'." }
}

$hostName = "Codex"
$expectedCommands = @("plugin marketplace upgrade $marketplaceName")
$expectedError = $null
switch ($Case) {
    "codex_wrapped_without_ref" {
        $script:cliJson = '{"marketplaces":[{"name":"agent-orchestration-marketplace","root":"C:/cache/marketplace","marketplaceSource":{"sourceType":"git","source":"https://github.com/Yeonny0723/agent-orchestration.git"}}]}'
        $expectedCommands = @("plugin marketplace remove $marketplaceName", "plugin marketplace add $codexMarketplaceSource --ref master", "plugin marketplace upgrade $marketplaceName")
    }
    "codex_wrapped_matching_ref" {
        $script:cliJson = '{"marketplaces":[{"name":"agent-orchestration-marketplace","marketplaceSource":{"sourceType":"git","source":"https://github.com/Yeonny0723/agent-orchestration.git","ref":"master"}}]}'
    }
    "codex_wrapped_stale_ref" {
        $script:cliJson = '{"marketplaces":[{"name":"agent-orchestration-marketplace","marketplaceSource":{"sourceType":"git","source":"https://github.com/Yeonny0723/agent-orchestration.git","ref":"feature/old"}}]}'
        $expectedCommands = @("plugin marketplace remove $marketplaceName", "plugin marketplace add $codexMarketplaceSource --ref master", "plugin marketplace upgrade $marketplaceName")
    }
    "claude_single_entry_array" {
        $hostName = "Claude Code"
        $script:cliJson = '[{"name":"agent-orchestration-marketplace","source":"git","url":"https://github.com/Yeonny0723/agent-orchestration.git","ref":"master"}]'
    }
    "codex_empty_wrapper" {
        $script:cliJson = '{"marketplaces":[]}'
        $expectedCommands = @("plugin marketplace add $codexMarketplaceSource --ref master", "plugin marketplace upgrade $marketplaceName")
    }
    "claude_empty_array" {
        $hostName = "Claude Code"
        $script:cliJson = '[]'
        $expectedCommands = @("plugin marketplace add $codexMarketplaceSource --ref master", "plugin marketplace upgrade $marketplaceName")
    }
    "malformed_wrapper" {
        $script:cliJson = '{"marketplaces":{}}'
        $expectedError = "*JSON array*"
    }
    "missing_source" {
        $script:cliJson = '{"marketplaces":[{"name":"agent-orchestration-marketplace","root":"C:/cache/marketplace"}]}'
        $expectedError = "*Could not verify*source*"
    }
    "conflicting_sources" {
        $script:cliJson = '{"marketplaces":[{"name":"agent-orchestration-marketplace","url":"https://github.com/another/repo","marketplaceSource":{"sourceType":"git","source":"https://github.com/Yeonny0723/agent-orchestration.git"}}]}'
        $expectedError = "*source values are ambiguous*"
    }
    "malformed_nested_source" {
        $script:cliJson = '{"marketplaces":[{"name":"agent-orchestration-marketplace","marketplaceSource":"invalid"}]}'
        $expectedError = "*marketplace*not an object*"
    }
    "legacy_missing_ref" {
        $script:cliJson = '[{"name":"agent-orchestration-marketplace","url":"https://github.com/Yeonny0723/agent-orchestration.git"}]'
        $expectedError = "*Could not verify*ref*"
    }
    "network_failure" {
        $script:cliJson = 'ERROR: authentication failed'
        $script:cliExitCode = 1
        $expectedError = "*network or authentication error*"
    }
    default { throw "Unknown test case: $Case" }
}

$caughtError = $null
try {
    Refresh-MarketplaceRegistration "Test-Cli" $hostName @("plugin", "marketplace", "upgrade", $marketplaceName) @(
        "plugin", "marketplace", "add", $codexMarketplaceSource, "--ref", $releaseRef
    ) @("plugin", "marketplace", "remove", $marketplaceName) @($publicMarketplaceSource) $true
}
catch { $caughtError = $_.Exception.Message }

if ($expectedError) {
    if (-not $caughtError -or $caughtError -notlike $expectedError) {
        throw "Expected error '$expectedError', got '$caughtError'."
    }
    Assert-Equal 0 $script:commands.Count
}
else {
    if ($caughtError) { throw $caughtError }
    Assert-Equal ($expectedCommands -join "`n") ($script:commands -join "`n")
}
