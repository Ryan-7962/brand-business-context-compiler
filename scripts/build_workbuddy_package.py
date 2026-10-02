from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile


PACKAGE_DIRECTORY = "brand-business-context-compiler"
ARCHIVE_FILENAME = "brand-business-context-compiler-workbuddy.zip"
SKILL_PATH = Path("SKILL.md")
PROMPT_PATH = Path("prompts/10_compile_agent_neutral_wiki.md")
ONCE_PROMPT_PATH = Path("prompts/11_compile_once.md")
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
    ).replace(
        "prompts/11_compile_once.md",
        "references/compile_once.md",
    )
    packaged_prompt = (repo_root / PROMPT_PATH).read_text(encoding="utf-8").replace(
        "schemas/agent_neutral_wiki.schema.md",
        "references/agent_neutral_wiki.schema.md",
    )

    schema = (repo_root / SCHEMA_PATH).read_bytes()
    once_prompt = (repo_root / ONCE_PROMPT_PATH).read_bytes()
    guide = (repo_root / "docs/work_buddy_handoff_guide.md").read_bytes()
    archive = output_dir / ARCHIVE_FILENAME
    output_dir.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=output_dir, suffix=".zip", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as package:
            package.writestr(f"{PACKAGE_DIRECTORY}/SKILL.md", packaged_skill)
            package.writestr(f"{PACKAGE_DIRECTORY}/references/agent_neutral_wiki.schema.md", schema)
            package.writestr(f"{PACKAGE_DIRECTORY}/references/compile_agent_neutral_wiki.md", packaged_prompt)
            package.writestr(f"{PACKAGE_DIRECTORY}/references/compile_once.md", once_prompt)
        temporary.replace(archive)
    finally:
        temporary.unlink(missing_ok=True)
    (output_dir / "START_HERE_ZH.md").write_bytes(guide)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output_dir / "SHA256SUMS").write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    return archive


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    archive = build_workbuddy_package(repo_root, repo_root / "dist")
    print(archive)


if __name__ == "__main__":
    main()
