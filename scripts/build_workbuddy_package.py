from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PACKAGE_DIRECTORY = "brand-business-context-compiler"
ARCHIVE_FILENAME = "brand-business-context-compiler-workbuddy.zip"
SKILL_PATH = Path("SKILL.md")
PROMPT_PATH = Path("prompts/10_compile_agent_neutral_wiki.md")
SCHEMA_PATH = Path("schemas/agent_neutral_wiki.schema.md")


def build_workbuddy_package(repo_root: Path, output_dir: Path) -> Path:
    """Build the minimal public Skill archive for WorkBuddy."""
    skill_text = (repo_root / SKILL_PATH).read_text(encoding="utf-8")
    packaged_skill = skill_text.replace(
        "prompts/10_compile_agent_neutral_wiki.md",
        "references/compile_agent_neutral_wiki.md",
    ).replace(
        "schemas/agent_neutral_wiki.schema.md",
        "references/agent_neutral_wiki.schema.md",
    )

    archive = output_dir / ARCHIVE_FILENAME
    output_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as package:
        package.writestr(f"{PACKAGE_DIRECTORY}/SKILL.md", packaged_skill)
        package.writestr(
            f"{PACKAGE_DIRECTORY}/references/agent_neutral_wiki.schema.md",
            (repo_root / SCHEMA_PATH).read_bytes(),
        )
        package.writestr(
            f"{PACKAGE_DIRECTORY}/references/compile_agent_neutral_wiki.md",
            (repo_root / PROMPT_PATH).read_bytes(),
        )
    return archive


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    archive = build_workbuddy_package(repo_root, repo_root / "dist")
    print(archive)


if __name__ == "__main__":
    main()
