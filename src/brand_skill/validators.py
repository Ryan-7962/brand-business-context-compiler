"""Validation helpers for phase-one Markdown outputs."""

from __future__ import annotations

from pathlib import Path

RISKY_PUBLIC_TERMS = [
    "无可竞品",
    "必赢",
    "碾压",
    "唯一",
    "第一",
    "竞品弱点",
    "攻击点",
]
INFO_STATUSES = [
    "已从来源资料提取",
    "AI 结构化转述，待确认",
    "AI 初步拟定，待品牌确认",
    "待补充",
    "不适用",
    "已品牌确认",
]


def _markdown_table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def check_claim_matrix(project_dir: Path) -> None:
    matrix = project_dir / "outputs" / "06_claim_matrix.md"
    if not matrix.exists():
        legacy_matrix = project_dir / "outputs" / "05_claim_matrix.md"
        if legacy_matrix.exists():
            matrix = legacy_matrix
    if not matrix.exists():
        print("Claim matrix not found: outputs/06_claim_matrix.md")
        raise SystemExit(1)
    text = matrix.read_text(encoding="utf-8")
    warnings = []
    required_headers = ["适用产品", "可外发表述", "支撑数据", "是否可用于全系列", "风险等级"]
    for header in required_headers:
        if header not in text:
            warnings.append(f"Missing expected header or field: {header}")
    rows = _markdown_table_rows(text)
    if len(rows) >= 2:
        header = rows[0]
        applicable_index = next(
            (index for index, name in enumerate(header) if "适用产品" in name or "SKU" in name or "香型" in name),
            None,
        )
        if applicable_index is None:
            warnings.append("Missing applicable product/SKU/fragrance column")
        else:
            for row_number, row in enumerate(rows[1:], start=1):
                value = row[applicable_index] if applicable_index < len(row) else ""
                if not value:
                    warnings.append(f"Claim row {row_number} missing applicable product/SKU/fragrance")
    elif "|" in text:
        warnings.append("Claim matrix table has no data rows")
    if warnings:
        print("Claim matrix warnings:")
        for warning in warnings:
            print(f"- {warning}")
        raise SystemExit(1)
    print("Claim matrix basic check passed.")


def check_brand_lock_sheet_draft(project_dir: Path) -> None:
    draft = project_dir / "outputs" / "02_brand_lock_sheet_draft.md"
    if not draft.exists():
        legacy_draft = project_dir / "outputs" / "01_brand_lock_sheet_draft.md"
        if legacy_draft.exists():
            draft = legacy_draft
    if not draft.exists():
        print("Brand Lock Sheet Draft not found: outputs/02_brand_lock_sheet_draft.md")
        raise SystemExit(1)
    text = draft.read_text(encoding="utf-8")
    warnings = []
    if "信息状态" not in text:
        warnings.append("Brand Lock Sheet Draft missing 信息状态")
    if not any(status in text for status in INFO_STATUSES):
        warnings.append("Brand Lock Sheet Draft missing recognized information status")
    if warnings:
        print("Brand Lock Sheet Draft warnings:")
        for warning in warnings:
            print(f"- {warning}")
        raise SystemExit(1)
    print("Brand Lock Sheet Draft basic check passed.")


def check_public_safe_text(text: str) -> list[str]:
    return [term for term in RISKY_PUBLIC_TERMS if term in text]
