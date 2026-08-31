# Remote Marketplace Master Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish any requested, already-pushed branch through the public GitHub marketplace so Codex and Claude Code users can install and update the plugin without cloning the repository, while keeping the branch-aware release script versioned for maintainers.

**Architecture:** The GitHub repository is the remote marketplace source for both hosts. A versioned PowerShell script accepts a branch, validates the checked-out branch against its matching `origin/<branch>` ref, validates the plugin, and refreshes the maintainer's Codex and Claude Code marketplace installations from that branch. User-facing installation and update commands live in `README.md`; maintainer release instructions live in tracked `scripts/README.md`.

**Tech Stack:** PowerShell, Codex plugin CLI, Claude Code plugin CLI, Python `unittest`, GitHub Git remote, JSON marketplace/plugin manifests.

---

## File Map

- Modify: `README.md` — public GitHub marketplace installation and update commands.
- Create: `scripts/README.md` — maintainer-only, branch-aware release procedure.
- Modify: `scripts/redeploy-plugin.ps1` — branch-aware release/refresh script committed separately from the documentation.
- Modify: `tests/test_contracts.py` — contract tests for public source and release policy.
- Create: `docs/superpowers/plans/2026-08-28-remote-marketplace-master-release.md` — this plan.

### Task 1: Add failing documentation contract tests

**Files:**
- Modify: `tests/test_contracts.py`

- [ ] **Step 1: Add the public marketplace contract tests.**

Add this class after the existing acceptance contract tests:

~~~python
class MarketplaceReleaseContractTests(unittest.TestCase):
    def test_readme_uses_public_marketplace_source(self):
        text = read("README.md")
        self.assertIn("https://github.com/Yeonny0723/agent-orchestration.git", text)
        self.assertIn("Yeonny0723/agent-orchestration", text)
        self.assertNotIn("C:\\Users\\<사용자>", text)
        self.assertNotIn("orca\\projects\\agent-orchestration", text)

    def test_release_instructions_accept_a_requested_branch(self):
        text = read("scripts/README.md")
        self.assertIn("-Branch", text)
        self.assertIn("origin/<branch>", text)
        self.assertIn("redeploy-plugin.ps1", text)

    def test_release_script_is_tracked(self):
        self.assertTrue((ROOT / "scripts/redeploy-plugin.ps1").is_file())

    def test_user_updates_do_not_require_clone_or_pull(self):
        text = read("README.md")
        self.assertIn("codex plugin marketplace upgrade", text)
        self.assertIn("claude plugin marketplace update", text)
        self.assertNotIn("git clone", text)
        self.assertNotIn("git pull", text)
~~~

- [ ] **Step 2: Run the focused tests and verify the new contract fails.**

Run:

~~~powershell
python -m unittest tests.test_contracts.MarketplaceReleaseContractTests -v
~~~

Expected: FAIL because `scripts/README.md` does not exist and `README.md` still documents local paths.

### Task 2: Document public installation and maintainer release

**Files:**
- Modify: `README.md`
- Create: `scripts/README.md`

- [ ] **Step 1: Replace local installation instructions in `README.md`.**

Replace the current local-path commands with this public-source flow while retaining the dependency section:

~~~markdown
## 설치와 업데이트

공개 GitHub marketplace에서 설치하므로 사용자는 이 저장소를 clone하거나 pull할 필요가 없습니다. 기본 배포 브랜치는 `master`이며 다른 브랜치도 ref로 지정할 수 있습니다.

Claude Code:

~~~powershell
claude plugin marketplace add "https://github.com/Yeonny0723/agent-orchestration.git#master" --scope user
claude plugin install agent-orchestration@agent-orchestration-marketplace --scope user
~~~

Codex:

~~~powershell
codex plugin marketplace add Yeonny0723/agent-orchestration --ref master
codex plugin add agent-orchestration@agent-orchestration-marketplace
~~~

업데이트:

~~~powershell
claude plugin marketplace update agent-orchestration-marketplace
claude plugin update agent-orchestration@agent-orchestration-marketplace --scope user

codex plugin marketplace upgrade agent-orchestration-marketplace
codex plugin add agent-orchestration@agent-orchestration-marketplace
~~~

업데이트한 skill을 적용하려면 Codex 새 스레드 또는 Claude Code 재시작이 필요할 수 있습니다.
~~~

- [ ] **Step 2: Create `scripts/README.md` with the maintainer-only release contract.**

Include:

~~~markdown
# Maintainer release

`redeploy-plugin.ps1`는 저장소에 포함된 관리자용 배포 스크립트입니다. 지정한 원격 브랜치에 push된 내용을 Codex·Claude Code marketplace에서 다시 읽도록 갱신합니다.

## 릴리즈 절차

1. 배포할 브랜치를 원격에 push합니다.
2. 해당 브랜치의 깨끗한 worktree에서 실행합니다.

~~~powershell
.\scripts\redeploy-plugin.ps1 -Branch feature/review-comment
~~~

`-Branch`를 생략하면 `master`를 사용합니다. 스크립트는 현재 branch가 요청한 branch인지, 작업 트리가 깨끗한지, local branch가 `origin/<branch>`와 같은 commit인지, plugin validator가 통과하는지 확인합니다. 조건을 만족하지 않으면 Codex·Claude Code marketplace를 변경하지 않고 중단합니다.

## 배포 대상 변경

공식 기본 배포 대상은 `master`입니다. 다른 branch를 배포하려면 `-Branch`와 사용자의 marketplace 설치 ref를 같은 값으로 맞춥니다. Codex는 `--ref <branch>`, Claude Code는 Git URL 뒤에 `#<branch>`를 사용합니다.

## 운영 권한

실제 merge·push 권한은 Git hosting의 branch protection과 관리자 credential로 제한합니다. 스크립트는 요청한 branch, 원격 동기화 상태와 plugin 유효성을 확인한 뒤에만 marketplace를 갱신합니다.
~~~
~~~

- [ ] **Step 3: Run the focused documentation tests.**

~~~powershell
python -m unittest tests.test_contracts.MarketplaceReleaseContractTests -v
~~~

Expected: PASS.

### Task 3: Make the versioned release script branch-aware and remote-source based

**Files:**
- Modify: `scripts/redeploy-plugin.ps1` (stage and commit separately from documentation)

- [ ] **Step 1: Set public source and release constants.**

Keep `$ErrorActionPreference = "Stop"` and replace local marketplace constants with:

~~~powershell
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$validatorScript = Join-Path $repoRoot "scripts\validate_plugin.py"
$publicMarketplaceSource = "https://github.com/Yeonny0723/agent-orchestration.git"
$codexMarketplaceSource = "Yeonny0723/agent-orchestration"
$releaseRef = "master"
$marketplaceName = "agent-orchestration-marketplace"
$pluginSelector = "agent-orchestration@$marketplaceName"
~~~

Do not retain a call to `update_plugin_cachebuster.py` for the remote release path.

- [ ] **Step 2: Add the master and remote synchronization guard.**

Before any marketplace command, check the current branch, worktree, and remote commit:

~~~powershell
function Get-CommandOutput {
    param(
        [Parameter(Mandatory = $true)] [string]$FilePath,
        [Parameter(Mandatory = $true)] [string[]]$CommandArgs,
        [Parameter(Mandatory = $true)] [string]$Step
    )

    $output = & $FilePath @CommandArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE.`n$output"
    }
    return (($output -join "`n").Trim())
}

function Assert-ReleaseCheckout {
    $currentBranch = Get-CommandOutput git @("-C", $repoRoot, "branch", "--show-current") "Read current branch"
    if ($currentBranch -ne $releaseRef) {
        throw "Release must run from '$releaseRef'; current branch is '$currentBranch'."
    }

    $dirtyFiles = & git -C $repoRoot status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "Read worktree status failed with exit code $LASTEXITCODE."
    }
    if ($dirtyFiles) {
        throw "Release requires a clean worktree.`n$($dirtyFiles -join "`n")"
    }

    Invoke-RequiredCommand git @("-C", $repoRoot, "fetch", "origin", $releaseRef, "--quiet") "Refresh origin/$releaseRef"
    $localCommit = Get-CommandOutput git @("-C", $repoRoot, "rev-parse", $releaseRef) "Read local $releaseRef commit"
    $remoteCommit = Get-CommandOutput git @("-C", $repoRoot, "rev-parse", "origin/$releaseRef") "Read origin/$releaseRef commit"
    if ($localCommit -ne $remoteCommit) {
        throw "Local '$releaseRef' and 'origin/$releaseRef' are not at the same commit."
    }
}
~~~

The guard must run before validation or marketplace mutation, so a branch mismatch, dirty tree, or stale remote ref cannot change a marketplace.

- [ ] **Step 3: Replace local registration with remote Codex and Claude refresh functions.**

Remove `Ensure-LocalMarketplace`. Add host-specific functions that never pass `$repoRoot` as a marketplace source:

~~~powershell
function Refresh-CodexMarketplace {
    & codex plugin marketplace remove $marketplaceName 2>&1 | Out-Host
    Invoke-RequiredCommand codex @(
        "plugin", "marketplace", "add", $codexMarketplaceSource,
        "--ref", $releaseRef
    ) "Register public Codex marketplace"
    Invoke-RequiredCommand codex @("plugin", "marketplace", "upgrade", $marketplaceName) "Refresh Codex marketplace"
    Invoke-RequiredCommand codex @("plugin", "add", $pluginSelector) "Update Codex plugin"
}

function Refresh-ClaudeMarketplace {
    & claude plugin marketplace remove $marketplaceName --scope user 2>&1 | Out-Host
    Invoke-RequiredCommand claude @(
        "plugin", "marketplace", "add", $publicMarketplaceSource,
        "--scope", "user"
    ) "Register public Claude marketplace"
    Invoke-RequiredCommand claude @(
        "plugin", "marketplace", "update", $marketplaceName
    ) "Refresh Claude marketplace"
    Invoke-RequiredCommand claude @(
        "plugin", "update", $pluginSelector, "--scope", "user"
    ) "Update Claude plugin"
}
~~~

If an update command reports that the plugin is not installed, call the corresponding install command once with its supported non-interactive confirmation option and report that it installed. Do not silently skip a missing host or CLI.

- [ ] **Step 4: Remove the cachebuster mutation from the remote release path.**

The existing `update_plugin_cachebuster.py` helper rewrites a local Codex manifest. It must not publish a temporary version to the public marketplace. Remove the current manifest snapshot/restoration block unless a host command specifically needs a temporary local mutation.

- [ ] **Step 5: Add the final release entrypoint.**

The executable flow must be:

~~~powershell
Assert-ReleaseCheckout
Invoke-RequiredCommand python @($validatorScript, $repoRoot) "Validate plugin"
Refresh-CodexMarketplace
Refresh-ClaudeMarketplace
Write-Host "Released $pluginSelector from $publicMarketplaceSource at $releaseRef. Start a new thread or restart the host to load the update."
~~~

Any exception must exit non-zero. Do not convert a failed host update into a success message.

### Task 4: Verify without releasing before the requested branch is synchronized

**Files:**
- Test: `tests/test_contracts.py`
- Check: `scripts/redeploy-plugin.ps1`, `README.md`, `scripts/README.md`

- [ ] **Step 1: Run focused tests and the validator.**

~~~powershell
python -m unittest tests.test_contracts.MarketplaceReleaseContractTests tests.test_validate_plugin -v
~~~

Expected: PASS.

- [ ] **Step 2: Run the full Python suite.**

~~~powershell
python -m unittest discover -s tests -v
~~~

Expected: PASS.

- [ ] **Step 3: Check the feature-branch guard safely.**

Invoke the local script with a requested branch that does not match the checkout or remote synchronization state. Expected: it exits with an error containing `requested branch` and does not invoke either marketplace command.

- [ ] **Step 4: Run the real release only after merging to `master`.**

From a clean, synchronized worktree for the requested branch, run:

~~~powershell
.\scripts\redeploy-plugin.ps1
~~~

Expected: validation passes, the public GitHub source is used, both host marketplaces are refreshed, and the restart/new-thread notice is printed.

- [ ] **Step 5: Confirm tracked-file and diff boundaries.**

~~~powershell
git diff --check
git status --short -- scripts/redeploy-plugin.ps1
~~~

Expected: no whitespace errors; `scripts/redeploy-plugin.ps1` is the only staged script in its separate commit; unrelated user changes are not staged.

### Task 5: Commit documentation and the release script separately

**Files:**
- Commit: `README.md`
- Commit: `scripts/README.md`
- Commit: `tests/test_contracts.py`
- Commit separately: `scripts/redeploy-plugin.ps1`
- Exclude: pre-existing unrelated user changes

- [ ] **Step 1: Stage only approved tracked files.**

~~~powershell
git add -- README.md scripts/README.md tests/test_contracts.py
git diff --cached --check
git diff --cached --stat
~~~

- [ ] **Step 2: Commit the tracked documentation and contract changes.**

~~~powershell
git commit -m "feat: branch-aware remote marketplace release"
~~~

- [ ] **Step 3: Confirm the commit boundary.**

~~~powershell
git status --short
git show --stat --oneline --summary HEAD
~~~

Expected: the first commit contains only public installation docs, maintainer release docs, and contract tests; the second commit contains only `scripts/redeploy-plugin.ps1`.
