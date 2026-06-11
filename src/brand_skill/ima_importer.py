"""Import IMA knowledge-base media into a private local source directory."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


DEFAULT_IMA_API_SCRIPT = Path("/Users/ryan/.codex/skills/ima-skill/ima_api.cjs")


def import_ima_media(
    project_dir: Path,
    *,
    media_id: str,
    title: str,
    knowledge_base: str = "",
    knowledge_path: str = "",
    api_script: Path = DEFAULT_IMA_API_SCRIPT,
    env: dict[str, str] | None = None,
) -> Path:
    _ensure_private_target(project_dir)
    if not media_id.strip():
        print("Missing required IMA media id.")
        raise SystemExit(1)
    if not title.strip():
        print("Missing required IMA media title.")
        raise SystemExit(1)

    media_info = _get_media_info(api_script, media_id, env=env)
    url_info = media_info.get("data", {}).get("url_info") or {}
    url = str(url_info.get("url", "")).strip()
    if not url:
        print("IMA media did not return a downloadable URL. Please use the IMA client to view/export it.")
        raise SystemExit(1)

    source_dir = project_dir / "source" / "ima_imports"
    source_dir.mkdir(parents=True, exist_ok=True)
    file_name = _safe_file_name(title)
    target_path = _dedupe_path(source_dir / file_name)
    _download_url(url, url_info.get("headers") or {}, target_path)

    _upsert_source_manifest(
        project_dir,
        {
            "path": str(target_path.relative_to(project_dir / "source")).replace(os.sep, "/"),
            "source_platform": "ima",
            "knowledge_base": knowledge_base,
            "knowledge_path": knowledge_path,
            "media_id": media_id,
            "imported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    print(f"Imported IMA media into private source: {target_path}")
    return target_path


def _ensure_private_target(project_dir: Path) -> None:
    normalized = project_dir.as_posix()
    if "_private_test_runs/" in f"{normalized}/" or normalized.startswith("_private_test_runs/"):
        return
    print("IMA imports may only be written under _private_test_runs/ to avoid committing real brand materials.")
    raise SystemExit(1)


def _get_media_info(api_script: Path, media_id: str, env: dict[str, str] | None = None) -> dict:
    if not api_script.exists():
        print(f"Missing IMA API script: {api_script}")
        raise SystemExit(1)
    request_env = os.environ.copy()
    if env:
        request_env.update(env)
    result = subprocess.run(
        ["node", str(api_script), "openapi/wiki/v1/get_media_info", json.dumps({"media_id": media_id})],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=request_env,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr.strip() or "IMA media info request failed.")
        raise SystemExit(1)
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print("IMA media info response was not valid JSON.")
        raise SystemExit(1) from exc
    if response.get("code") != 0:
        print(response.get("msg", "IMA media info request failed."))
        raise SystemExit(1)
    return response


def _download_url(url: str, headers: dict[str, str], target_path: Path) -> None:
    request = Request(url, headers={str(key): str(value) for key, value in headers.items()})
    try:
        with urlopen(request, timeout=120) as response:
            target_path.write_bytes(response.read())
    except OSError as exc:
        print(f"Failed to download IMA media: {exc}")
        raise SystemExit(1) from exc


def _safe_file_name(title: str) -> str:
    name = Path(title.strip()).name
    name = re.sub(r"[/:\\]+", "_", name)
    return name or "ima_media"


def _dedupe_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(1, 1000):
        candidate = path.with_name(f"{stem}_{index:03d}{suffix}")
        if not candidate.exists():
            return candidate
    print(f"Too many duplicate IMA imports for: {path.name}")
    raise SystemExit(1)


def _upsert_source_manifest(project_dir: Path, entry: dict[str, str]) -> None:
    manifest_path = project_dir / "source" / "source_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"sources": []}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"Invalid source manifest JSON: {manifest_path}")
            raise SystemExit(1) from exc
    sources = manifest.setdefault("sources", [])
    if not isinstance(sources, list):
        print("Invalid source manifest: `sources` must be a list.")
        raise SystemExit(1)
    sources[:] = [item for item in sources if not isinstance(item, dict) or item.get("path") != entry["path"]]
    sources.append(entry)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
