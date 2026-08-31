import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL_PATH = ROOT / "skills" / "review-comment" / "SKILL.md"


def read_skill() -> str:
    if not SKILL_PATH.is_file():
        raise AssertionError(f"skill file is missing: {SKILL_PATH}")
    return SKILL_PATH.read_text(encoding="utf-8")


class ReviewCommentSkillTests(unittest.TestCase):
    def test_skill_declares_session_target_and_explicit_invocation(self):
        text = read_skill()

        for phrase in (
            "review-comment",
            "사용자가 skill을 호출할 때만 실행",
            "PR/MR 링크",
            "현재 대화 세션",
            "다시 요구하지 않는다",
        ):
            self.assertIn(phrase, text)

        self.assertIn("백그라운드 polling으로 실행하지 않는다", text)

    def test_skill_prefers_connectors_and_never_installs_or_changes_auth(self):
        text = read_skill()

        connector = text.index("connector")
        github_cli = text.index("`gh`", connector)
        gitlab_cli = text.index("`glab`", github_cli)
        self.assertLess(connector, github_cli)
        self.assertLess(github_cli, gitlab_cli)

        for phrase in (
            "설치하지",
            "인증을 자동으로 변경하지 않는다",
            "인증·권한",
            "수행하지 않고",
        ):
            self.assertIn(phrase, text)

    def test_skill_handles_only_new_actionable_comments(self):
        text = read_skill()

        for phrase in (
            "새 unresolved 리뷰 코멘트",
            "사람이 작성한",
            "실행 가능한",
            "봇",
            "중복",
            "단순 질의",
            "파일·라인·본문",
        ):
            self.assertIn(phrase, text)

    def test_skill_commits_pushes_and_marks_successful_comments(self):
        text = read_skill()

        for phrase in (
            "자동 commit",
            "push",
            "이번 실행에서 변경된 파일만",
            "git add -A",
            "✅ 반영 완료",
            "commit SHA",
            "resolve",
            "실패하면 코멘트를 resolve하지",
        ):
            self.assertIn(phrase, text)

        self.assertRegex(text, r"GitHub.*review thread.*GitLab.*discussion", re.DOTALL)

    def test_skill_preserves_existing_git_command_scope(self):
        text = read_skill()

        for phrase in (
            "기존 `git:commit`",
            "기존 `git:pr`",
            "기존 `git:comment`",
            "기존 `git:issue`",
            "자동 설치",
            "자동 merge",
            "branch protection",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
