# Validation Rules｜Brand Marketing Context Compiler

## Default Phase-One Checks

- `scaffold-output` must create the generic Marketing semantic base files:
  - `02_document_profile.md`
  - `03_marketing_semantic_transcript.md`
  - `04_key_facts_and_claims.md`
  - `05_strategy_and_execution_map.md`
  - `06_risk_and_review_items.md`
  - `07_ai_ready_marketing_brief_base.md`
  - `08_review_pack.md`
  - `09_quality_check_report.md`
  - `10_context_asset_index.md`
- `build-prompt-pack` must include only phase-one Marketing semantic prompts.
- `build-prompt-pack` must not include derived brief prompts.
- Optional product-module prompts such as Claim Matrix or SKU Cards must not be included in the default bundle.
- `convert-source` must preserve source anchors, page screenshots, and conversion reports.

## Information Status

Recognized statuses:

- `已从来源资料提取`
- `AI 结构化转述，待确认`
- `AI 初步拟定，待品牌确认`
- `待补充`
- `不适用`
- `已品牌确认`

## Optional Product Module Checks

The following checks are retained only for product-training / PDP / packaging / claim-report documents:

- Brand Lock Sheet Draft must contain information status.
- Claim Matrix must contain applicable product / SKU / fragrance or other explicit scope.
- Public-safe text must not contain internal sensitive terms.

## Test Fixture Privacy Checks

Official repo examples and Skill release packages must not contain raw private test materials. If a real test PDF is used during development, it must stay outside official `examples/` or be rewritten as anonymous sample data.

Private test outputs can live under `_private_test_runs/` and should not be treated as product documentation.
