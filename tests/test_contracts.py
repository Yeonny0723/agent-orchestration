import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}")
    end = text.find("\n## ", start + len(heading) + 3)
    return text[start:] if end < 0 else text[start:end]


class WorkflowContractTests(unittest.TestCase):
    def test_scale_cases_cover_all_sizes(self):
        cases = json.loads(read("tests/fixtures/work-scale-cases.json"))
        self.assertEqual({"small", "medium", "large"}, {case["expected"] for case in cases})

    def test_workflow_has_required_order(self):
        text = read("skills/orchestrate-work/references/workflow.md")
        headings = [
            "규모 판정",
            "범위 탐색",
            "의사결정",
            "spec 승인",
            "계획 기술 합의",
            "TDD 기반 구현",
            "테스트 민감도",
            "선택형 작업 이해",
            "PR 작성",
        ]
        positions = [text.index(f"## {heading}") for heading in headings]
        self.assertEqual(sorted(positions), positions)

    def test_invocation_contracts_are_distinct_and_git_command_ready(self):
        text = read("skills/orchestrate-work/references/invocation-contracts.md")
        for skill in ("implement-with-tdd", "verify-test-sensitivity", "understand-work", "write-pr"):
            self.assertEqual(1, len(re.findall(rf"^## `{skill}`$", text, re.MULTILINE)))
        self.assertIn("1:1", text)
        self.assertIn("업무 로직을 포함하지 않는다", text)
        for command in ("git:commit", "git:issue", "git:comment", "git:pr"):
            self.assertIn(command, text)


class SkillContractTests(unittest.TestCase):
    def assert_pr_authoring_prerequisites(self, skill: str):
        authoring = section(skill, "작성과 provider 감지")
        author = authoring.index("`author-reviewable-text`")
        prerequisites = (
            "GitHub, host가 GitLab이거나 `glab repo view`만 성공하면 GitLab으로 판정한다",
            "필요한 `gh` 또는 `glab` CLI와 인증 상태를 확인",
            "provider를 감지할 수 없거나 둘 다 성공하면 외부 생성은 중단하고 사용자에게 확인한다",
        )
        for prerequisite in prerequisites:
            self.assertLess(authoring.index(prerequisite), author, prerequisite)

    def assert_plan_consensus_precedes_authoring(self, skill: str):
        plan = section(skill, "plan 작성")
        consensus = plan.index("계획 기술 합의가 끝나면")
        author = plan.index("`author-reviewable-text`")
        self.assertLess(consensus, author)

    def test_required_skills_have_metadata(self):
        required = {
            "setup-orchestration",
            "orchestrate-work",
            "capture-authoring-voice",
            "author-reviewable-text",
            "decision-first-grill",
            "apply-conventions",
            "implement-with-tdd",
            "verify-test-sensitivity",
            "understand-work",
            "commit-changes",
            "write-issue",
            "post-git-comment",
            "write-pr",
        }
        self.assertEqual(required, {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")})
        for name in required:
            skill = read(f"skills/{name}/SKILL.md")
            metadata = read(f"skills/{name}/agents/openai.yaml")
            self.assertRegex(skill, rf"(?m)^name: {re.escape(name)}$")
            self.assertRegex(skill, r"(?m)^description: .+$")
            for key in ("display_name", "short_description", "default_prompt"):
                self.assertRegex(metadata, rf"(?m)^\s*{key}: .+$")

    def test_author_reviewable_text_preserves_content_contract(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        for phrase in (
            "최종 초안을 한 번",
            "stop-slop",
            "humanizer",
            "선택형",
            "차단하지 않는다",
            "사용자의 명시적 지시",
            "필수 형식",
            "확인된 사실",
        ):
            self.assertIn(phrase, skill)

    def test_author_reviewable_text_resolves_optional_inputs_without_blocking(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        input_contract = skill[skill.index("## 입력 계약"):skill.index("## 적용 범위")]
        self.assertNotIn("voice profile", input_contract)
        primary = skill.index("$AGENT_ORCHESTRATION_HOME/voice-profile.md")
        fallback = skill.index("~/.agent-orchestration/voice-profile.md")
        self.assertLess(primary, fallback)
        for phrase in (
            "직접 확인",
            "환경 변수가 설정되어 있으면",
            "환경 변수가 없을 때만",
            "정확한 skill 이름",
            "실패 원인",
            "호출자에게 보고",
            "작성을 차단하지 않는다",
        ):
            self.assertIn(phrase, skill)

    def test_author_reviewable_text_expands_required_format_priority(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        priority = skill[skill.index("## 우선순위"):skill.index("## 작성 절차")]
        self.assertRegex(
            priority,
            r"(?m)^2\. 템플릿, 필수 절 또는 내용, 길이 제한을 포함한 산출물의 필수 형식$",
        )

    def test_author_reviewable_text_gathers_rules_before_single_draft(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        workflow = skill[skill.index("## 작성 절차"):skill.index("## 결과")]
        gather_phrase = "작성 규칙을 먼저 수집"
        draft_phrase = "수집한 모든 규칙을 사용해"
        self.assertIn(gather_phrase, workflow)
        self.assertIn(draft_phrase, workflow)
        gather = workflow.index(gather_phrase)
        draft = workflow.index(draft_phrase)
        self.assertLess(gather, draft)
        self.assertIn("최종 초안을 한 번 작성", workflow)
        self.assertIn("작업 중인 초안을 순차적으로 다시 쓰거나 다듬지 않는다", workflow)
        for forbidden in ("작업 중인 문안을 다듬는다", "그 결과의 군더더기를 줄인다"):
            self.assertNotIn(forbidden, workflow)

    def test_author_reviewable_text_invokes_installed_skills_before_drafting(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        workflow = skill[skill.index("## 작성 절차"):skill.index("## 결과")]
        stages = ("### 입력 확인", "### 선택 skill 호출", "### 초안 작성", "### 반환")
        for stage in stages:
            self.assertIn(stage, workflow)
        positions = [workflow.index(stage) for stage in stages]
        self.assertEqual(sorted(positions), positions)

        optional = workflow[positions[1]:positions[2]]
        for name in ("humanizer", "stop-slop"):
            heading = f"#### `{name}`"
            self.assertIn(heading, optional)
            start = optional.index(heading)
            end = optional.find("#### ", start + len(heading))
            subsection = optional[start:] if end < 0 else optional[start:end]
            for phrase in ("설치", "호출", "확인된 사실", "필수 형식", "전달"):
                self.assertIn(phrase, subsection, name)

    def test_author_reviewable_text_keeps_failures_and_missing_input_outside_draft(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        workflow = skill[skill.index("## 작성 절차"):skill.index("## 결과")]
        for stage in ("### 입력 확인", "### 선택 skill 호출", "### 초안 작성"):
            self.assertIn(stage, workflow)
        input_check = workflow[workflow.index("### 입력 확인"):workflow.index("### 선택 skill 호출")]
        for phrase in ("누락된 입력 목록", "초안을 작성하지", "사용자에게 직접 묻지", "호출자에게 반환"):
            self.assertIn(phrase, input_check)

        optional = workflow[workflow.index("### 선택 skill 호출"):workflow.index("### 초안 작성")]
        for phrase in (
            "설치되지 않",
            "조용히 계속",
            "설치된 skill",
            "호출하거나 읽을 수 없",
            "정확한 skill 이름",
            "실패 원인",
            "별도로 반환",
            "초안에 포함하지",
            "작성을 계속",
        ):
            self.assertIn(phrase, optional)

    def test_author_reviewable_text_preserves_literals_and_length(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        for phrase in (
            "길이 제한",
            "필수 절",
            "숫자",
            "파일명",
            "명령어",
            "선택지",
            "차이",
            "판단 기준",
            "인용문",
            "사용자가 제공한 인용문은 다시 쓰지 않는다",
        ):
            self.assertIn(phrase, skill)

    def test_author_reviewable_text_keeps_caller_ownership_and_narrow_scope(self):
        skill = read("skills/author-reviewable-text/SKILL.md")
        for phrase in (
            "호출자에게 반환",
            "호출자가 승인",
            "외부 쓰기",
            "일반적인 선택형 질문",
            "`understand-work` 질문",
        ):
            self.assertIn(phrase, skill)

    def test_decision_first_spec_contract(self):
        skill = read("skills/decision-first-grill/SKILL.md")
        for phrase in ("전수 목록화", "한 번에 한 질문", "선택지", "트레이드오프", "추천안", "spec 작성 금지"):
            self.assertIn(phrase, skill)
        self.assertIn("grill-with-docs", skill)
        self.assertIn("domain-modeling", skill)
        template = read("templates/spec.md")
        for heading in ("문제", "목적", "현재 구조와 제약", "결정", "비목표", "완료 기준"):
            self.assertIn(f"## {heading}", template)

    def test_tdd_entrypoint_delegates_without_crossing_boundaries(self):
        text = read("skills/implement-with-tdd/SKILL.md")
        self.assertIn("superpowers:test-driven-development", text)
        self.assertIn("사용자 직접 호출", text)
        self.assertIn("orchestrate-work", text)
        self.assertIn("verify-test-sensitivity", text)
        for forbidden in ("mutation을 직접 수행", "PR을 생성한다", "이해 질문을 생성한다"):
            self.assertNotIn(forbidden, text)

    def test_sensitivity_skill_requires_exact_restore(self):
        text = read("skills/verify-test-sensitivity/SKILL.md")
        for phrase in ("byte snapshot", "SHA-256", "killed", "survived", "hash", "복원"):
            self.assertIn(phrase, text)
        self.assertIn("사용자 직접 호출", text)

    def test_understanding_is_manual_chat_only_and_capped(self):
        text = read("skills/understand-work/SKILL.md")
        for phrase in ("사용자 명시적 호출", "최대 5", "한 번에 하나", "현재 대화", "PR을 차단하지 않는다"):
            self.assertIn(phrase, text)
        for axis in ("사양 설명", "구조와 실행 흐름", "핵심 결정과 제약", "문제 진단과 변경 위치", "검증과 영향 범위"):
            self.assertIn(axis, text)

    def test_pr_skill_is_manual_host_neutral_and_evidence_based(self):
        text = read("skills/write-pr/SKILL.md")
        for phrase in ("사용자가 직접 호출", "승인된 spec", "실제 diff", "일반 검증", "verify-test-sensitivity", "사용자 승인"):
            self.assertIn(phrase, text)
        self.assertIn("특정 호스트", text)
        self.assertIn("understand-work 실행 여부와 무관", text)

    def test_pr_detects_provider_before_authoring_and_keeps_write_order(self):
        skill = read("skills/write-pr/SKILL.md")
        authoring = section(skill, "작성과 provider 감지")
        approval = section(skill, "승인과 생성")

        provider = authoring.index("git remote get-url origin")
        author = authoring.index("`author-reviewable-text`")
        returned_draft = authoring.index("반환된 한국어 제목과 본문 최종 초안")
        approval_gate = approval.index("사용자 승인을 받는다")
        external_write = approval.index("git push -u origin HEAD")
        self.assertLess(provider, author)
        self.assert_pr_authoring_prerequisites(skill)
        self.assertLess(author, returned_draft)
        self.assertLess(approval_gate, external_write)
        self.assertLess(skill.index("반환된 한국어 제목과 본문 최종 초안"), skill.index("## 승인과 생성"))

        for phrase in ("provider의 길이 제한", "target branch 등 사용자 옵션"):
            self.assertIn(phrase, authoring)
        for phrase in ("사용자 승인을 받는다", "승인 전에는", "git push -u origin HEAD"):
            self.assertIn(phrase, approval)

    def test_pr_authoring_order_assertions_reject_each_weakened_prerequisite(self):
        skill = read("skills/write-pr/SKILL.md")
        author = "`author-reviewable-text`"
        prerequisites = (
            "GitHub, host가 GitLab이거나 `glab repo view`만 성공하면 GitLab으로 판정한다",
            "필요한 `gh` 또는 `glab` CLI와 인증 상태를 확인",
            "provider를 감지할 수 없거나 둘 다 성공하면 외부 생성은 중단하고 사용자에게 확인한다",
        )
        without_author = skill.replace(author, "author-reviewable-text", 1)
        for prerequisite in prerequisites:
            with self.subTest(prerequisite=prerequisite):
                weakened = without_author.replace(prerequisite, f"{author} {prerequisite}", 1)
                with self.assertRaises(AssertionError):
                    self.assert_pr_authoring_prerequisites(weakened)

    def test_orchestrate_plan_authoring_passes_only_confirmed_technology_decisions(self):
        skill = read("skills/orchestrate-work/SKILL.md")
        plan = section(skill, "plan 작성")
        self.assert_plan_consensus_precedes_authoring(skill)
        self.assertIn("승인된 spec과 확정된 기술 결정인 확인된 사실", plan)
        self.assertIn("확정된 기술 결정만 전달", plan)
        self.assertIn("일반적인 기술 선택을 추가하거나 대안이나 새로운 선택지를 다시 열지 않는다", plan)
        self.assertNotIn("길이 제한과 기술 선택지를 전달", plan)

    def test_orchestrate_plan_order_assertion_rejects_authoring_before_consensus(self):
        skill = read("skills/orchestrate-work/SKILL.md")
        author = "`author-reviewable-text`"
        consensus = "계획 기술 합의가 끝나면"
        weakened = skill.replace(author, "author-reviewable-text", 1).replace(
            consensus,
            f"{author} {consensus}",
            1,
        )
        with self.assertRaises(AssertionError):
            self.assert_plan_consensus_precedes_authoring(weakened)

    def test_git_commands_delegate_one_to_one_without_business_logic(self):
        commands = {
            "git/commit.md": "commit-changes",
            "git/issue.md": "write-issue",
            "git/comment.md": "post-git-comment",
            "git/pr.md": "write-pr",
        }
        actual = {
            path.relative_to(ROOT / "commands").as_posix()
            for path in (ROOT / "commands").rglob("*.md")
        }
        self.assertEqual(set(commands), actual)
        for filename, skill in commands.items():
            text = read(f"commands/{filename}")
            self.assertEqual(1, text.count(f"Delegate-To: `{skill}`"), filename)
            self.assertIn("인자를 그대로 전달", text, filename)
            for forbidden in ("git remote", "gh ", "glab ", "git commit", "git push"):
                self.assertNotIn(forbidden, text, filename)

    def test_git_skills_detect_github_and_gitlab_and_gate_writes(self):
        for name in ("write-issue", "post-git-comment", "write-pr"):
            text = read(f"skills/{name}/SKILL.md")
            for phrase in ("git remote get-url origin", "GitHub", "GitLab", "gh", "glab", "사용자 승인"):
                self.assertIn(phrase, text, name)
            self.assertIn("감지할 수 없", text, name)

    def test_commit_skill_preserves_atomic_and_supply_chain_checks(self):
        text = read("skills/commit-changes/SKILL.md")
        for phrase in (
            "스테이지된 파일",
            "커밋 계획",
            "사용자 승인",
            "72자",
            "package.json",
            "lockfile",
            "정확한 버전",
            "AI 서명",
            "본문(description)",
            "--signoff",
            "--author",
            "--trailer",
        ):
            self.assertIn(phrase, text)

    def test_issue_and_pr_resources_preserve_source_contracts(self):
        bug = read("skills/write-issue/assets/bug-issue-template.md")
        feature = read("skills/write-issue/assets/feature-issue-template.md")
        pr = read("skills/write-pr/assets/pr-template.md")
        rules = read("skills/write-pr/references/writing-pr-rules.md")
        for heading in ("Background", "Root Cause", "Verification", "Priority"):
            self.assertIn(f"## {heading}", bug)
        for heading in ("Background", "Goal", "Scope", "Tasks", "Priority", "Notes"):
            self.assertIn(f"## {heading}", feature)
        for heading in (
            "Summary",
            "How It Works",
            "Decisions",
            "Assumptions & Unverified",
            "Verification",
            "How To Validate",
            "Review Points",
            "Risk / Rollback",
        ):
            self.assertIn(f"## {heading}", pr)
        for phrase in ("진실성 우선", "코드의 지도", "file:line", "가정", "미검증", "Self-Check"):
            self.assertIn(phrase, rules)

    def test_git_skill_invocation_contracts_are_explicit(self):
        text = read("skills/orchestrate-work/references/invocation-contracts.md")
        for skill in ("commit-changes", "write-issue", "post-git-comment", "write-pr"):
            self.assertEqual(1, len(re.findall(rf"^## `{skill}`$", text, re.MULTILINE)))

    def test_reviewable_text_authoring_is_centralized_and_scoped(self):
        included = {
            "decision-first-grill": ("spec 작성", "spec 작성", "승인을 받는다"),
            "orchestrate-work": ("plan 작성", "plan 작성", "승인 게이트로 만들지는 않는다"),
            "write-issue": ("초안 작성", "승인과 생성", "승인 전에는 issue"),
            "post-git-comment": ("초안과 승인", "초안과 승인", "승인 전에는 코멘트"),
            "write-pr": ("작성과 provider 감지", "승인과 생성", "승인 전에는 push"),
            "understand-work": ("질문 작성", "질문 작성", "답변 뒤의 기술적 피드백"),
        }
        for name, (author_heading, boundary_heading, boundary_phrase) in included.items():
            text = read(f"skills/{name}/SKILL.md")
            self.assertEqual(1, text.count("author-reviewable-text"), name)
            authoring = section(text, author_heading)
            boundary = section(text, boundary_heading)
            self.assertEqual(1, authoring.count("author-reviewable-text"), name)
            self.assertIn("반환된", authoring, name)
            self.assertIn(boundary_phrase, boundary, name)
            self.assertLess(text.index("반환된", text.index("author-reviewable-text")), text.index(boundary_phrase), name)
            for phrase in ("산출물 종류", "확인된 사실", "필수 형식", "길이 제한", "반환된"):
                self.assertIn(phrase, authoring, name)

        for name in ("commit-changes", "implement-with-tdd"):
            self.assertNotIn("author-reviewable-text", read(f"skills/{name}/SKILL.md"), name)

        direct_voice_readers = {
            path.parent.name
            for path in (ROOT / "skills").glob("*/SKILL.md")
            if "voice-profile.md" in path.read_text(encoding="utf-8")
        }
        self.assertEqual(
            {"author-reviewable-text", "capture-authoring-voice"},
            direct_voice_readers,
        )

    def test_setup_is_interactive_and_never_overwrites_conflicts(self):
        text = read("skills/setup-orchestration/SKILL.md")
        for dependency in ("superpowers", "grill-with-docs", "domain-modeling"):
            self.assertIn(dependency, text)
        for phrase in ("항목별 승인", "사용자 범위", "directory junction", "symbolic link", "덮어쓰지"):
            self.assertIn(phrase, text)

    def test_setup_offers_optional_authoring_skills_without_blocking(self):
        text = read("skills/setup-orchestration/SKILL.md")
        for dependency in ("stop-slop", "humanizer"):
            self.assertIn(dependency, text)
        for command in (
            "npx skills add hardikpandya/stop-slop --global --skill stop-slop",
            "npx skills add blader/humanizer --global --skill humanizer",
        ):
            self.assertIn(command, text)
        for phrase in (
            "선택형",
            "둘 다 선택하지",
            "자동 업데이트하지 않는다",
            "작업을 차단하지 않는다",
            "다른 원본",
        ):
            self.assertIn(phrase, text)
        for path in (
            "skills/setup-orchestration/SKILL.md",
            "skills/author-reviewable-text/SKILL.md",
        ):
            self.assertNotIn("unslop", read(path), path)


class ConventionContractTests(unittest.TestCase):
    def test_registry_has_unique_ids_and_existing_files(self):
        registry = json.loads(read("conventions/registry.json"))
        ids = [pack["id"] for pack in registry["packs"]]
        self.assertEqual(len(ids), len(set(ids)))
        for pack in registry["packs"]:
            self.assertTrue((ROOT / "conventions" / pack["file"]).is_file())
        self.assertEqual(["project", "plugin", "default"], registry["priority"])

    def test_general_pack_preserves_boundary_test_and_delivery_rules(self):
        text = read("conventions/general.md")
        for phrase in (
            "추상화된 내부 인터페이스",
            "메시지 브로커",
            "통과하는 테스트",
            "핵심 행위를 mock",
            "getter",
            "도메인 용어",
            "CONTEXT.md",
            "UBIQUITOUS_LANGUAGE.md",
            "canonical term",
            "임의로 확정하지 말고",
            "일반화",
            "스크린샷",
        ):
            self.assertIn(phrase, text)

    def test_react_pack_distinguishes_user_facing_errors(self):
        text = read("conventions/react.md")
        self.assertIn("사용자에게 노출할 오류", text)
        self.assertIn("내부 진단용 오류", text)

    def test_pr_skill_loads_delivery_conventions(self):
        text = read("skills/write-pr/SKILL.md")
        self.assertIn("conventions/general.md", text)

    def test_migrated_root_convention_drafts_are_removed(self):
        for name in ("CLEAN_CODE.md", "CODE_CONVENTION.md", "REACT_CONVENTION.md"):
            self.assertFalse((ROOT / name).exists(), name)


class AcceptanceContractTests(unittest.TestCase):
    def test_cases_cover_cross_host_independent_entrypoints(self):
        cases = read("tests/acceptance/cases.md")
        expected = read("tests/acceptance/expected.md")
        for host in ("Codex", "Claude Code"):
            self.assertIn(host, cases)
        for skill in ("implement-with-tdd", "verify-test-sensitivity", "understand-work", "write-pr"):
            self.assertIn(skill, cases)
            self.assertIn(skill, expected)
        for command in ("git:commit", "git:issue", "git:comment", "git:pr"):
            self.assertIn(command, cases)
            self.assertIn(command, expected)


if __name__ == "__main__":
    unittest.main()
