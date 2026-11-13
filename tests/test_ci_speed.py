# =============================================================================
# A.R.M.O.R. - tests/test_ci_speed.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The workflow template keeps the CI quick without taking a check away (the text of the files is read, nothing runs).

* a newer push to a branch cancels the run before it, and main and the tags are never cancelled;
* the slow steps (Gradle) wait for the answer of the changed-paths workflow and run on main, on tags and when the answer cannot be found;
* a job that holds a coverage floor or runs infrastructure (a real broker, containers) is pinned to an Ubuntu image, not to the moving label;
* every job has a time limit and every workflow a read-only token;
* the CHANGELOG files merge as a union."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "tools" / "ci.yml.template"
E2E = ROOT / "tools" / "e2e.yml.template"
WORKFLOWS = ROOT / ".github" / "workflows"
INFRA = re.compile(r"(mosquitto|systemd|systemctl|apparmor|docker|podman|gcov|lcov|coverage_threshold|cov-fail-under|npm run coverage)", re.I)
CANCEL_EXPRESSION = "${{ github.ref != 'refs/heads/main' && !startsWith(github.ref, 'refs/tags/') }}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def jobs(text: str) -> dict[str, str]:
    """The text of each job of a workflow, by its key."""
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"(?m)^  ([A-Za-z0-9_-]+):\n", body)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


class TemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = read(TEMPLATE)
        self.jobs = jobs(self.text)

    def test_only_branch_runs_are_cancelled(self) -> None:
        self.assertIn(f"cancel-in-progress: {CANCEL_EXPRESSION}", self.text)
        self.assertNotRegex(self.text, r"cancel-in-progress:\s*true")

    def test_the_slow_steps_follow_the_answer_of_the_changed_paths_workflow(self) -> None:
        changes = self.jobs["changes"]
        self.assertRegex(changes, r"uses: JuanenRac/ARMOR-DEVOPS/\.github/workflows/changed-paths\.yml@[0-9a-f]{40}\n")
        self.assertIn("label: full-ci", changes)
        baseline = self.jobs["baseline"]
        self.assertIn("needs: changes", baseline)
        self.assertIn("if: ${{ !cancelled() }}", baseline)   # a question that could not be answered must not skip the validation
        decide = baseline.split("id: slow", 1)[1].split("- name:", 1)[0]
        for forced in ('"refs/heads/main"', "refs/tags/", '"$MATCHED" != "false"'):
            self.assertIn(forced, decide)
        for step in re.split(r"(?m)^      - name: ", baseline)[1:]:
            if "gradlew" in step.split("\n", 1)[0] or "Java" in step.split("\n", 1)[0]:
                self.assertIn("steps.slow.outputs.run == 'true'", step, step.split("\n", 1)[0])
        build = baseline.split("Run this project's real build and test", 1)[1].split("- name:", 1)[0]
        self.assertIn("hashFiles('gradlew') == '' || steps.slow.outputs.run == 'true'", build)   # only a repository with a Gradle wrapper may skip it

    def test_the_documents_and_the_manifest_are_always_validated(self) -> None:
        baseline = self.jobs["baseline"]
        validate = baseline.split("Validate manifest, version, changelog and README parity", 1)[1].split("- name:", 1)[0]
        self.assertNotIn("if:", validate)
        self.assertNotIn("slow", validate)

    def test_jobs_with_a_floor_or_infrastructure_are_pinned(self) -> None:
        for name, body in {**self.jobs, **jobs(read(E2E))}.items():
            runs_on = re.search(r"(?m)^    runs-on: (\S+)", body)
            if runs_on and runs_on.group(1) == "ubuntu-latest":
                self.assertIsNone(INFRA.search(body), f"job {name} measures a floor or runs infrastructure on ubuntu-latest")
        self.assertIn("runs-on: ubuntu-24.04", self.jobs["baseline"])

    def test_every_job_has_a_time_limit_and_the_token_is_read_only(self) -> None:
        for name, body in self.jobs.items():
            if "\n    uses:" not in "\n" + body:
                self.assertRegex(body, r"(?m)^    timeout-minutes: \d+$", name)
        self.assertRegex(self.text, r"(?m)^permissions:\n  contents: read$")

    def test_the_end_to_end_workflow_cancels_only_branch_runs_too(self) -> None:
        self.assertIn(f"cancel-in-progress: {CANCEL_EXPRESSION}", read(E2E))

    def test_the_copy_this_repository_runs_is_the_template(self) -> None:
        self.assertEqual(read(WORKFLOWS / "ci.yml"), self.text)


class WorkflowsOfThisRepositoryTests(unittest.TestCase):
    def test_no_workflow_that_runs_on_main_cancels_it(self) -> None:
        for path in sorted(WORKFLOWS.glob("*.yml")):
            text = read(path)
            if re.search(r"(?m)^  push:", text) or re.search(r"(?m)^on:.*\bpush\b", text):
                self.assertNotRegex(text, r"cancel-in-progress:\s*true", path.name)

    def test_the_coverage_floor_runs_on_a_pinned_image(self) -> None:
        text = read(WORKFLOWS / "coverage-floor.yml")
        self.assertIn("runs-on: ubuntu-24.04", text)
        self.assertNotIn("ubuntu-latest", text)
        self.assertRegex(text, r"(?m)^    timeout-minutes: \d+$")

    def test_no_macos_job_starts_on_every_pull_request(self) -> None:
        for path in sorted(WORKFLOWS.glob("*.yml")):
            text = read(path)
            if "macos-" in text and re.search(r"(?m)^  pull_request:", text):
                self.assertRegex(text, r"github\.event_name", path.name)

    def test_the_changelog_files_merge_as_a_union(self) -> None:
        attributes = read(ROOT / ".gitattributes")
        for pattern in ("CHANGELOG.md", "CHANGELOG_*.md", "CHANGELOG.*.md"):
            self.assertIn(f"{pattern} merge=union", attributes)


if __name__ == "__main__":
    unittest.main()
