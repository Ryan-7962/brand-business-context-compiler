from pathlib import Path
import re
from zipfile import ZipFile

from scripts.build_workbuddy_package import build_workbuddy_package


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = "brand-business-context-compiler"
EXPECTED_FILES = [
    f"{PACKAGE_ROOT}/SKILL.md",
    f"{PACKAGE_ROOT}/references/agent_neutral_wiki.schema.md",
    f"{PACKAGE_ROOT}/references/compile_agent_neutral_wiki.md",
    f"{PACKAGE_ROOT}/references/compile_once.md",
]
FORBIDDEN_PATH_PARTS = (
    "examples",
    "docs",
    "src",
    "tests",
    "_private_test_runs",
    ".git",
)
FORBIDDEN_CONTENT = (
    "PRIVATE_TEST_BRAND",
    "WORKBUDDY_PRIVATE_TOKEN",
    "PRIVATE_TEST_ENV_VAR",
    "/Users/ryan/",
)


def test_workbuddy_package_contains_only_public_files(tmp_path: Path) -> None:
    archive = build_workbuddy_package(REPO_ROOT, tmp_path)

    with ZipFile(archive) as package:
        names = sorted(package.namelist())

    assert names == EXPECTED_FILES
    assert all(
        forbidden_part not in name
        for name in names
        for forbidden_part in FORBIDDEN_PATH_PARTS
    )


def test_workbuddy_package_rewrites_skill_references_to_packaged_files(tmp_path: Path) -> None:
    archive = build_workbuddy_package(REPO_ROOT, tmp_path)

    with ZipFile(archive) as package:
        skill_text = package.read(f"{PACKAGE_ROOT}/SKILL.md").decode("utf-8")
        names = set(package.namelist())

    assert "references/compile_agent_neutral_wiki.md" in skill_text
    assert "references/agent_neutral_wiki.schema.md" in skill_text
    assert f"{PACKAGE_ROOT}/references/compile_agent_neutral_wiki.md" in names
    assert f"{PACKAGE_ROOT}/references/agent_neutral_wiki.schema.md" in names
    assert "prompts/10_compile_agent_neutral_wiki.md" not in skill_text
    assert "schemas/agent_neutral_wiki.schema.md" not in skill_text


def test_workbuddy_package_rewrites_prompt_schema_reference_to_packaged_file(tmp_path: Path) -> None:
    archive = build_workbuddy_package(REPO_ROOT, tmp_path)

    with ZipFile(archive) as package:
        prompt_text = package.read(
            f"{PACKAGE_ROOT}/references/compile_agent_neutral_wiki.md"
        ).decode("utf-8")
        names = set(package.namelist())

    reference = re.search(r"`(references/agent_neutral_wiki\.schema\.md)`", prompt_text)
    assert reference is not None
    assert f"{PACKAGE_ROOT}/{reference.group(1)}" in names
    assert "schemas/agent_neutral_wiki.schema.md" not in prompt_text


def test_workbuddy_prompt_escalates_only_compilation_blockers(tmp_path: Path) -> None:
    archive = build_workbuddy_package(REPO_ROOT, tmp_path)

    with ZipFile(archive) as package:
        prompt_text = package.read(
            f"{PACKAGE_ROOT}/references/compile_agent_neutral_wiki.md"
        ).decode("utf-8")

    assert "does not block faithful Wiki compilation" in prompt_text
    assert "Do not add generic disclaimers" in prompt_text


def test_workbuddy_package_supports_standalone_conversion(tmp_path: Path) -> None:
    archive = build_workbuddy_package(REPO_ROOT, tmp_path)

    with ZipFile(archive) as package:
        skill = package.read(f"{PACKAGE_ROOT}/SKILL.md").decode("utf-8")
        prompt = package.read(f"{PACKAGE_ROOT}/references/compile_once.md").decode("utf-8")

    assert "Default to one-off conversion" in skill
    assert "references/compile_once.md" in skill
    assert "prompts/11_compile_once.md" not in skill
    assert "Do not create a Wiki" in prompt
    assert "compiled/<source-id>.md" in prompt
    assert "Do not replace the body with a summary" in prompt


def test_workbuddy_package_excludes_sensitive_content_and_absolute_paths(tmp_path: Path) -> None:
    archive = build_workbuddy_package(REPO_ROOT, tmp_path)

    with ZipFile(archive) as package:
        content = "\n".join(package.read(name).decode("utf-8") for name in package.namelist())

    assert all(forbidden_text not in content for forbidden_text in FORBIDDEN_CONTENT)
