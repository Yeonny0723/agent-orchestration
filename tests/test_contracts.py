import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


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
        primary = skill.index("$AGENT_ORCHESTRATION_HOME/voice-profile.md")
        fallback = skill.index("~/.agent-orchestration/voice-profile.md")
        self.assertLess(primary, fallback)
        for phrase in (
            "직접 확인",
            "정확한 skill 이름",
            "실패 원인",
            "호출자에게 보고",
            "작성을 차단하지 않는다",
        ):
            self.assertIn(phrase, skill)

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

    def test_voice_profile_is_shared_by_user_facing_skills(self):
        for name in ("orchestrate-work", "decision-first-grill", "implement-with-tdd", "understand-work", "write-pr"):
            text = read(f"skills/{name}/SKILL.md")
            self.assertIn("voice-profile.md", text, name)
            self.assertIn("차단", text, name)
        profile = read("templates/voice-profile.md")
        self.assertEqual(10, len(re.findall(r"^## [0-9]+\.", profile, re.MULTILINE)))

    def test_setup_is_interactive_and_never_overwrites_conflicts(self):
        text = read("skills/setup-orchestration/SKILL.md")
        for dependency in ("superpowers", "grill-with-docs", "domain-modeling"):
            self.assertIn(dependency, text)
        for phrase in ("항목별 승인", "사용자 범위", "directory junction", "symbolic link", "덮어쓰지"):
            self.assertIn(phrase, text)


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
