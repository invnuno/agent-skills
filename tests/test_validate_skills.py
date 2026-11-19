from __future__ import annotations

import importlib.util
from pathlib import Path
import stat
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPOSITORY_ROOT / "scripts" / "validate_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills", MODULE_PATH)
assert SPEC and SPEC.loader
validate_skills = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_skills
SPEC.loader.exec_module(validate_skills)


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.skill = self.root / "skills" / "sample-skill"
        self.skill.mkdir(parents=True)
        self.write_skill()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_skill(self, body: str = "# Sample\n\nFollow these instructions.\n", **metadata: str) -> None:
        values = {
            "name": "sample-skill",
            "description": "Use this sample skill for validator tests.",
            **metadata,
        }
        frontmatter = "\n".join(f"{key}: {value}" for key, value in values.items())
        (self.skill / "SKILL.md").write_text(
            f"---\n{frontmatter}\n---\n\n{body}",
            encoding="utf-8",
        )

    def rules(self) -> set[str]:
        return {item.rule for item in validate_skills.validate_repository(self.root)}

    def test_valid_multi_skill_repository(self) -> None:
        second = self.root / "skills" / "second-skill"
        second.mkdir()
        (second / "SKILL.md").write_text(
            "---\n"
            "name: second-skill\n"
            "description: Use this second skill when another test needs it.\n"
            "---\n\n# Second\n\nDo the work.\n",
            encoding="utf-8",
        )

        self.assertEqual(validate_skills.validate_repository(self.root), [])

    def test_invalid_name_and_frontmatter_are_reported(self) -> None:
        self.write_skill(name="Sample Skill", compatibility="unsupported")

        self.assertTrue({"skill.name", "skill.name-match", "skill.frontmatter-keys"} <= self.rules())

    def test_missing_local_reference_is_reported(self) -> None:
        self.write_skill(body="# Sample\n\nRead [details](references/missing.md).\n")

        self.assertIn("skill.resource", self.rules())

    def test_non_executable_helper_is_reported(self) -> None:
        scripts = self.skill / "scripts"
        scripts.mkdir()
        helper = scripts / "helper.sh"
        helper.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        helper.chmod(stat.S_IRUSR | stat.S_IWUSR)

        self.assertIn("script.executable", self.rules())

    def test_personal_path_is_reported(self) -> None:
        personal_path = "/".join(("", "home", "private-user", "project")) + "/"
        self.write_skill(body=f"# Sample\n\nNever publish `{personal_path}`.\n")

        self.assertIn("privacy.personal-path", self.rules())

    def test_private_address_is_reported(self) -> None:
        address = ".".join(("192", "168", "50", "20"))
        self.write_skill(body=f"# Sample\n\nConnect to `{address}`.\n")

        self.assertIn("privacy.private-ip", self.rules())

    def test_secret_is_reported_without_echoing_value(self) -> None:
        sample_value = "ghp_" + "A" * 24
        self.write_skill(body=f"# Sample\n\nToken: `{sample_value}`.\n")

        issues = validate_skills.validate_repository(self.root)
        self.assertIn("secret.github-token", {item.rule for item in issues})
        self.assertNotIn(sample_value, "\n".join(item.message for item in issues))

    def test_placeholder_credentials_are_allowed(self) -> None:
        self.write_skill(body="# Sample\n\nSet `API_KEY=<replace-me>`.\n")

        self.assertNotIn("secret.assignment", self.rules())

    def test_valid_openai_metadata_is_accepted(self) -> None:
        agents = self.skill / "agents"
        agents.mkdir()
        (agents / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: Sample Skill\n"
            "  short_description: Validate a portable sample skill\n"
            "  default_prompt: Use $sample-skill to validate this package.\n",
            encoding="utf-8",
        )

        self.assertEqual(validate_skills.validate_repository(self.root), [])


if __name__ == "__main__":
    unittest.main()
